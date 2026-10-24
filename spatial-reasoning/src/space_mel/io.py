"""Loading 10x Visium samples downloaded from GEO.

GEO flattens Space Ranger's output folder into files named ``GSMxxxx_<sample>_<file>[.gz]``.
``squidpy.read.visium`` expects the original layout instead::

    <sample_dir>/
        filtered_feature_bc_matrix.h5      (or matrix.mtx.gz + barcodes.tsv.gz + features.tsv.gz)
        spatial/tissue_positions.csv
        spatial/scalefactors_json.json
        spatial/tissue_hires_image.png
        spatial/tissue_lowres_image.png

``assemble_visium`` rebuilds that layout (decompressing where needed) and ``load_visium`` reads it.
"""

import gzip
import shutil
from pathlib import Path

import squidpy as sq
from anndata import AnnData

SPATIAL_FILES = [
    "tissue_positions.csv",
    "scalefactors_json.json",
    "tissue_hires_image.png",
    "tissue_lowres_image.png",
]
MTX_FILES = ["matrix.mtx.gz", "barcodes.tsv.gz", "features.tsv.gz"]
H5_FILE = "filtered_feature_bc_matrix.h5"


def _find(files_dir: Path, prefix: str, name: str) -> Path | None:
    """Find ``<prefix>_<name>`` or ``<prefix>_<name>.gz`` in a GEO files folder."""
    for candidate in (f"{prefix}_{name}", f"{prefix}_{name}.gz"):
        if (files_dir / candidate).exists():
            return files_dir / candidate
    return None


def _copy(src: Path, dest: Path, decompress: bool) -> None:
    if dest.exists():
        return
    if decompress and src.suffix == ".gz":
        with gzip.open(src, "rb") as fin, open(dest, "wb") as fout:
            shutil.copyfileobj(fin, fout)
    else:
        shutil.copyfile(src, dest)


def assemble_visium(files_dir: str | Path, prefix: str, out_dir: str | Path) -> tuple[Path, str]:
    """Rebuild the Space Ranger folder layout for one GEO sample.

    Parameters
    ----------
    files_dir
        Folder with the extracted GEO files, e.g. ``data/raw/GSE316760/files``.
    prefix
        File name prefix of the sample, e.g. ``GSM9459774_mel2``.
    out_dir
        Folder to create, e.g. ``data/processed/visium/GSE316760_mel2``.

    Returns
    -------
    The sample folder and the ``counts_file`` name to pass to ``squidpy.read.visium``.
    Raw files are never modified; already assembled files are skipped.
    """
    files_dir, out_dir = Path(files_dir), Path(out_dir)
    (out_dir / "spatial").mkdir(parents=True, exist_ok=True)

    for name in SPATIAL_FILES:
        src = _find(files_dir, prefix, name)
        if src is None:
            raise FileNotFoundError(f"{prefix}_{name}[.gz] not found in {files_dir}")
        _copy(src, out_dir / "spatial" / name, decompress=True)

    h5 = _find(files_dir, prefix, H5_FILE)
    if h5 is not None:
        _copy(h5, out_dir / H5_FILE, decompress=True)
        return out_dir, H5_FILE

    # Matrix Market format: scanpy reads the gzipped files directly, so keep them compressed.
    for name in MTX_FILES:
        src = _find(files_dir, prefix, name)
        if src is None:
            raise FileNotFoundError(f"{prefix}_{name} not found in {files_dir}")
        _copy(src, out_dir / name, decompress=False)
    return out_dir, "matrix.mtx.gz"


def load_visium(
    files_dir: str | Path,
    prefix: str,
    out_dir: str | Path,
    library_id: str,
    in_tissue_only: bool = False,
) -> AnnData:
    """Assemble a GEO Visium sample (if needed) and load it with squidpy.

    Set ``in_tissue_only=True`` when the matrix also contains spots outside this sample's tissue, e.g. in
    GSE298774, where patients sharing a capture area each come with the whole-slide matrix and only their own
    ``tissue_positions.csv`` marks which spots are theirs (``in_tissue == 1``).
    """
    sample_dir, counts_file = assemble_visium(files_dir, prefix, out_dir)
    adata = sq.read.visium(sample_dir, counts_file=counts_file, library_id=library_id)
    adata.var_names_make_unique()
    if in_tissue_only:
        adata = adata[adata.obs["in_tissue"] == 1].copy()
    return adata


def read_series_matrix(path: str | Path) -> "pd.DataFrame":
    """Sample metadata from a GEO ``*_series_matrix.txt.gz`` file: one row per sample, one column per field.

    Repeated fields (e.g. several ``!Sample_data_processing`` lines) get numbered: ``data_processing_2``, ...
    """
    import csv

    import pandas as pd

    fields: dict[str, list[str]] = {}
    with gzip.open(path, "rt", encoding="utf-8") as h:
        for row in csv.reader(h, delimiter="\t"):
            if not row or not row[0].startswith("!Sample_"):
                continue
            key = row[0].removeprefix("!Sample_")
            name, i = key, 1
            while name in fields:
                i += 1
                name = f"{key}_{i}"
            fields[name] = row[1:]
    return pd.DataFrame(fields).set_index("title")


def load_visium_without_images(
    matrix_tar: str | Path,
    reference_positions: str | Path,
    out_dir: str | Path,
    library_id: str,
) -> AnnData:
    """Load a Visium count matrix that comes without spatial files (e.g. GSE221390) and recover spot positions.

    Every Visium slide of the same version uses the same barcode -> grid-position layout, so the
    ``tissue_positions.csv`` of another sample on the same slide version (``reference_positions``) tells us
    ``array_row`` / ``array_col`` for each barcode. There is no image, so ``obsm["spatial"]`` holds positions in
    **micrometres** computed from the grid (see ``space_mel.spatial.grid_to_um``), not pixels.
    """
    import tarfile

    import pandas as pd
    import scanpy as sc

    from space_mel.spatial import grid_to_um

    out_dir = Path(out_dir)
    if not (out_dir / "matrix.mtx.gz").exists():
        out_dir.mkdir(parents=True, exist_ok=True)
        with tarfile.open(matrix_tar) as tar:
            tar.extractall(out_dir, filter="data")
    adata = sc.read_10x_mtx(out_dir)
    adata.var_names_make_unique()

    ref = pd.read_csv(reference_positions, index_col=0)
    missing = adata.obs_names.difference(ref.index)
    if len(missing):
        raise ValueError(f"{len(missing)} barcodes not in the reference grid; is it the same slide version?")
    adata.obs[["array_row", "array_col"]] = ref.loc[adata.obs_names, ["array_row", "array_col"]].values
    adata.obsm["spatial"] = grid_to_um(adata.obs["array_row"], adata.obs["array_col"])
    adata.uns["spatial"] = {library_id: {"metadata": {"coordinates": "micrometres from the Visium grid, no image"}}}
    return adata

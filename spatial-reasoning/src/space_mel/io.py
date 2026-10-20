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


def load_visium(files_dir: str | Path, prefix: str, out_dir: str | Path, library_id: str) -> AnnData:
    """Assemble a GEO Visium sample (if needed) and load it with squidpy."""
    sample_dir, counts_file = assemble_visium(files_dir, prefix, out_dir)
    adata = sq.read.visium(sample_dir, counts_file=counts_file, library_id=library_id)
    adata.var_names_make_unique()
    return adata

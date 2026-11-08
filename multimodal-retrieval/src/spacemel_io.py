"""
spacemel_io.py - data loading and processing for GSE298774 (Kreuger et al., Cancer Res 2026).

This module holds ALL data processing used by the notebooks. The notebooks only call
these functions, show the results and save outputs. Nothing here draws figures
(that is in spacemel_plots.py).

Organisation
------------
1. Paths and constants (with the source of every constant)
2. File discovery (which GEO file belongs to which GSM / tissue section)
3. Readers (positions, scale factors, counts, images, GEO series matrix, paper tables)
4. Geometry (pixel <-> micrometre, full-resolution <-> image pixels)
5. Section loading (one AnnData per tissue section, in-tissue spots only)
6. QC metrics and normalisation (never in place on the raw counts)
7. Patch extraction (for the paired H&E-RNA dataset)

Vocabulary (see docs/glossary.md)
---------------------------------
GSM / capture area : one GEO sample = one Visium capture area (one sequencing library).
section            : one patient's tissue piece on a capture area (file token, e.g. "A24").
patient            : a person (Supplementary Table S1). Patient B38 has two sections
                     (B38ex, B38_2) on two different capture areas.
spot               : one 55 um Visium capture spot, identified by its barcode *within* a
                     capture area. The same barcode string exists on every capture area,
                     so the unique key is spot_uid = "<GSM>:<barcode>".
"""
from __future__ import annotations

import gzip
import io
import json
import os
import re
import tarfile
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.io
import scipy.sparse as sp
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

# =============================================================================
# 1. Paths and constants
# =============================================================================
REPO_ROOT = Path(__file__).resolve().parents[1]
GSE_ID = "GSE298774"
GEO_SERIES_URL = "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE298nnn/GSE298774"
RAW_TAR_URL = f"{GEO_SERIES_URL}/suppl/GSE298774_RAW.tar"
SERIES_MATRIX_URL = f"{GEO_SERIES_URL}/matrix/GSE298774_series_matrix.txt.gz"
SUPP_TABLES_FILENAME = "can-25-2934_supplementary_tables_suppst1.xlsx"


def get_paths() -> dict:
    """All input/output locations. Override the data folders with environment variables:
    SPACEMEL_DATA (default <repo>/data/GSE298774) and SPACEMEL_SUPP (default <repo>/data/supplementary).
    """
    data = Path(os.environ.get("SPACEMEL_DATA", REPO_ROOT / "data" / GSE_ID))
    supp = Path(os.environ.get("SPACEMEL_SUPP", REPO_ROOT / "data" / "supplementary"))
    paths = {
        "repo": REPO_ROOT,
        "data": data,                         # downloads (gitignored)
        "raw": data / "raw",                  # extracted GEO files, flat (gitignored)
        "processed": data / "processed",      # per-section .h5ad files (gitignored)
        "supp": supp,                         # paper supplementary files (gitignored)
        "supp_tables": supp / SUPP_TABLES_FILENAME,
        "manifests": REPO_ROOT / "manifests",  # small CSV outputs (committed)
        "figures": REPO_ROOT / "figures",      # figure outputs (committed)
    }
    return paths


def ensure_output_dirs(paths: dict) -> None:
    for k in ("data", "raw", "processed", "supp", "manifests", "figures"):
        Path(paths[k]).mkdir(parents=True, exist_ok=True)


# Physical Visium geometry (10x Genomics specification; spot diameter also stated in the paper, Methods).
SPOT_DIAMETER_UM = 55.0
SPOT_PITCH_UM = 100.0          # centre-to-centre distance between neighbouring spots

# Visium array sizes (10x specification): 6.5 mm capture area = 4,992 spots, 11 mm = 14,336 spots.
ARRAY_SIZE_BY_N_SPOTS = {4992: "6.5 mm", 14336: "11 mm"}

# QC thresholds. Source: Kreuger et al. 2026, Methods p. 4401:
# "Spots with more than 500 genes were retained, as well as spots with less than 30% mitochondrial counts."
QC_MIN_GENES_EXCLUSIVE = 500   # keep n_genes  > 500
QC_MAX_PCT_MT_EXCLUSIVE = 30.0  # keep pct_mt  < 30

# Sections excluded from this project, with the reason (recorded in manifests/skipped_samples.csv).
EXCLUDED_SECTIONS = {
    "A2": ("No barcodes.tsv file in GEO; its matrix has 13,916 columns that cannot be "
           "matched to spot barcodes. Decision (project): not used, no recovery attempted."),
}

# The 18 individuals shown on the x-axis of Supplementary Fig. S1C/S1D (read from the figure).
# B38ex is not among them; A2 is.
PAPER_S1C_SECTIONS = ["A16", "A17", "A2", "A21", "A22", "A23", "A24", "A34", "A7",
                      "B1", "B13", "B14", "B15", "B38.2", "B4", "B8", "D20", "D3"]

# GEO file tokens differ from labels used in GEO titles / the paper for one section.
FILE_TOKEN_TO_LABEL = {"B38_2": "B38.2"}


def section_label(section_id: str) -> str:
    """Label used in GEO titles and in the paper for a file token (B38_2 -> B38.2)."""
    return FILE_TOKEN_TO_LABEL.get(section_id, section_id)


def patient_of(section_id: str) -> str:
    """Patient ID (Supplementary Table S1 'Visium ID') for a section. B38ex and B38_2 -> B38."""
    return "B38" if section_id.startswith("B38") else section_id


# =============================================================================
# 2. File discovery
# =============================================================================
_KINDS = {
    "aligned_fiducials.jpg": "fiducials_image",
    "barcodes.tsv": "barcodes",
    "features.tsv": "features",
    "matrix.mtx": "matrix",
    "scalefactors_json.json": "scalefactors",
    "tissue_hires_image.png": "hires_image",
    "tissue_lowres_image.png": "lowres_image",
    "tissue_positions.csv": "positions",
}
_FILE_RE = re.compile(r"^(GSM\d+)_(.+?)_(" + "|".join(re.escape(k) for k in _KINDS) + r")(\.gz)?$")


def discover_files(raw_dir) -> pd.DataFrame:
    """List every GEO file in raw_dir and parse it into (gsm, section_id, kind, path).
    Files that do not follow the GEO naming pattern are returned with kind='unrecognised'."""
    rows = []
    for p in sorted(Path(raw_dir).iterdir()):
        if not p.is_file():
            continue
        m = _FILE_RE.match(p.name)
        if m:
            rows.append({"gsm": m.group(1), "section_id": m.group(2),
                         "kind": _KINDS[m.group(3)], "path": str(p)})
        else:
            rows.append({"gsm": None, "section_id": None, "kind": "unrecognised", "path": str(p)})
    return pd.DataFrame(rows)


def files_by_section(files: pd.DataFrame) -> dict:
    """{(gsm, section_id): {kind: path}} for recognised files."""
    out = {}
    for r in files[files.kind != "unrecognised"].itertuples():
        out.setdefault((r.gsm, r.section_id), {})[r.kind] = r.path
    return out


# =============================================================================
# 3. Readers
# =============================================================================
def _open_bytes(path) -> bytes:
    path = str(path)
    with (gzip.open(path, "rb") if path.endswith(".gz") else open(path, "rb")) as f:
        return f.read()


def load_positions(path) -> pd.DataFrame:
    """tissue_positions.csv -> DataFrame indexed by barcode with columns
    in_tissue, array_row, array_col, pxl_row_in_fullres, pxl_col_in_fullres."""
    txt = _open_bytes(path).decode()
    has_header = "barcode" in txt.splitlines()[0].lower()
    df = pd.read_csv(io.StringIO(txt), header=0 if has_header else None)
    df.columns = ["barcode", "in_tissue", "array_row", "array_col",
                  "pxl_row_in_fullres", "pxl_col_in_fullres"]
    df["barcode"] = df["barcode"].astype(str)
    return df.set_index("barcode")


def load_scalefactors(path) -> dict:
    return json.loads(_open_bytes(path))


def load_image(path) -> Image.Image:
    return Image.open(io.BytesIO(_open_bytes(path))).convert("RGB")


def load_counts(matrix_path, barcodes_path, features_path):
    """Read a 10x MTX triplet. Returns (X spots x genes CSR, barcodes, features DataFrame).
    The MTX file stores genes x barcodes; it is transposed here."""
    X = scipy.io.mmread(io.BytesIO(_open_bytes(matrix_path)))
    X = sp.csr_matrix(X).T.tocsr()
    barcodes = pd.read_csv(io.BytesIO(_open_bytes(barcodes_path)), header=None, sep="\t")[0].astype(str).values
    feats = pd.read_csv(io.BytesIO(_open_bytes(features_path)), header=None, sep="\t")
    feats = feats.iloc[:, :3]
    feats.columns = ["gene_id", "gene_symbol", "feature_type"][: feats.shape[1]]
    if X.shape != (len(barcodes), len(feats)):
        raise ValueError(f"Matrix shape {X.shape} does not match "
                         f"{len(barcodes)} barcodes x {len(feats)} features")
    return X, barcodes, feats


def parse_series_matrix(path) -> pd.DataFrame:
    """GEO series matrix -> one row per GSM with every !Sample_ field (repeated fields get _0, _1 ...)."""
    rows = {}
    for line in _open_bytes(path).decode(errors="ignore").splitlines():
        if line.startswith("!Sample_"):
            parts = [x.strip().strip('"') for x in line.split("\t")]
            rows.setdefault(parts[0][len("!Sample_"):], []).append(parts[1:])
    gsms = rows["geo_accession"][0]
    df = pd.DataFrame(index=pd.Index(gsms, name="gsm"))
    for key, lists in rows.items():
        for j, vals in enumerate(lists):
            df[key if len(lists) == 1 else f"{key}_{j}"] = vals
    return df


def patients_in_geo_title(title: str) -> list:
    """'Nevus and melanoma in a single slide of patient B14, B15 and B38.2' -> ['B14','B15','B38.2']."""
    m = re.search(r"patient\s+(.+)$", title)
    if not m:
        return []
    return [t.strip() for t in re.split(r",|\band\b", m.group(1)) if t.strip()]


def load_supp_table(path, table: str) -> pd.DataFrame:
    """Read one supplementary table from the paper's Excel file.
    table: 'S1', 'S3', 'S4' or 'S5'. Header row positions were checked in the file."""
    header_row = {"S1": 4, "S3": 1, "S4": 2, "S5": 4}[table]
    xl = pd.ExcelFile(path)
    sheet = next(s for s in xl.sheet_names if s.strip() == f"Supplementary Table {table}")
    return pd.read_excel(xl, sheet_name=sheet, header=header_row)


def extract_raw_tar(tar_path, raw_dir) -> int:
    """Extract GSE298774_RAW.tar (flat list of .gz files) into raw_dir. Existing files are kept.
    Returns the number of newly extracted files."""
    raw_dir = Path(raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    with tarfile.open(tar_path) as tf:
        for m in tf.getmembers():
            if not m.isfile():
                continue
            name = Path(m.name).name  # flatten, never write outside raw_dir
            out = raw_dir / name
            if out.exists() and out.stat().st_size == m.size:
                continue
            with tf.extractfile(m) as src, open(out, "wb") as dst:
                dst.write(src.read())
            n += 1
    return n


# =============================================================================
# 4. Geometry
# =============================================================================
def grid_um_per_px(positions: pd.DataFrame) -> tuple:
    """Micrometres per FULL-RESOLUTION pixel, measured from the spot grid.
    On the Visium hexagonal grid, spots (array_row, array_col) and (array_row, array_col + 2)
    are neighbours 100 um apart. Uses all array positions (in and out of tissue).
    Returns (um_per_px, n_neighbour_pairs, relative spread (IQR/median) of the pair distances)."""
    g = positions[["array_row", "array_col", "pxl_row_in_fullres", "pxl_col_in_fullres"]]
    right = g.assign(array_col=g["array_col"] - 2)
    pairs = g.merge(right, on=["array_row", "array_col"], suffixes=("_a", "_b"))
    d = np.hypot(pairs.pxl_row_in_fullres_a - pairs.pxl_row_in_fullres_b,
                 pairs.pxl_col_in_fullres_a - pairs.pxl_col_in_fullres_b)
    med = float(np.median(d))
    iqr = float(np.subtract(*np.percentile(d, [75, 25])))
    return SPOT_PITCH_UM / med, int(len(d)), iqr / med


IMAGE_SCALE_KEY = {
    "hires": "tissue_hires_scalef",
    "lowres": "tissue_lowres_scalef",
    "fiducials": "regist_target_img_scalef",
}
IMAGE_FILE_KIND = {"hires": "hires_image", "lowres": "lowres_image", "fiducials": "fiducials_image"}


def fullres_to_image(pxl_row, pxl_col, scalefactors: dict, image: str = "hires"):
    """Full-resolution pixel coordinates -> pixel coordinates of a distributed image.
    Returns (x, y) = (column, row) in that image. The hires/lowres relation is defined by
    Space Ranger; for 'fiducials' (aligned_fiducials.jpg) it is an assumption that
    notebook 03 tests visually."""
    s = scalefactors[IMAGE_SCALE_KEY[image]]
    return np.asarray(pxl_col, float) * s, np.asarray(pxl_row, float) * s


# =============================================================================
# 5. Section loading
# =============================================================================
def load_section(gsm: str, section_id: str, files: dict):
    """Build one AnnData for one tissue section with ONLY its in-tissue spots.

    Why: on shared capture areas the matrix covers the whole capture area; each section's
    tissue_positions file marks only that section's spots with in_tissue == 1.

    Returns (adata, report) where report counts what happened at each step."""
    import anndata as ad

    needed = ["positions", "scalefactors", "matrix", "barcodes", "features"]
    missing = [k for k in needed if k not in files]
    if missing:
        raise FileNotFoundError(f"{gsm} {section_id}: missing {missing}")

    pos = load_positions(files["positions"])
    sf = load_scalefactors(files["scalefactors"])
    um_px, n_pairs, spread = grid_um_per_px(pos)
    X, barcodes, feats = load_counts(files["matrix"], files["barcodes"], files["features"])

    in_tissue = pos.index[pos["in_tissue"] == 1]
    bc_index = pd.Index(barcodes)
    present = in_tissue[in_tissue.isin(bc_index)]
    rows = bc_index.get_indexer(present)

    obs = pos.loc[present].copy()
    obs.insert(0, "gsm", gsm)
    obs.insert(1, "section_id", section_id)
    obs.insert(2, "patient_id", patient_of(section_id))
    obs.insert(3, "barcode", obs.index.astype(str))
    obs["spot_uid"] = gsm + ":" + obs["barcode"]
    obs["x_um"] = obs["pxl_col_in_fullres"] * um_px
    obs["y_um"] = obs["pxl_row_in_fullres"] * um_px
    obs.index = obs["spot_uid"].values

    var = feats.copy()
    var.index = pd.Index(var["gene_symbol"].astype(str)) if "gene_symbol" in var else pd.Index(var["gene_id"])
    var.index.name = None   # h5ad cannot store an index named like a column with different (made-unique) values
    a = ad.AnnData(X=X[rows].astype(np.float32), obs=obs, var=var)
    a.var_names_make_unique()
    a.var.index.name = None
    a.layers["counts"] = a.X.copy()
    a.obsm["spatial"] = obs[["pxl_col_in_fullres", "pxl_row_in_fullres"]].to_numpy(float)
    a.obsm["spatial_um"] = obs[["x_um", "y_um"]].to_numpy(float)
    a.uns["section_meta"] = {
        "gsm": gsm, "section_id": section_id, "patient_id": patient_of(section_id),
        "um_per_fullres_px": um_px, "grid_pairs": n_pairs, "grid_rel_iqr": spread,
        "scalefactors": {k: float(v) for k, v in sf.items()},
        "files": {k: Path(v).name for k, v in files.items()},
    }
    report = {
        "gsm": gsm, "section_id": section_id,
        "matrix_barcodes": int(len(barcodes)), "n_genes_panel": int(len(feats)),
        "positions_rows": int(len(pos)), "in_tissue": int(len(in_tissue)),
        "in_tissue_missing_from_matrix": int(len(in_tissue) - len(present)),
        "spots_loaded": int(a.n_obs),
        "matrix_scope": "whole capture area" if len(barcodes) > len(in_tissue) else "this section only",
        "um_per_fullres_px": um_px,
    }
    return a, report


def processed_path(paths: dict, gsm: str, section_id: str) -> Path:
    return Path(paths["processed"]) / f"{gsm}_{section_id}.h5ad"


def read_processed(paths: dict, gsm: str, section_id: str):
    import anndata as ad
    return ad.read_h5ad(processed_path(paths, gsm, section_id))


# =============================================================================
# 6. QC metrics and normalisation
# =============================================================================
def add_qc_metrics(a) -> None:
    """Add total_counts, n_genes, pct_mt and qc_* flags to a.obs (computed from layers['counts']).
    Mitochondrial genes = gene symbols starting with 'MT-'."""
    C = a.layers["counts"]
    a.obs["total_counts"] = np.asarray(C.sum(axis=1)).ravel()
    a.obs["n_genes"] = np.asarray((C > 0).sum(axis=1)).ravel()
    mt = a.var_names.str.startswith("MT-")
    mt_counts = np.asarray(C[:, mt].sum(axis=1)).ravel()
    with np.errstate(invalid="ignore", divide="ignore"):
        a.obs["pct_mt"] = np.where(a.obs["total_counts"] > 0,
                                   100 * mt_counts / a.obs["total_counts"], np.nan)
    a.obs["qc_genes_ok"] = a.obs["n_genes"] > QC_MIN_GENES_EXCLUSIVE
    a.obs["qc_mt_ok"] = a.obs["pct_mt"] < QC_MAX_PCT_MT_EXCLUSIVE   # NaN (0 counts) -> False
    a.obs["qc_pass"] = a.obs["qc_genes_ok"] & a.obs["qc_mt_ok"]
    a.uns["n_mt_genes"] = int(mt.sum())


def lognormalised_copy(a, target_sum: float = 1e4):
    """Return a COPY with X = log1p(counts / total * target_sum). layers['counts'] is untouched.
    Note: the authors used Seurat SCTransform (SCT assay in their scripts), so values are not
    numerically comparable with theirs."""
    import scanpy as sc
    b = a.copy()
    b.X = b.layers["counts"].copy()
    sc.pp.normalize_total(b, target_sum=target_sum)
    sc.pp.log1p(b)
    return b


def gene_vector(a, gene: str, layer: str | None = None) -> np.ndarray:
    """Dense 1-D vector of one gene (from X or a layer)."""
    M = a.layers[layer] if layer else a.X
    col = M[:, a.var_names.get_loc(gene)]
    return np.asarray(col.toarray() if sp.issparse(col) else col).ravel()


def rescale_free(v: np.ndarray, q: float = 0.99) -> np.ndarray:
    """Rescale to 0-1 per section, capping at the q-quantile (mirrors the authors' plotting
    call MapMultipleFeatures(scale='free', max_cutoff=0.99) in DEGs_OnOff_Enrichment.md)."""
    v = np.asarray(v, float)
    top = np.quantile(v, q)
    if top <= 0:
        top = v.max()
    return np.zeros_like(v) if top <= 0 else np.clip(v / top, 0, 1)


# =============================================================================
# 7. Patch extraction
# =============================================================================
def odd_side_px(side_um: float, um_per_img_px: float) -> int:
    """Patch side in image pixels for a side length in micrometres, rounded to an odd number
    so that the spot centre falls on the centre pixel."""
    n = max(1, int(round(side_um / um_per_img_px)))
    return n if n % 2 == 1 else n + 1


def crop_centered(img: np.ndarray, x: float, y: float, side_px: int):
    """Square crop of side_px centred on image pixel (x=column, y=row).
    Returns None if the crop would leave the image (no padding is invented)."""
    cx, cy = int(round(x)), int(round(y))
    h = side_px // 2
    r0, r1, c0, c1 = cy - h, cy + h + 1, cx - h, cx + h + 1
    if r0 < 0 or c0 < 0 or r1 > img.shape[0] or c1 > img.shape[1]:
        return None
    return img[r0:r1, c0:c1].copy()


def select_spread_spots(xy_um: np.ndarray, n: int, min_dist_um: float, seed: int) -> np.ndarray:
    """Randomly pick up to n row indices whose pairwise distance is >= min_dist_um
    (so patches do not share pixels). Deterministic for a given seed."""
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(xy_um))
    chosen = []
    for i in order:
        if all(np.hypot(*(xy_um[i] - xy_um[j])) >= min_dist_um for j in chosen):
            chosen.append(i)
            if len(chosen) == n:
                break
    return np.array(chosen, dtype=int)


# =============================================================================
# 8. Convenience for notebooks 02-05
# =============================================================================
def usable_sections(paths: dict) -> list:
    """[(gsm, section_id), ...] marked used_in_this_project in manifests/tissue_sections.csv (notebook 01)."""
    ts = pd.read_csv(Path(paths["manifests"]) / "tissue_sections.csv")
    ts = ts[ts["used_in_this_project"]]
    return list(zip(ts["gsm"], ts["section_id"]))


def section_image(paths: dict, a, image: str = "hires"):
    """Image of a loaded section plus its spots in that image's pixel coordinates.
    Returns (img as uint8 array, x, y, um_per_image_px)."""
    meta = a.uns["section_meta"]
    img = np.asarray(load_image(Path(paths["raw"]) / meta["files"][IMAGE_FILE_KIND[image]]))
    s = float(meta["scalefactors"][IMAGE_SCALE_KEY[image]])
    x = a.obs["pxl_col_in_fullres"].to_numpy(float) * s
    y = a.obs["pxl_row_in_fullres"].to_numpy(float) * s
    return img, x, y, float(meta["um_per_fullres_px"]) / s

# Datasets

Public 10x Visium datasets from Slack `#data` (posted by Myles, 15/10/2026), downloaded 20/10/2026
from GEO with `scripts/download_data.ps1`. Each one is explored in `01_data_exploration/notebooks/0X_explore_<GSE>.ipynb`.

- Local copy (for analysis): `data/raw/<GSE>/files/` (gitignored). `data/raw/<GSE>/download/` keeps the
  original GEO archives so the script can verify and skip them. `data/raw/<GSE>/metadata/` has GEO's
  `*_series_matrix.txt.gz` (sample descriptions; read with `space_mel.io.read_series_matrix`).
- Backup copy: Google Drive `TECNUN 2026-27/Alumno_Interno/02_data/raw/<GSE>/` (extracted files only)

## The four studies

| GSE | Study | Usable samples | Protocol | Capture area | Genes | Notebook |
|---|---|---|---|---|---|---|
| GSE316760 | Primary cutaneous melanoma, tumour microenvironment | 2 (mel2, mel3) | Visium FFPE, Space Ranger 2.0.1 | 6.5 mm (4,992 spots) | 17,943 (probe set v1), no MT- genes | 01 |
| GSE300445 | Primary melanoma before adjuvant anti-PD1 ([PMID 42315253](https://pubmed.ncbi.nlm.nih.gov/42315253/)) | 4 patients (AdjIII-0019/0022/0113/0133) | CytAssist, Space Ranger 3.0.0 | 6.5 mm | 18,085 (probe set v2), 11 MT- genes | 02 |
| GSE298774 | Nevus → melanoma transition ([PMID 42258703](https://pubmed.ncbi.nlm.nih.gov/42258703/)) | 18 of 19 patients (A2 unusable) on 11 capture areas | CytAssist, Space Ranger 2.1.1 | mostly 11 mm (14,336 spots), some 6.5 mm | 37,082 (most) or 18,085 (A16, A21, A23) | 03 |
| GSE221390 | Skin cancer atlas: SCC, BCC, melanoma | 2 melanoma samples × 2 patients | Visium FFPE (V1 slide) | 6.5 mm | 17,943 (same panel as GSE316760), no MT- genes | 04 |

Not public yet (useful later): bioRxiv 2026.01.20.700607 and CORDIS project 101096667.

## Coordinates and units

All samples are Visium: 55 µm spots, **100 µm centre-to-centre** on a hexagonal grid (one `array_col` step = 50 µm,
one `array_row` step = 86.6 µm). `tissue_positions.csv` gives `pxl_row_in_fullres, pxl_col_in_fullres` in
**full-resolution image pixels**.

**Rule: convert pixels to µm with the grid, `um_per_px = 100 / median nearest-neighbour spot distance (px)`**
(`space_mel.spatial.add_spatial_um`, which stores `obsm["spatial_um"]`).

Do **not** rely on `scalefactors_json.json`'s `spot_diameter_fullres`. Space Ranger does not define it consistently:

| Dataset | `65 / spot_diameter_fullres` vs grid |
|---|---|
| GSE316760 (Space Ranger 2.0.1) | agrees (0.346 µm/px). Using the physical 55 µm would be 15% wrong |
| GSE300445 (3.0.0, CytAssist) | **exactly 7.14% too small** in every sample (it corresponds to a 70 µm spot) |
| GSE298774 (2.1.1, CytAssist) | **−7.1% on 6.5 mm areas, +7.6 to +7.9% on 11 mm areas** |

A full fit of the grid → pixel transformation confirmed the grid method within 0.5% on every sample checked.
The pixel size differs per sample (0.23–0.39 µm/px), so always convert before comparing distances.

## Known quirks

- **GEO flattens the 10x folder layout.** Files are renamed `GSMxxx_<sample>_<file>.gz`. `space_mel.io.load_visium`
  rebuilds the Space Ranger layout so `squidpy.read.visium` can read it.
- **GSE300445:** files carry an extra `_processed` in the prefix. GEO's sample list says "ADJIII-0013" but that
  sample's files (GSM9060734) are named "AdjIII-0113" (GEO typo). No response-to-therapy labels on GEO.
- **GSE298774: patients share capture areas.** One GEO sample = one capture area with 1–3 patients. Each patient's
  `tissue_positions.csv` lists all spots of the area and marks its own with `in_tissue == 1` (never overlapping).
  For A17, A22/A24, A34, A7, B1/B38ex, B4, B8/B13, B14/B15/B38_2, D3/D20 the matrix covers the whole area, so load with
  `load_visium(..., in_tissue_only=True)`. A16, A21, A23 come already split.
- **GSE298774 A2 is unusable:** no `barcodes.tsv.gz`, and its matrix (13,916 columns) does not match A17's barcodes
  (13,887), so its columns cannot be assigned to spots. Ask Myles / the authors.
- **GSE298774 is NOT filtered**, although GEO says spots with ≤ 500 genes or ≥ 30% mitochondrial counts were removed
  with *semla*: the files contain spots with 0 counts and up to 54% MT. Quality varies enormously between patients
  (median counts per spot from ~130 in B8 to ~22,000 in D20); B8, B14, B15, A17, A34 and A7 are very shallow.
  Apply our own QC filter before spatial analyses.
- **GSE221390 has no images or positions on GEO** (only `filtered_feature_bc_matrix.tar.gz`). Positions are
  recovered from the barcodes: every Visium V1 slide maps barcodes to the same grid positions, and all its barcodes
  are in GSE316760's `tissue_positions.csv` (`space_mel.io.load_visium_without_images`). Coordinates are then in µm
  from the grid, with **unknown orientation** (possibly mirrored/rotated vs the real tissue). Each sample holds two
  patients, which separate cleanly into two tissue pieces; which piece is which patient ID is unknown. GEO also
  spells one patient both "6474" (sample title) and "6747" (protocol). The sections are mostly normal skin with
  little tumour.
- **Three gene panels:** 17,943 (v1), 18,085 (v2) and 37,082 genes. Use the shared genes when combining datasets.
- **No annotations shipped:** none of the GEO files label regions (tumour / nevus / immune / stroma).
  These must come from the papers' supplements or be derived by us (marker genes such as PRAME, clustering).

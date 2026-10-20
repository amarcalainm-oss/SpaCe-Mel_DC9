# Datasets

Public 10x Visium datasets from Slack `#data` (posted by Myles, 15/10/2026), downloaded 20/10/2026
from GEO with `scripts/download_data.ps1`.

- Local copy (for analysis): `data/raw/<GSE>/files/` (gitignored). `data/raw/<GSE>/download/` keeps the
  original GEO archives so the script can verify and skip them.
- Backup copy: Google Drive `TECNUN 2026-27/Alumno_Interno/02_data/raw/<GSE>/` (extracted files only)

## The four studies

| GSE | Study | Samples | Slide size | Genes | Format |
|---|---|---|---|---|---|
| GSE316760 | Primary cutaneous melanoma, tumour microenvironment | 2 (mel2: 4,084 spots, mel3: 4,949) | 6.5 mm (4,992 spots) | 17,943 (probe-based, Space Ranger 2.0.1; no MT- genes) | Standard Space Ranger `.h5`, easiest to load |
| GSE300445 | Primary melanoma before adjuvant anti-PD1 ([PMID 42315253](https://pubmed.ncbi.nlm.nih.gov/42315253/)) | 4 patients (ADJIII-0019/0022/0113/0133) | 6.5 mm | 18,085 | `.mtx`, already filtered to tissue spots |
| GSE298774 | Nevus → melanoma transition, + imaging mass cytometry ([PMID 42258703](https://pubmed.ncbi.nlm.nih.gov/42258703/)) | 11 slides, ~20 lesions (A*, B*, D*) | mostly 11 mm (14,336 spots), some 6.5 mm | 37,082 (most) or 18,085 (A16, A21, A23) | `.mtx` |
| GSE221390 | Skin cancer atlas: SCC, BCC, melanoma (+ scRNA-seq of SCC/BCC) | 2 melanoma Visium slides (patients 66487+48974, 6474+21031) | ? | ? | **Matrices only (`.tar.gz` with mtx/barcodes/features): no coordinates or images on GEO, so not usable for spatial analysis as is.** Ask Myles whether the spatial files exist elsewhere. |

Not public yet (useful later): bioRxiv 2026.01.20.700607 and CORDIS project 101096667.

## Coordinates and units

All samples are Visium: 55 µm spots, 100 µm centre-to-centre on a hexagonal grid.
`tissue_positions.csv` gives `pxl_row_in_fullres, pxl_col_in_fullres` in **full-resolution image pixels**.
To convert to micrometres: `um_per_px = 65 / spot_diameter_fullres` (from `scalefactors_json.json`).
Careful: Space Ranger defines `spot_diameter_fullres` as a theoretical **65 µm** spot, not the physical 55 µm.
Verified on GSE316760: neighbouring spots are 289 px apart and `spot_diameter_fullres` = 188 px, so
65/188 × 289 = 100 µm (using 55 would give a wrong 84.6 µm). A robust alternative is
`um_per_px = 100 / median nearest-neighbour spot distance`.
The pixel size differs per sample (`spot_diameter_fullres` ranges 155–318 px), so always convert before
comparing distances across samples.

## Known quirks (check during exploration)

- **GEO flattens the 10x folder layout.** Files are renamed `GSMxxx_<sample>_<file>.gz`. Squidpy's
  `sq.read.visium()` expects the original Space Ranger layout, so each sample has to be reassembled
  (or loaded manually) before it becomes an AnnData object.
- **GSE298774: several lesions share one slide.** Pairs such as A2/A17, A22/A24, B1/B38ex, B8/B13, D3/D20
  and B14/B15/B38_2 have identical scalefactors and matrices with identical numbers of non-zero entries,
  so the matrix covers the whole slide. The lesions are separated by the `in_tissue` column of each
  sample's `tissue_positions.csv`.
- **GSE298774: many matrices include off-tissue spots** (e.g. A22: 14,336 spots, 4,326 in tissue). Filter
  on `in_tissue == 1`.
- **GSE298774 A2 has no `barcodes.tsv.gz`**, and its features file is a separate download
  (`GSE298774_A2_features.tsv.gz`). Its barcodes may have to be recovered from the paired slide (A17).
- **Two gene panels:** 37,082 vs 18,085 genes (different 10x chemistry/reference). Use the shared genes
  when combining samples.
- **No annotations shipped:** none of the GEO files label regions (tumour / nevus / immune / stroma).
  These must come from the papers' supplements or be derived by us (marker genes, clustering).

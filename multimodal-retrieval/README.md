# Multimodal Tissue-Region Retrieval (SPACE-MEL DC9 — Student 2)

**Dataset:** [GEO GSE298774](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE298774).

**Reference:** Kreuger IZM et al., *Cancer Res* 2026;86:4400–13, doi:10.1158/0008-5472.CAN-25-2934.

**Authors' code:** <https://github.com/roderickslieker/NevusMelanomaVisium>.

## Project

**Provisional title:** Evaluating Histology–Transcriptomics Fusion for Interpretable Melanoma Tissue Region Retrieval

**Research question:** Does integrating transcriptomic information with histological features improve the
identification and retrieval of biologically meaningful melanoma tissue regions?

**Primary contribution:** Interpretable, lightweight multimodal embeddings, and a rigorous evaluation of whether H&E
and spatial gene expression give *complementary* descriptions of nevus/melanoma tissue regions, especially across
patients.

> A new fusion architecture is optional. Rigorous, leakage-free evaluation is the point.

### Questions addressed

| ID | Question | Planned output |
|----|----------|----------------|
| **M1** | How do RNA and histological image embeddings compare? | RNA-only vs image-only embedding plots, patient/slide effects, retrieval examples and failure cases |
| **M2** | Does multimodal fusion improve tissue-region retrieval? | Precision@k, Recall@k, mAP for RNA-only, image-only, concatenation and one stronger fusion baseline (same queries, gallery and tuning budget) |
| **M3** | Does retrieval work for unseen patients? | Cross-patient metrics with patient-level confidence intervals; failure analysis linked to tissue heterogeneity |
| **M4** | Which tissue regions benefit most from fusion? | Region-stratified gain/loss (nevus, melanoma, other compartments), hard positive/negative examples |
| **M5** | Which design choices drive performance? | Ablation table (patch size, RNA preprocessing/dimensionality, fusion strategy, normalization), stain robustness, recommended parsimonious baseline |

Core hypothesis: histology and transcriptomics capture partly non-overlapping information about tissue state, so a
simple fusion of the two retrieves biologically similar regions better than either alone, and the gain is
region-dependent.

**Current stage.** The work in this folder is data preparation only: dataset audit, replication of published results,
and a verified set of paired H&E patches and spot RNA profiles. M1–M5 have not been started. They begin once the
pairing and evaluation assumptions are verified (see [`STATUS.md`](STATUS.md)).


## What this folder contains

GSE298774 contains 11 Visium capture areas holding 19 tissue sections from 18 patients. Each lesion has a benign
nevus part next to a melanoma part. This folder:

1. builds a traceable manifest at three levels (capture area → patient/section → spot);
2. applies the paper's spot QC;
3. checks that spots and H&E images line up;
4. maps CDK2 and immune-associated genes and compares them with the exact published numbers;
5. prepares a small, verified set of H&E patches paired with the RNA of the same spot.

No model is trained and no biological similarity is claimed. Current results are in [`STATUS.md`](STATUS.md);
terms are explained in [`docs/glossary.md`](docs/glossary.md).

## Layout

```
multimodal-retrieval/
├── README.md               this file: what is here and how to run it
├── STATUS.md               what is done, results, open questions
├── environment.yml         software versions (see "Software" below)
├── src/
│   ├── spacemel_io.py      all data processing (loading, coordinates, QC, normalisation, patches)
│   └── spacemel_plots.py   all drawing (spots at true 55 µm size on the H&E)
├── notebooks/              run the code, show results, save outputs; every step explained
│   ├── 00_setup_and_download.ipynb
│   ├── 01_inventory_and_manifest.ipynb
│   ├── 02_qc.ipynb
│   ├── 03_registration_overlay.ipynb       R1
│   ├── 04_replication_CDK2_immune.ipynb    R2, R3
│   └── 05_paired_HE_RNA_dataset.ipynb      paired H&E patch – spot RNA
├── manifests/              small CSV outputs (column descriptions in manifests/README.md)
├── figures/                PNG outputs, one subfolder per notebook
├── docs/                   written documentation (see below)
├── archive/                the original Part I worksheet and first version of the Part II notebook (superseded, kept for the record)
└── data/                   NOT committed: GEO download, extracted files, processed .h5ad, supplementary files
```

**Separation of concerns:** data processing is in `src/spacemel_io.py` and drawing in `src/spacemel_plots.py`;
the only processing written directly in a notebook is the download and file inventory in notebook 00. The notebooks
call these modules, show the outputs and save them. Outputs go only to `manifests/` and `figures/`; large data stay
in `data/`.

**`docs/`** holds text documents that are not code and not outputs:

| File | Content |
|---|---|
| `part_I_worksheet.md` | Part I: answers to the reference-paper worksheet and the novelty audit |
| `data_facts.md` | facts taken from the paper, supplementary material, GEO and the authors' code, each with its source |
| `annotation_caveats.md` | which labels exist and which do not; evidence levels for immune statements |
| `glossary.md` | plain-language definitions of the terms used (Visium, spot, barcode, H&E, QC, …) |

## Software

```bash
conda env create -f environment.yml
conda activate spacemel
python -m ipykernel install --user --name spacemel
```

The results in this repository were produced with **Python 3.14.7** and the package versions recorded in
`manifests/environment_versions.csv` (notebook 00), which are newer than those pinned in `environment.yml`.
Packages used: numpy, pandas, scipy, anndata, scanpy, matplotlib, pillow, h5py, openpyxl.

## Input data

| Input | Where to get it | Where to put it |
|---|---|---|
| `GSE298774_RAW.tar` (≈ 1.4 GB) and the series matrix | downloaded by notebook 00, or manually from the GEO page | `data/GSE298774/` (or any folder listed in notebook 00, cell 0.2) |
| `can-25-2934_supplementary_tables_suppst1.xlsx` | article page → Supplementary Data | `data/supplementary/` |

Other locations can be used by setting the environment variables `SPACEMEL_DATA` and `SPACEMEL_SUPP` before starting
Jupyter. No user-specific path is hard-coded. The supplementary Excel file is not downloaded by notebook 00; without it notebook 01 omits the clinical columns and notebook 04 stops at 4.2.

## Run order

Run the notebooks in order, each from a fresh kernel (*Restart* → *Run All*). Each reads only files written by
earlier ones.

| # | Notebook | Task | Produces |
|---|---|---|---|
| 00 | setup and download | 2 | data on disk, software versions, file inventory, file-presence figure |
| 01 | inventory and manifest | 1 | capture-area / section / spot manifests, skipped samples, reconciliation with spatial-reasoning, processed `.h5ad` |
| 02 | QC | 1, 2 | QC flags in the spot manifest, QC summary, QC figures |
| 03 | registration overlay | 3 (R1) | overlay figures, aligned_fiducials test, comparison with published figures |
| 04 | replication CDK2 + immune | 3 (R2, R3), 4 | gene maps, detection tables, evidence levels, replication record |
| 05 | paired H&E–RNA dataset | 5 | paired-spot table, patches, RNA matrices, pairing checks, montage |

Notebook 05 processes the sections listed in `SECTIONS` (cell 5.1); the current run uses B1 and A24.

## Decisions recorded in the code

| Decision | Where |
|---|---|
| A2 is not used: GEO has no barcodes file for it; no recovery attempted | `EXCLUDED_SECTIONS` in `spacemel_io.py`; `manifests/skipped_samples.csv` |
| Patients from Supplementary Table S1; B38ex and B38_2 are one patient (B38) | `patient_of()` in `spacemel_io.py`; `manifests/tissue_sections.csv` |
| Spot key `spot_uid = <GSM>:<barcode>` (barcodes repeat across capture areas) | notebook 01 |
| No nevus/melanoma label per spot (`region_label = "not available"`) | notebook 01; `docs/annotation_caveats.md` |
| QC = `n_genes > 500` and `pct_mt < 30` (paper, Methods); spots flagged, not deleted | `QC_*` constants; notebook 02 |
| µm per pixel from the spot grid (100 µm pitch), not from `spot_diameter_fullres` | `grid_um_per_px()`; notebook 01 |
| H&E patches cut from the hires image; aligned_fiducials.jpg is not used (does not align with the given scale factor) | notebook 03 (3.3); notebook 05 `IMAGE_SOURCE` |
| Normalisation on a copy: counts / spot total × 10,000, then log(1 + x) | `lognormalised_copy()`; notebooks 04, 05 |

## Not committed

Raw GEO files, processed `.h5ad` files, the GEO archive and full expression matrices. RNA is committed only for the paired spots (40 per section, `manifests/paired_spots/`).

## References

 - Kreuger IZM et al. (2026). *Cancer Research* 86:4400–4413. https://doi.org/10.1158/0008-5472.CAN-25-2934
 - GEO GSE298774: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE298774
 - Author code: https://github.com/roderickslieker/NevusMelanomaVisium
 - IMC data: https://zenodo.org/records/15582615
 - SPACE-MEL: https://space-mel.eu/
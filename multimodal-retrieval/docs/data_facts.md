# Established facts about GSE298774 and the reference paper

Everything below was read from a named source before any analysis in this folder. Facts that the notebooks
re-measure are marked *(re-checked in notebook NN)*. Nothing here is a result of our analysis.

## Study design (paper)
Kreuger IZM et al. *Spatial Analysis Reveals Gene Expression and Microenvironmental Changes in the Transition of Nevus
to Melanoma.* Cancer Res 2026;86:4400–13. doi:10.1158/0008-5472.CAN-25-2934.

| Fact | Source |
|---|---|
| 18 lesions from different patients, each with a contiguous nevus and melanoma | Results, p. 4403 |
| FFPE, 5 µm sections, Visium CytAssist; Space Ranger v2.1.1 with probe set GRCh38-2020-A; H&E scanned on a Zeiss Axio Scan Z1 | Methods, p. 4401 |
| Spots 55 µm, 5–10 cells per spot | Methods, p. 4401 |
| QC: "Spots with more than 500 genes were retained, as well as spots with less than 30% mitochondrial counts" (R package semla) | Methods, p. 4401 |
| Final data: 18,072 features and 39,481 spots | Methods (deconvolution), Results p. 4403 |
| Spot labels = most abundant of 15 STdeconvolve profiles (Nevus, Melanoma 1, Melanoma 2, Immune cells 1/2, ...) | Methods; Results p. 4403; Fig. 1F–G |
| DEGs use spots where Melanoma 1 (12 lesions) or Nevus (17 lesions) is most abundant | Results p. 4403 |
| Immune composition: semla RunNNLS with a single-cell reference (Franken et al.); IMC on 9 lesions | Methods p. 4402; Results p. 4409 |
| Authors' normalisation for DE: Seurat SCT assay | authors' code, `RandomEffectsModel.md` |
| IMC data: Zenodo doi:10.5281/zenodo.15582615; code: github.com/roderickslieker/NevusMelanomaVisium | Data Availability |

## Patients and sections (Supplementary Table S1, Supp. Fig. S1C, GEO)
| Fact | Source |
|---|---|
| Table S1 lists 18 patients; column "Visium ID" (A2, A7, A16, A17, A21, A22, A23, A24, A34, B1, B4, B8, B13, B14, B15, B38, D3, D20) | Supplementary Table S1 |
| GEO has 11 GSMs = 11 capture areas, with 19 section tokens; B38 appears as B38ex (GSM9022969) and B38_2 (GSM9022972) | GEO titles and file names |
| The 18 individuals on the x-axis of Supp. Fig. S1C include A2 and B38.2, not B38ex | Supplementary Fig. S1C |
| The authors' code excludes B38ex in one analysis | `DEGsPathwaysTsoi_PseudoTimesAllSamples.md`, line 81 |
| A2 has no `barcodes.tsv` in GEO; its matrix has 13,916 columns | inventory *(re-checked in notebook 00)* |
| On shared capture areas each section's `tissue_positions.csv` lists all array spots and marks its own with `in_tissue == 1`; most matrices cover the whole array | colleague's notes (`spatial-reasoning/docs/datasets.md`); inventory *(confirmed in notebook 01: 0 shared barcodes, 0 in-tissue spots missing from matrices)* |

## Files and images (inventory of the GEO archive)
| Fact | Source |
|---|---|
| Per section: `aligned_fiducials.jpg`, `barcodes.tsv`, `features.tsv`, `matrix.mtx`, `scalefactors_json.json`, `tissue_hires_image.png`, `tissue_lowres_image.png`, `tissue_positions.csv` (all `.gz`) | inventory |
| No full-resolution H&E image is distributed | inventory |
| hires images ~2000 px; µm per hires pixel 5.1–11.8 (one 55 µm spot = 4.7–10.7 px) | inventory summary *(re-checked in notebook 01)* |
| `aligned_fiducials.jpg` is a 3000 × 3000 px greyscale image of the capture area with the fiducial frame; spot coordinates scaled with `regist_target_img_scalef` alone do not fall on its tissue (0–63.8 % of spots inside the image) | notebook 03, 3.3 |

## Published numbers used as replication targets
| Gene | Table S4 avg_log2FC | Table S4 detected in Melanoma 1 / Nevus spots | Table S5 % spots, ≥75 % purity, Melanoma 1 / Nevus |
|---|---|---|---|
| CDK2 | 3.86 | 0.928 / 0.200 | 99.8 / 10.7 |
| PRAME | 2.73 | 0.958 / 0.251 | 100 / 13.8 |
| SNX10 | 2.17 | 0.954 / 0.303 | 98.3 / 19.7 |
| HHATL | −8.60 | 0.010 / 0.596 | 0.12 / 75.5 |

Table S5 also reports percentages over all labelled spots (CDK2: 84.4 % Melanoma 1, 24.9 % Nevus), which differ from
the Table S4 fractions; the tables do not explain the difference. Notebook 04 reads these values from the Excel file.

## What is not available
- Per-spot nevus / melanoma / cell-type labels (authors' deconvolution output; not in GEO or the repository).
- Full-resolution H&E images.
- The crop boxes used for published figures (`CropSections.xlsx`, not in the repository).
- Which patient is shown in Fig. 1B–G, Supp. Fig. S1E and Supp. Fig. S4 (legends give no IDs).

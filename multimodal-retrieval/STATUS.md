# Status

*Last updated: 8 November 2026. Every result below comes from the executed notebooks; the notebook and section are
given for each.*

## This week's tasks

| # | Task | Status | Where |
|---|---|---|---|
| 1 | Corrected manifest: capture area / patient / spot separated; no labels from GEO wording; reconciled with spatial-reasoning | ✅ done | notebook 01; `manifests/capture_areas.csv`, `tissue_sections.csv`, `spots.csv.gz`, `reconciliation_spatial_reasoning.csv` |
| 2 | Notebook run end to end; hard-coded path removed; packages and inputs documented; skipped samples recorded | ✅ done | notebooks 00–05; `README.md`; `manifests/skipped_samples.csv` |
| 3 | Replication R1 (overlay), R2 (CDK2), R3 (immune) with comparison to the exact published results | ✅ done (approximate / not reproduced, see below) |   notebooks 03, 04; replication records in 3.4 and 4.7; example figures for A24 and A21 in `figures/03_registration/` and `figures/04_replication/*_examples_A24_A21.png` |
| 4 | Immune interpretation revised: PTPRC not a macrophage marker; evidence level for every output | ✅ done | notebook 04 (4.6); `docs/annotation_caveats.md`; `manifests/r3_evidence_levels.csv` |
| 5 | Paired H&E–RNA dataset: 30–50 spots, patches, RNA, montage | ✅ done (section B1 and A24, 40 pairs each) |   notebook 05; `manifests/paired_spots/GSM9022969_B1/`, `manifests/paired_spots/GSM9022967_A24/`, `manifests/paired_spots/paired_sections_summary.csv` |

## Changes from the first version of the notebook

- Split into six notebooks plus two modules; processing, drawing and outputs are kept separate.
- Removed the hard-coded Windows path; paths now come from `SPACEMEL_DATA` / `SPACEMEL_SUPP` or default to `data/`.
- Removed the documentation of a `KNOWN_PATHOLOGY` fallback that did not exist in the code.
- Removed the pathology label taken from GEO title wording, which had marked every spot "melanoma".
- Removed the GSM-level CDK2 violin plot and the CD163 + PTPRC "macrophage score".
- The old notebook is in `archive/`, marked as superseded; its figures are not kept.

## Results

| Item | Result | Source |
|---|---|---|
| Sections / patients | 19 sections from 18 patients in GEO; 18 sections from 17 patients used; A2 skipped (no barcodes file); B38ex and B38_2 are one patient (B38) | 01 (1.4, 1.7) |
| Reconciliation with spatial-reasoning | Agrees on sections, A2 exclusion, 6.5 mm capture areas, gene panels, non-overlapping sections, µm per pixel, in-tissue and QC spot totals; differs on patient count (spatial-reasoning counts B38ex and B38_2 as two patients) | 01 (1.10) |
| Matrices | No in-tissue spot missing from its matrix; 0 shared barcodes between sections on a capture area; A16, A21, A23 have section-only matrices (18,085 genes), the other 15 whole-capture-area matrices (37,082 genes) | 01 (1.5, 1.6) |
| Spots | 61,734 in tissue; 39,483 pass QC (paper reports 39,481 for a different section set) | 01 (1.8), 02 (2.6) |
| QC | Failures are due to the > 500 genes rule; pass rate 15.2 % (B8) to 99.7 % (B38ex); in low-pass sections failing spots form contiguous areas | 02 (2.3, 2.5) |
| Registration (hires) | Spots lie on the tissue and stop at tissue edges; hires image 5.12–11.78 µm/px (one spot = 4.7–10.8 px) | 03 (3.1, 3.2) |
| aligned_fiducials.jpg | Greyscale CytAssist image of the same capture area; the scale factor alone places spots in the wrong position; not used | 03 (3.3) |
| R1 vs published figures | Approximate: spot–tissue alignment agrees; which published panel shows which section cannot be determined (panels labelled A–O only) | 03 (3.4) |
| R2 CDK2 | Not reproduced (no public nevus/melanoma labels). RNA-level approximation: CDK2 detected more often in PRAME-detected spots in 17 of 18 sections | 04 (4.5, 4.7) |
| R2 Fig. 2D | Approximate (qualitative): HHATL and SNX10 high in separate, adjacent areas in several sections | 04 (4.4) |
| R3 immune | Not reproduced: our outputs are single-marker RNA and provisional scores (evidence levels 1–2); the paper's are inferred composition and IMC protein (levels 3–4) | 04 (4.6, 4.7) |
| Paired dataset | 40 pairs per section, all 6 pairing checks passed in both. B1: patches 253 µm (29 px) and 61 µm (7 px) at 8.73 µm/px; minimum distance between selected spots 264.3 µm. A24: patches 259 µm (23 px) and 56 µm (5 px) at 11.27 µm/px; minimum distance 264.8 µm | 05 (5.3, 5.8, 5.11) |

## Known missing inputs

- Per-spot nevus/melanoma labels from the authors' deconvolution (not public).
- Full-resolution H&E scans; GEO has hires images only (5–12 µm/px).
- A2 barcodes; A2 is not used, by decision.
- Which patient is shown in each published spatial panel.

## Questions for the supervisor / authors

- Which patient is shown in Fig. 1B–G, Supp. Fig. S1E and Supp. Fig. S4 panels A–O?
- Can the authors share per-spot labels and the full-resolution H&E scans?
- Why is B38ex in GEO but not in the paper-analysed set (Supp. Fig. S1C)?
- Which sections does the reported total of 39,481 spots refer to?

## Next steps

- [ ] Choose retrieval relevance labels that do not come from RNA (instructions, Part IV guardrails).
- [ ] Extend the paired dataset to more sections and patients for patient-level splits.
- [ ] Optional: register aligned_fiducials.jpg (greyscale, 1.7–3.9 µm/px) to the spot grid for sharper patches;
      a first attempt (AUC-based search) did not give a reliable placement and was not kept.
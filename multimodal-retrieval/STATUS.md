# Status note · Week 2 (2–8 November 2026)

Student: Kinga · Multimodal tissue-region retrieval (`multimodal-retrieval/`)
Every result below comes from the executed notebooks; the notebook and section are given for each.
Presentation: `presentation_week2/multimodal_retrieval_week2.pptx` (editable).

## This week's tasks

| # | Task | Status | Where |
|---|---|---|---|
| 1 | Corrected manifest: capture area / patient / spot separated; no labels from GEO wording; reconciled with spatial-reasoning | ✅ done | notebook 01; `manifests/capture_areas.csv`, `tissue_sections.csv`, `spots.csv.gz`, `reconciliation_spatial_reasoning.csv` |
| 2 | Notebook run end to end; hard-coded path removed; packages and inputs documented; skipped samples recorded | ✅ done | notebooks 00–05; `README.md`; `manifests/skipped_samples.csv` |
| 3 | Replication R1 (overlay), R2 (CDK2), R3 (immune) compared with the exact published results | ✅ done (approximate / not reproduced) | notebooks 03, 04 (records in 3.4, 4.7); example figures for A24 and A21 |
| 4 | Immune interpretation revised: PTPRC not a macrophage marker; evidence level for every output | ✅ done | notebook 04 (4.6); `docs/annotation_caveats.md`; `manifests/r3_evidence_levels.csv` |
| 5 | Paired H&E–RNA dataset: 30–50 spots, patches, RNA, montage | ✅ done (A24 and B1, 40 pairs each) | notebook 05; `manifests/paired_spots/` |

## 1. What changed since last week

- The single Part II notebook is split into six notebooks (00–05) plus two modules: processing in `src/spacemel_io.py`,
  drawing in `src/spacemel_plots.py`.
- Removed the hard-coded Windows path; paths come from `SPACEMEL_DATA` / `SPACEMEL_SUPP` or default to `data/`.
- Removed the documentation of a `KNOWN_PATHOLOGY` fallback that did not exist in the code.
- Removed the pathology label taken from GEO title wording, which had marked every spot "melanoma".
- Manifest rebuilt on separate levels: capture area (GSM), patient / section, spot (`spot_uid = <GSM>:<barcode>`);
  `region_label = "not available"`.
- Removed the GSM-level CDK2 violin plot and the CD163 + PTPRC "macrophage score"; every immune output now has an
  evidence level.
- New: paired H&E patch – spot RNA dataset for A24 and B1.
- The old notebook is in `archive/`, marked as superseded; its figures are not kept.

## 2. What runs and is supported by evidence

Notebooks 00–05 run from a fresh kernel (Restart → Run All) with no errors; the executed notebooks are committed.

| Item | Result | Source |
|---|---|---|
| Sections / patients | 19 sections from 18 patients in GEO; 18 sections from 17 patients used; A2 skipped (no barcodes file); B38ex and B38_2 are one patient (B38) | 01 (1.4, 1.7) |
| Reconciliation with spatial-reasoning | Agrees on sections, A2 exclusion, 6.5 mm capture areas, gene panels, non-overlapping sections, µm per pixel, in-tissue and QC spot totals; differs on patient count (spatial-reasoning counts B38ex and B38_2 as two patients) | 01 (1.10) |
| Matrices | No in-tissue spot missing from its matrix; 0 shared barcodes between sections on a capture area; A16, A21, A23 section-only (18,085 genes), the other 15 whole-capture-area (37,082 genes) | 01 (1.5, 1.6) |
| QC | 61,734 in-tissue spots, 39,483 pass the paper's QC (> 500 genes, < 30 % MT; paper: 39,481); failures come from the 500-gene rule; pass rate 15.2 % (B8) to 99.7 % (B38ex) | 01 (1.8), 02 (2.3, 2.6) |
| R1 overlay | Spots at true 55 µm size lie on the tissue and stop at tissue edges; hires image 5.12–11.78 µm/px; aligned_fiducials.jpg not usable with its scale factor (0–63.8 % of spots inside the image) | 03 (3.1–3.3) |
| R1 vs published figures | Approximate: no published panel could be matched to a section (panels carry no patient IDs) | 03 (3.4) |
| R2 CDK2 | Not reproduced (no public nevus/melanoma labels). RNA-level approximation: CDK2 detected more often in PRAME-detected spots in 17 of 18 sections (A24: 92.1 % vs 10.5 %; published Table S5: 99.8 % vs 10.7 %) | 04 (4.5, 4.7) |
| R2 Fig. 2D | Approximate (qualitative): HHATL and SNX10 high in separate, adjacent areas in several sections | 04 (4.4) |
| R3 immune | Not reproduced: our outputs are single-marker RNA and provisional scores (evidence levels 1–2); the paper's are inferred composition and IMC protein (levels 3–4) | 04 (4.6, 4.7) |
| Paired dataset | 40 pairs per section, all 6 pairing checks passed in both. A24: patches 259 µm (23 px) and 56 µm (5 px) at 11.27 µm/px, minimum distance 264.8 µm. B1: 253 µm (29 px) and 61 µm (7 px) at 8.73 µm/px, minimum distance 264.3 µm | 05 (5.3, 5.8, 5.11) |

## 3. What remains unresolved

- **No independent nevus / melanoma label per spot.** The paper's labels come from RNA deconvolution and are not
  public, so retrieval relevance cannot yet be defined without using RNA. Expression groupings such as
  "PRAME detected" are provisional, not pathology.
- **H&E resolution.** GEO has hires images only (5–12 µm per pixel; one spot = 5–11 px), so patches show tissue
  colour and architecture, not cells. Full-resolution scans are not public; aligned_fiducials.jpg does not align as
  given.
- **Replication stays approximate.** Published panels name no patient; R2 and R3 cannot be repeated exactly without
  the authors' spot labels.
- **The paired set is small.** 80 spots from 2 patients are enough to verify pairing, not to evaluate across
  patients. Some spots sit next to unstained gaps (e.g. A24_001) and still pass QC, because QC uses RNA only.
- **Open questions:** which patient each published panel shows; why B38ex is in GEO but not in Supp. Fig. S1C;
  which sections the paper's 39,481 spots refer to.

## 4. Next proposed correction or test

1. **Most important: independent region labels for A24 and B1**, from the authors' per-spot labels or a pathologist's
   annotation of the H&E, so that retrieval relevance is defined without RNA.
2. Agree on one patient definition with spatial-reasoning (B38ex + B38_2 = patient B38, Table S1), possibly as a
   shared manifest in `shared/`, so both projects split by the same patients.
3. Extend the paired dataset to more sections and patients, for patient-level splits.
4. Ask the authors for full-resolution H&E scans (registering aligned_fiducials.jpg was tried and did not give a
   reliable placement).

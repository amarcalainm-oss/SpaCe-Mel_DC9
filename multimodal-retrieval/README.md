# Multimodal Tissue-Region Retrieval (SPACE-MEL DC9 — Student 2)

**Provisional title:** Evaluating Histology–Transcriptomics Fusion for Interpretable Melanoma Tissue Region Retrieval

**Research question:** Does integrating transcriptomic information with histological features improve the identification and retrieval of biologically meaningful melanoma tissue regions?

**Primary contribution:** Interpretable, lightweight multimodal embeddings, and a rigorous evaluation of whether H&E and spatial gene expression give *complementary* descriptions of nevus/melanoma tissue regions, especially across patients.

> A new fusion architecture is optional. Rigorous, leakage-free evaluation is the point.

---

## 1. Questions addressed

| ID | Question | Planned output |
|----|----------|----------------|
| **M1** | How do RNA and histological image embeddings compare? | RNA-only vs image-only embedding plots, patient/slide effects, retrieval examples and failure cases |
| **M2** | Does multimodal fusion improve tissue-region retrieval? | Precision@k, Recall@k, mAP for RNA-only, image-only, concatenation and one stronger fusion baseline (same queries, gallery and tuning budget) |
| **M3** | Does retrieval work for unseen patients? | Cross-patient metrics with patient-level confidence intervals; failure analysis linked to tissue heterogeneity |
| **M4** | Which tissue regions benefit most from fusion? | Region-stratified gain/loss (nevus, melanoma, other compartments), hard positive/negative examples |
| **M5** | Which design choices drive performance? | Ablation table (patch size, RNA preprocessing/dimensionality, fusion strategy, normalization), stain robustness, recommended parsimonious baseline |

Core hypothesis: histology and transcriptomics capture partly non-overlapping information about tissue state, so a simple fusion of the two retrieves biologically similar regions better than either alone, and the gain is region-dependent.


## References

- Kreuger IZM et al. (2026). *Cancer Research* 86:4400–4413. https://doi.org/10.1158/0008-5472.CAN-25-2934
- GEO GSE298774: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE298774
- Author code: https://github.com/roderickslieker/NevusMelanomaVisium
- IMC data: https://zenodo.org/records/15582615
- SPACE-MEL: https://space-mel.eu/

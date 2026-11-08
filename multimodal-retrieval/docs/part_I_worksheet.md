# Part I · Reference-paper worksheet

**Student 2 (multimodal tissue-region retrieval)**, SPACE-MEL DC9
**Paper:** Kreuger IZM et al. *Spatial Analysis Reveals Gene Expression and Microenvironmental Changes in the
Transition of Nevus to Melanoma.* Cancer Res 2026;86:4400–13. doi:10.1158/0008-5472.CAN-25-2934
**Code:** <https://github.com/roderickslieker/NevusMelanomaVisium>, **Data:** GEO GSE298774

---

## 1. Primary biological research question and rationale

*State what the authors wanted to learn about the nevus-to-melanoma transition; distinguish biological aims from methods.*

**Aim.** To characterise the transcriptional and microenvironmental changes that accompany the transition from nevus
to melanoma.

**Rationale.** Nevus and melanoma harbour mutations in the same genes (BRAF or NRAS), which activate the MAPK
signalling pathway. Earlier work mainly used bulk RNA sequencing or analysed limited gene subsets, lacked spatial
context, or focused on advanced-stage melanoma rather than early stages.

**Gap addressed.** This study focuses specifically on transcriptional reprogramming and on alterations in the tumour
microenvironment, with spatial context and in early-stage lesions.

## 2. Biological material and unit of independence

*Identify tissue states, sampling structure, Visium spots versus specimens/patients, and use of adjacent sections.*

- **Material:** 18 lesions, one per patient. The **patient is the unit of independence**. Patients were aged 17–72,
  with melanoma stages T1a–T3b.
- **Measurements:** 39,481 spots (the unit of measurement: 55 µm, containing 5–10 cells each), covering up to
  18,072 genes.
- **Tissue states:** the study focuses on intradermal nevus to invasive melanoma; junctional nevus to melanoma
  in situ is not covered in detail.
- **Annotation:** nevus and melanoma components were evaluated on H&E sections with immunohistochemical staining for
  SOX10, PRAME and p16.
- **Spot labels:** deconvolution identified 15 transcriptional profiles, each assigned a cell type using publicly
  available profiles. Each spot was assigned a single cell type; for 80.5 % of spots, the assigned cell type made up at
  least 40 % of the spot.
- **Adjacent sections:** FFPE skin blocks were sectioned at 5 µm for Visium; a consecutive 4 µm section from the same
  block was used for imaging mass cytometry (IMC).

## 3. Why Visium was combined with imaging mass cytometry

*Specify what each modality measures and which claims were supported by RNA versus protein evidence.*

| | Visium | IMC |
|---|---|---|
| Measures | RNA, ~18,000 genes | Protein, 43 markers |
| Resolution | Spot (55 µm, 5–10 cells) | Pixel / single cell |
| Tells us | Which genes are expressed, and where | Which proteins are present, and where |

Protein does not always follow from transcription (RNA can be present without the protein), so RNA alone cannot
confirm or exclude a cell type. IMC was therefore used to **validate** the Visium findings, confirming actual markers
and providing single-cell spatial resolution.

## 4. How nevus, melanoma and other regions were identified

*Locate the description of histopathology/region labels and establish whether per-spot labels are publicly available.*

1. **Histopathology (before computation):** a dedicated dermatologist reviewed the stained tissue samples.
2. **Computation:** deconvolution (STdeconvolve) separated transcriptional profiles, which were assigned cell types
   using publicly available data. The locations of nevus and melanoma spots were checked against the histopathological
   annotation.
3. **Melanoma signatures:** two were identified, M1 and M2. M2 tended to have low spot purity, so the study focused
   mainly on M1.

**Availability:** per-spot labels are **not** publicly available. They would have to be reconstructed by running the
deconvolution on GSE298774.

## 5. Preprocessing and analytical methods

*Include filtering, normalisation, cell-type deconvolution, differential expression, immune infiltration, spatial
analyses, pseudotime and ligand–receptor analysis where applicable. Reference scripts.*

**Samples and sequencing.** FFPE blocks from a pathology archive were selected where nevus adjacent to melanoma was
reported, and verified by a dedicated dermatologist (H&E, SOX10, PRAME, p16) to choose the most representative samples
with clear morphological distinction. Blocks were sectioned for Visium (55 µm spots, 5–10 cells each, hence the need
for deconvolution) and libraries sequenced on a NovaSeq 6000.

**Filtering.** Using the Visium image, the H&E image and the R package semla, spots with more than 500 genes and less
than 30 % mitochondrial counts were retained.

| Analysis | Method | Script |
|---|---|---|
| Deconvolution | STdeconvolve (reference-free); number of topics K chosen with `fitLDA`, K = 10–20; topics assigned to cell types by Pearson correlation with literature signatures | `Deconvolute_Visium.md` |
| Neighbourhood / distance | All spots surrounding a spot of a given cell type identified; distance from epithelial cells to the nearest melanoma spot | `Immune_infiltration_IC1_Franken.md` |
| Differential expression | Nevus- vs melanoma-dominated spots, negative binomial model; thresholds \|log2FC\| ≥ 1, Padj ≤ 0.05, expressed in > 25 % of spots. About 250 genes showed an on/off pattern (almost exclusive to nevus or melanoma). Also examined per patient and checked against external data | `DEGs_Visium_NevusTumor.md` |
| Pathway enrichment | Reactome and KEGG on up- and down-regulated DEGs | `DEGs_OnOff_Enrichment.md` |
| Cell cycle | Spots with > 50 % purity; percentage per phase | `CellCycle_estimation.md` |
| Ligand–receptor | SpatialDM on spatially close spots, to study nevus–melanoma communication | `SpatialDM_ExpressionBased_withFiltering.md` |
| Immune cells | Estimated with semla functions (RunNNLS) and a single-cell reference | `Immune_infiltration_IC1_Franken.md` |
| IMC | Consecutive section, custom panel of structural and cell-defining markers; MCD/txt data, pixel-based analysis; poor-quality markers excluded | — |

## 6. Three most important biological findings

*For each, give the evidence and figure/table number.*

1. **Proliferation and stress adaptation.** Pathways upregulated in melanoma support cell-cycle progression and help
   manage increased metabolic and proteotoxic stress (Fig. 3A–B). Cell-cycle phases match this: melanoma spots are
   mainly in S and G2/M phase, nevus spots in G1 (Fig. 3C–D).
2. **Melanocytic programme.** Developmental pathways regulated by the transcription factor MITF are upregulated from
   nevus to melanoma. Melanoma cells have higher melanocytic signature scores than nevus cells, a shift from a neural
   crest-like transitory signature in nevus to a more melanocytic one in melanoma (Fig. 3E–I). MITF expression itself
   did not increase while many of its targets did, suggesting post-translational regulation or other transcription
   factors.
3. **Microenvironment remodelling.** Combining Visium and IMC (43 immune and microenvironmental proteins; Fig. 5A–B):
   - Visium revealed two immune signatures: one near melanoma comprising multiple cell types, and one near fibroblasts,
     mainly plasma cells.
   - IMC confirmed that the immune population around the tumour includes multiple immune cell types, whereas nevus
     tissue contained almost exclusively M2-like macrophages.
   - Pathway analysis showed enrichment of antigen-presentation genes; genes linked to extracellular-matrix
     organisation and integrins shifted in expression, and melanoma cells upregulated ECM-degradation genes.
   - Deconvolution identified distinct fibroblast and keratinocyte signatures (Fig. 4A–B).

## 7. Immune cells around nevi versus melanoma

*Differentiate observation, inferred cell identity and validated protein marker evidence; mention macrophage and T-cell patterns.*

| Evidence type | Finding |
|---|---|
| **Inferred from RNA (Visium)** | Two immune signatures: **IC1** near melanoma, containing multiple cell types; **IC2** near fibroblasts throughout the dermis, mainly plasma cells |
| **Protein-validated (IMC)** | Around the tumour: multiple immune cell types (e.g. T cells, CD4+, CD8+), with few immune cells inside the tumour. In the nevus: almost only macrophages (Fig. 5B, 5D) |
| **Macrophage subtypes** | Nevus macrophages were M2-like (immunosuppressive); near the tumour there were also CXCL10+ macrophages, which are M1-like, inflammatory and can attract T cells |
| **Interpretation** | May indicate local immune activation in the melanoma region |

## 8. Spatial questions already investigated

*Look explicitly for neighbourhood/distance analyses, deconvolution, spatial ligand–receptor work and pseudotime in both the paper and code repository.*

- **Neighbourhood:** all spots surrounding a region were identified, mainly to characterise the immune
  microenvironment around tumour versus nevus regions.
- **Distance:** minimal distance from epithelial cells to the nearest melanoma spots.
- **Deconvolution:** maps cell-type composition across the tissue, enabling spatial comparisons (STdeconvolve; each
  spot contains 5–10 cells).
- **Ligand–receptor:** SpatialDM, run separately for each patient.
- **Pseudotime:** not described specifically in the paper, but scripts are in the repository
  (`PseudoTime_NevusTumor.md`), so it was probably an exploratory or supplementary step.

## 9. Main limits for new computational work

*Address cross-sectional sampling, spot-level resolution, patient/slide dependence, annotation quality and variation across samples.*

- **Cross-sectional sampling.** Each sample was taken at one time point, so temporal change cannot be observed. The
  paper shows that nevus and melanoma differ in gene expression and lie next to each other, and from that infers that
  nevus is becoming melanoma; this is not backed by observations over time.
- **Patient dependence.** Each capture is specific to a patient, so some findings may reflect one patient's biology,
  anatomy or immune history, or be driven by one or two samples.
- **Scope.** The study focuses on overall patterns and does not examine large sample sets for more specific changes.
- **Resolution.** Spot level, not single-cell (partly addressed with unsupervised computational methods).
- **Other.** Probe-based measurement limits the study of novel transcripts; no integration with DNA sequencing; and
  both pathologist annotation and deconvolution topic assignment add uncertainty to spot labels.

---

## Novelty audit

| Previously studied area | Evidence in paper / code | Novel question |
|---|---|---|
| **Differential expression, proliferation and melanocytic programmes** | **DEGs** (`DEGs_Visium_NevusTumor.md`, Seurat `FindMarkers`, Table S4): most genes upregulated in melanoma. **Proliferation** (Fig. 3A–D, Tables S6–S7, `CellCycle_estimation.md`): cells divide more actively in melanoma. **Melanocytic programme** (Fig. 3E–I, Table S6, `DEGsPathwaysTsoi_PseudoTimesAllSamples.md`): higher melanocytic signature scores in melanoma than nevus | Do spots at the nevus–melanoma boundary show intermediate topic composition, or do topic proportions switch abruptly? The paper defines which genes differ overall, but not whether boundary spots are in an intermediate state. |
| **Immune composition, infiltration and spatial proximity** | **Deconvolution** (`Deconvolute_Visium.md`, STdeconvolve, `fitLDA`): 15 transcriptional profiles. **Immune comparisons** (`Immune_infiltration_IC1_Franken.md`, semla `RunNNLS`, Fig. 5A–C): higher immune density around the melanoma part; two immune signatures. **Distances** (`Immune_infiltration_IC1_Franken.md`, semla `RadialDistance`, Fig. 5A–C): minimum distance from epithelial cells to the nearest melanoma spot | Do specific immune cell pairs (e.g. particular macrophages) co-occur within the same spots, and does their co-occurrence change with distance from the tumour boundary? The paper reports presence and abundance in defined zones but does not test co-occurrence as a function of distance. |
| **Pseudotime, spatial ligand–receptor and protein-level comparisons** | **Pseudotime** (`PseudoTime_NevusTumor.md`, slingshot): spots ordered along a nevus-to-tumour trajectory in PCA space; genes correlated with pseudotime identified with a linear model. **Ligand–receptor** (`SpatialDM_ExpressionBased_withFiltering.md`, SpatialDM, Tables S4, S9, S10, Fig. S7A–B): spatially co-expressed ligand–receptor pairs. **Protein** (Fig. 5A–B): IMC maps of 43 immune and microenvironmental proteins | Which ligand–receptor pairs are consistently active across patients, and does their spatial range differ between nevus and melanoma? The paper tests each patient separately, but does not ask which pairs recur across most or all patients, or how far apart ligand- and receptor-expressing spots can be while still co-varying. |

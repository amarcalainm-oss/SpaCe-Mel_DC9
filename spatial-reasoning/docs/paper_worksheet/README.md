# Paper worksheet: Kreuger et al. 2026

Answers to Part I of the SPACE-MEL student instructions: the common worksheet on the
reference paper and the novelty audit.

**Paper:** Kreuger et al. (2026). *Cancer Research* 86(17):4400–4413.
DOI [10.1158/0008-5472.CAN-25-2934](https://doi.org/10.1158/0008-5472.CAN-25-2934) · PMID 42258703.
**Data:** GEO [GSE298774](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE298774) (Visium),
Zenodo [15582615](https://zenodo.org/records/15582615) (IMC).
**Code:** [roderickslieker/NevusMelanomaVisium](https://github.com/roderickslieker/NevusMelanomaVisium).

**Author:** Aitor · **Status:** draft


## Q1. What are the paper's primary biological research question and its rationale?

> State what the authors wanted to learn about nevus-to-melanoma transition; distinguish biological aims from methods.

**Answer:**

-They wanted to see what changed transcriptionally and in the tissue when a benign nevus progressed to melanoma. Previous comparisons only used RNA-seq, but they added the spatial component. Nevus associated melanomas give side by side benign and malignant tissue within the same patient conditions, making this comparison possible. 


---

## Q2. What biological material was studied, and what is the correct unit of independence?

> Identify tissue states, sampling structure, Visium spots versus specimens/patients, and use of adjacent sections.

**Answer:**

Tissues with nevus and melanoma components were studied, and also with surrounding normal skin structures. The unit of independence are each patients (lesions, tissues), since spots inside them are spatially correlated. Therefore spot counts should not be treated as independent. 



---

## Q3. Why did the authors combine Visium with imaging mass cytometry?

> Specify what each modality measures and which claims were supported by RNA versus protein evidence.

**Answer:**

Visium measures RNA in each spot, but each spot mixes multiple cells. The cell composition of a spot can be estimated with deconvolution, but this is an inference from the expression on the spot, not a direct measurement. That is why the authors added imaging mass cytometry (IMC), which measures proteins at single-cell resolution, so they could check the cell identities with protein evidence. With RNA we measure the expresion of ~18000 genes in each 55 µm spot, whereas IMC measures 43 proteins at single cell resolution. 

Claims for RNA only:
- The nevus-melanoma gene differences (expression)
- Higher proliferation: melanoma cells seem to divide more
- The nevus looked more "immature" (neural crest-like) and melanoma more "mature" (melanocytic).
- Extracellular matrix (ECM) remodelling on melanoma
- Ligand-receptor pairs

Claims for IMC (protein):
- More immune cells around melanoma and less inside the tumor
- Macrophages, only immune cells inside the nevus
- More or denser collagen at melanoma areas


---

## Q4. How were nevus, melanoma, and other tissue regions identified or annotated?

> Locate the description of histopathology/region labels and establish whether per-spot labels are publicly available.

**Answer:**

First, an expert selected lesions with clear nevus/melanoma components. At spot level, deconvolution was used (15 topics) and each spot was assigned to its most frequent topic. Per-spot labels are not public, and if they are reconstucted they can´t be used for validation. 


## Q5. What preprocessing and analytical methods did the authors use?

> Include filtering, normalization, cell-type deconvolution, differential expression, immune infiltration, spatial
> analyses, pseudotime and ligand-receptor analysis where applicable. Reference scripts.

- Filtering: keep spots with >500 genes and <30% mitochondrial counts
- Normalization: SCTransform, parameters unknown
- Cell-type deconvolution: STdeconvolve. With fitLDA choose from k=10:20, chosen k=15. Topics name given by correlation with signatures.
- Differential expression: negative binomial + cell type fraction as a latent variable.
- Spatial: they use neighbouring spots of a type, and define distance as Euclidean distance in pixels to the nearest melanoma spot.
- Immune infiltration: NNLS with the Franken single-cell reference.
- Ligand–receptor: SpatialDM, run per patient, keeping pairs found in ≥ 5 patients, annotated with CellChatDB. Script: SpatialDM_ExpressionBased_withFiltering.md.
- Pseudotime: slingshot (PCA first)
  


---

## Q6. What are the three most important biological findings?

> For each, give the evidence and figure/table number. Consider proliferation/metabolic adaptation, melanocytic
> programs and microenvironment remodeling.

### Finding 1:

- **What they found:** Proliferation with metabolic adaptation: melanoma cells seem to divide more, and they switch on the "machinery" needed to support that growth.
- **Evidence:**
  - Pathway enrichment (RNA). The genes that are higher in melanoma were grouped into Reactome pathways (lists of genes that work on the same biological task). The following groups were up-represented in melanoma: cell-cycle transition, metabolism and protein quality control.
  - Cell-cycle scoring (RNA). In spots with > 50 % nevus or melanoma, a Seurat function assigned each spot a cell-cycle phase: G1 (not dividing), S (copying DNA) or G2/M (about to divide), based on phase-specific genes 
- **Figure/table:** Figures 3A and 3C–D.

### Finding 2: 

- **What they found:** Melanocytic programmes: melanoma cells look more like mature melanocytes (pigment-producing cells), while nevus cells look more neural crest-like (a less mature state). This happens without an increase in MITF, the main gene controlling melanocyte identity.
- **Evidence:**
    - Pathway enrichment (RNA). Pathways controlled by MITF were up in melanoma, including its target genes TYR and PMEL (pigment production), CDK2 (cell division) and KIT (a growth-signal receptor).
    - Lineage signature scores (RNA). Each spot was scored with published gene lists for melanocyte states. Melanoma spots scored higher on the melanocytic signature, and nevus spots higher on the neural crest-like/transitory signature. MITF itself was not higher in melanoma.
- **Figure/table:** Figures 3A and 3E–I

### Finding 3: 

- **What they found:** Microenvironment remodelling: the tissue around melanoma changes, with more antigen presentation (cells showing protein fragments to T cells), a rebuilt extracellular matrix (ECM, the protein network between cells) and more immune cells, which are activated but also show signs of "being exhausted".
- **Evidence:**
    - Antigen presentation and ECM (RNA). Genes that load protein fragments for T cells (TAP1, TAP2, B2M) were up in melanoma. ECM genes changed, and enzymes that break down the ECM (MMPs, cathepsins) went up.
    - Immune cells (RNA + protein). The immune signature IC1 sits next to melanoma and expresses activation and exhaustion genes (RNA). IMC confirmed more immune cells around melanoma than around nevus, few inside the tumour, and denser collagen at melanoma sites (protein).
      
- **Figure/table:** Figures 3A and 5A–G

---

## Q7. What did the authors report about immune cells around nevi versus melanoma?

> Differentiate observation, inferred cell identity and validated protein marker evidence; mention macrophage and
> T-cell patterns.

**Answer:**
They found that immune cells are much denser around the melanoma than around the nevus (Figures 5A–B), with few cells inside the tumour mass. 

**Macrophages:** Inside the nevus, the only immune cells are macrophages. This was seen directly with protein (IMC), using the markers CD14, CD68 and CD163 (Figure 5D, Supp. Figure S9C). Their subtype was not measured with protein, it was inferred from RNA (NNLS with a reference dataset). Inside the nevus they are mainly TREM2+ and LYVE1+ (M2-like, they calm the immune response). Near melanoma there are also CXCL10+ macrophages (M1-like, inflammatory, they attract T cells) (Figure 5C, Supp. Figure S9D).

**T cells:** IMC (protein) shows CD4+ (helper) and CD8+ (cytotoxic) T cells around the tumour, but very few inside it (Figures 5B, 5D). Their state is only inferred from RNA: the immune signature next to melanoma (IC1) expresses activation genes (CD69, CD38, IL2RA), genes that attract T cells (CXCL9, CXCL10) and exhaustion genes (TIGIT, HAVCR2) (Figure 5F). So the T cells seem to respond to the tumour, but they stay at the edge and get "worn out".

Summary: observed with protein = which immune cells are there and where. Inferred from RNA = their subtype and state (M1/M2, activated, exhausted).


---

## Q8. Which spatial questions have already been investigated?

> Look explicitly for neighborhood/distance analyses, deconvolution, spatial ligand-receptor work and pseudotime in
> both the paper and code repository.

| Analysis | Done? | In the paper | In the code | What exactly was asked |
|---|---|---|---|---|
| Neighbourhood / distance | Yes | Fig. 4A (neighbours of fibroblasts F1/F2), Fig. 4E (keratinocytes) | DEGs_Visium_Keratinocytes.md, Immune_infiltration_IC1_Franken.md | Which spot types are next to F1/F2; distance (in pixels) from keratinocyte spots to the nearest melanoma spot; in the code only, immune cell fractions in spots within 500 of the tumour or nevus vs further away |
| Deconvolution | Yes | Fig. 1, Methods | Deconvolute_Visium.md | Cell-type mix of each spot (STdeconvolve, 15 topics); each spot gets its main topic as label |
| Spatial ligand–receptor | Yes | Supp. Fig. S7, Supp. Tables S9–S10 | SpatialDM_ExpressionBased_withFiltering.md | Which signal–receptor pairs are expressed in neighbouring spots, in nevus vs melanoma |
| Pseudotime | Only in code | No | DEGsPathwaysTsoi_PseudoTimesAllSamples.md, PseudoTime_NevusTumor.md | Order spots along a nevus → melanoma path (slingshot) |
| Other | Yes | Fig. 5 | Immune_infiltration_IC1_Franken.md | Immune cell types in immune spots (NNLS), and IMC images of immune cells and collagen |

**Notes:**

All of these use the expression-based spot labels (deconvolution), not pathologist labels. The only distances in the paper are in pixels and pooled across lesions, even though pixel size changes between capture areas. The immune proximity analysis in the code uses one fixed cutoff (500) and is not described in the main text. What has not been done: distances in µm per patient, distance as a continuous value instead of one cutoff, comparisons across patients, and how regions are arranged in the tissue (borders, gaps between tumour and immune cells).

---

## Q9. What are the main limits of this study for new computational work?

> Address cross-sectional sampling (not longitudinal proof of progression), spot-level resolution, patient/slide
> dependence, annotation quality and variation across samples.

- **Cross-sectional sampling:** each lesion is one snapshot in time. Nevus and melanoma are seen side by side, but the transition from one to the other is inferred, not observed.
- **Spot-level resolution:** each spot is 55 µm and mixes several cells, so cell types are estimated (deconvolution), not seen.
- **Patient / slide dependence:** there are only 18 patients, and spots from the same patient are not independent. Some patients share a capture area, so patient and slide effects are mixed.
- **Annotation quality:** nevus/melanoma labels come from expression (main topic per spot), were only checked visually, and are not public. So they can't be used as ground truth.
- **Variation across samples:** data quality changes a lot between patients (median counts per spot from ~130 to ~22,000). After the paper's filter some patients keep very few spots (B8, B14, A17). There are two gene panels (~37k and ~18k genes) and different pixel sizes.
- **Other:** A2 can't be used (no barcodes file). IMC was done only on 9 lesions and in small regions, on the next section, so it can't be matched spot by spot.

---

## Q10. Novelty audit: do not redo established results

> Identify the exact figure, table, supplementary analysis or script supporting each published area below. Explain
> what remains unanswered and why a proposed follow-up would be genuinely new rather than a rerun with different
> software.

### Area 1: Differential expression, proliferation and melanocytic programs

- **Evidence in paper/code** (result, samples, method): 1,976 DEGs between nevus and melanoma spots (negative binomial, Fig. 2, Supp. Table S4; DEGs_Visium_NevusTumor.md), pathway enrichment (Fig. 3A), cell-cycle scoring (Fig. 3C–D) and melanocytic signatures (Fig. 3E–I). Melanoma spots from 12 lesions and nevus spots from 17.
- **What remains unanswered:** where in the tissue these changes happen. The comparisons are nevus vs melanoma as groups, not by position.
- **New question beyond repeating a known gene/program difference:** are the dividing melanoma spots at the edge of the tumour or in the centre? Does it change with distance to the nevus or to immune cells?
- **Why it is new, not a rerun:** it uses the position of the spots (distances in µm), not only the group difference. Running the same DE with other software would not be new.

### Area 2: Immune composition, infiltration and spatial proximity

- **Evidence in paper/code** (deconvolution, immune comparisons, distance analyses): immune signatures IC1/IC2 and NNLS cell types (Fig. 5A–C), IMC (Fig. 5B, 5D, 5G), keratinocyte distance to melanoma (Fig. 4E), and the immune proximity analysis with a 500 cutoff in Immune_infiltration_IC1_Franken.md.
- **What remains unanswered:** how far immune regions are from the tumour in µm, per patient, and how this changes between patients. The code only uses one cutoff and pools the lesions.
- **What can be tested about spatial organization beyond immune abundance or existing proximity results:** distance from immune spots to the tumour as a continuous value, whether there is a gap with no immune cells between tumour and immune cells, and the immune fraction in the neighbourhood of each spot.
- **Why it is new, not a rerun:** the paper says "more immune cells near melanoma", but it does not measure the distances or the arrangement. We would measure them in µm, per patient and per tissue section.

### Area 3: Pseudotime, spatial ligand–receptor and protein-level comparisons

- **Evidence in paper/code** (workflow, figures, scripts, validation data): SpatialDM ligand–receptor pairs (Supp. Fig. S7, Supp. Tables S9–S10; SpatialDM_ExpressionBased_withFiltering.md), pseudotime only in the code (slingshot; PseudoTime_NevusTumor.md), IMC on 9 lesions (Fig. 5; Zenodo 15582615).
- **What remains unanswered:** pseudotime is not reported or validated in the paper. Ligand–receptor pairs are only co-expression, not proven communication, and it is not shown where in the tissue they are.
- **Methodological claim or independent analysis that remains untested:** whether the melanoma–immune ligand–receptor pairs are concentrated at the border between tumour and immune cells.
- **Why it is new, not a rerun:** rerunning SpatialDM or slingshot would repeat their work. Asking where the pairs are, measured in µm from the tumour border, is a different question.

### Novelty statement

The authors did a fixed set of biological analyses to describe the nevus-to-melanoma transition. Our project does not try to find new biology. We build simple spatial operations (spots within a radius, distance to a region, neighbourhood fraction), in µm and per tissue section, and test them on examples with known answers. Then an LLM should pick and combine these operations to answer natural-language spatial questions, and its answers are compared with reference answers computed with code. So the contribution is the method and how it is evaluated, not new biological findings. We reuse their data and QC filter, but not their analyses.

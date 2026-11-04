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

**Macrophages:** Inside the nevus, the only immune cells are macrophages. This was seen with protein (IMC), so it is a direct observation (Figure 5D). The type of macrophage is not seen, it is inferred from RNA: in the nevus they look like macrophages that calm the immune response, and near melanoma there are also some that cause inflammation and attract T cells (Figure 5C).

**T cells:** T cells are around the tumour but very few get inside it. This was also seen with protein (Figures 5B, 5D). From RNA, they seem to be activated (reacting to the tumour) but also "exhausted", meaning they have been active for too long and work less (Figure 5F). This state is inferred, not seen with protein.

So, with protein we see which immune cells are there and where. What type or state they are in comes only from RNA.


---

## Q8. Which spatial questions have already been investigated?

> Look explicitly for neighborhood/distance analyses, deconvolution, spatial ligand-receptor work and pseudotime in
> both the paper and code repository.

| Analysis | Done? | In the paper | In the code | What exactly was asked |
|---|---|---|---|---|
| Neighbourhood / distance | Yes | Fig. 4A, Fig. 4E | DEGs_Visium_Keratinocytes.md, Immune_infiltration_IC1_Franken.md | Which spots are next to each fibroblast type. How far skin cells are from the nearest melanoma spot (in pixels). In the code only: which immune cells are close to the tumour or the nevus |
| Deconvolution | Yes | Fig. 1 | Deconvolute_Visium.md | What mix of cells is in each spot. Each spot gets a label from this |
| Spatial ligand–receptor | Yes | Supp. Fig. S7 | SpatialDM_ExpressionBased_withFiltering.md | Which cells could be "talking" to each other, because the signal and its receiver are in nearby spots |
| Pseudotime | Only in code | No | PseudoTime_NevusTumor.md | Order the spots from nevus to melanoma, as if it was a timeline |

**Notes:**

All of this uses the labels made from expression, not labels from a pathologist. The distances in the paper are in pixels and all lesions are put together, even if the pixel size is different between them. Nobody measured distances in µm for each patient, or how the regions are placed in the tissue (for example, if there is a gap between the tumour and the immune cells).

---

## Q9. What are the main limits of this study for new computational work?

> Address cross-sectional sampling (not longitudinal proof of progression), spot-level resolution, patient/slide
> dependence, annotation quality and variation across samples.

- **Cross-sectional sampling:** each lesion is one photo in time. We see nevus and melanoma side by side, but we never see one turning into the other.
- **Spot-level resolution:** each spot mixes several cells, so we can only estimate which cells are inside.
- **Patient / slide dependence:** there are only 18 patients, and spots from the same patient are not independent. Some patients share the same slide.
- **Annotation quality:** the nevus/melanoma labels come from expression, not from a pathologist, and they are not public. So they can't be used as ground truth.
- **Variation across samples:** the quality changes a lot between patients. After the filter some patients keep very few spots (B8, B14, A17).
- **Other:** A2 can't be used because a file is missing. IMC was only done on 9 lesions and small regions, so it can't be compared spot by spot.

---

## Q10. Novelty audit: do not redo established results

> Identify the exact figure, table, supplementary analysis or script supporting each published area below. Explain
> what remains unanswered and why a proposed follow-up would be genuinely new rather than a rerun with different
> software.

### Area 1: Differential expression, proliferation and melanocytic programs

- **Evidence in paper/code:** the gene differences between nevus and melanoma (Fig. 2), the pathways and cell division (Fig. 3A, 3C–D) and the melanocytic programmes (Fig. 3E–I). Script: DEGs_Visium_NevusTumor.md.
- **What remains unanswered:** where in the tissue these changes happen. They compare nevus vs melanoma as two groups, without looking at the position of the spots.
- **New question beyond repeating a known gene/program difference:** for example, are the melanoma spots that divide more at the edge of the tumour or in the centre?
- **Why it is new, not a rerun:** it uses the position of the spots (distances in µm). Doing the same comparison with other software would not be new.

### Area 2: Immune composition, infiltration and spatial proximity

- **Evidence in paper/code:** the immune cells estimated in the spots and the IMC images (Fig. 5), the distance of skin cells to melanoma (Fig. 4E), and in the code, which immune cells are close to the tumour (Immune_infiltration_IC1_Franken.md).
- **What remains unanswered:** how far the immune cells are from the tumour, in µm and for each patient. In the code they only use one distance limit and all lesions together.
- **What can be tested about spatial organization beyond immune abundance or existing proximity results:** the exact distance from immune regions to the tumour, if there is an empty gap between them, and how many immune spots there are around each spot.
- **Why it is new, not a rerun:** the paper says "more immune cells near melanoma", but it doesn't measure how near or how they are placed.

### Area 3: Pseudotime, spatial ligand–receptor and protein-level comparisons

- **Evidence in paper/code:** the "talking" cells analysis (Supp. Fig. S7, SpatialDM_ExpressionBased_withFiltering.md), pseudotime only in the code (PseudoTime_NevusTumor.md), and IMC on 9 lesions (Fig. 5).
- **What remains unanswered:** the pseudotime is not in the paper, so it is not checked. The "talking" cells are only a guess (signal and receiver close), and they don't show where in the tissue this happens.
- **Methodological claim or independent analysis that remains untested:** if these signals between tumour and immune cells happen mostly at the border between them.
- **Why it is new, not a rerun:** running the same tools again would repeat their work. Asking where it happens, with distances, is a different question.

### Novelty statement

The authors wanted to describe the biology of the change from nevus to melanoma. We don't want to find new biology. We want to build simple spatial tools (which spots are within a distance, how far a spot is from a region, what is around a spot), measured in µm, and check that they give the right answer on easy examples. Then an LLM should choose these tools to answer questions written in normal language, and we compare its answers with the correct ones calculated by the code. So what we add is the method and how to check it, not new biological results.

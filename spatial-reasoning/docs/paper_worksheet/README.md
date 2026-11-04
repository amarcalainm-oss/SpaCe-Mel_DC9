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

- **What they found:** Melanocytic programmes
- **Evidence:** _…_
- **Figure/table:** Figures 3E–I

### Finding 3: _…_

- **What they found:** _…_
- **Evidence:** _…_
- **Figure/table:** Figures 3A and 5A–G

---

## Q7. What did the authors report about immune cells around nevi versus melanoma?

> Differentiate observation, inferred cell identity and validated protein marker evidence; mention macrophage and
> T-cell patterns.

| | Observation | Inferred cell identity | Validated protein marker evidence | Source |
|---|---|---|---|---|
| Macrophages | | | | |
| T cells | | | | |
| Other | | | | |

**Answer:**

_…_

---

## Q8. Which spatial questions have already been investigated?

> Look explicitly for neighborhood/distance analyses, deconvolution, spatial ligand-receptor work and pseudotime in
> both the paper and code repository.

| Analysis | Done? | In the paper | In the code | What exactly was asked |
|---|---|---|---|---|
| Neighbourhood / distance | | | | |
| Deconvolution | | | | |
| Spatial ligand–receptor | | | | |
| Pseudotime | | | | |
| Other | | | | |

**Notes:**

_…_

---

## Q9. What are the main limits of this study for new computational work?

> Address cross-sectional sampling (not longitudinal proof of progression), spot-level resolution, patient/slide
> dependence, annotation quality and variation across samples.

- **Cross-sectional sampling:** _…_
- **Spot-level resolution:** _…_
- **Patient / slide dependence:** _…_
- **Annotation quality:** _…_
- **Variation across samples:** _…_
- **Other:** _…_

---

## Q10. Novelty audit: do not redo established results

> Identify the exact figure, table, supplementary analysis or script supporting each published area below. Explain
> what remains unanswered and why a proposed follow-up would be genuinely new rather than a rerun with different
> software.

### Area 1: Differential expression, proliferation and melanocytic programs

- **Evidence in paper/code** (result, samples, method): _…_
- **What remains unanswered:** _…_
- **New question beyond repeating a known gene/program difference:** _…_
- **Why it is new, not a rerun:** _…_

### Area 2: Immune composition, infiltration and spatial proximity

- **Evidence in paper/code** (deconvolution, immune comparisons, distance analyses): _…_
- **What remains unanswered:** _…_
- **What can be tested about spatial organization beyond immune abundance or existing proximity results:** _…_
- **Why it is new, not a rerun:** _…_

### Area 3: Pseudotime, spatial ligand–receptor and protein-level comparisons

- **Evidence in paper/code** (workflow, figures, scripts, validation data): _…_
- **What remains unanswered:** _…_
- **Methodological claim or independent analysis that remains untested:** _…_
- **Why it is new, not a rerun:** _…_

### Novelty statement

_One short paragraph: what our spatial-reasoning project adds that the paper did not do._

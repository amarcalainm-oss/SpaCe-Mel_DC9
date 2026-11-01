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

_…_

**Evidence:**

- _…_

---

## Q2. What biological material was studied, and what is the correct unit of independence?

> Identify tissue states, sampling structure, Visium spots versus specimens/patients, and use of adjacent sections.

**Answer:**

_…_

**Evidence:**

- _…_

---

## Q3. Why did the authors combine Visium with imaging mass cytometry?

> Specify what each modality measures and which claims were supported by RNA versus protein evidence.

**Answer:**

_…_

| Claim | RNA (Visium) | Protein (IMC / IHC / proteomics) | Source |
|---|---|---|---|
| _…_ | | | |

**Evidence:**

- _…_

---

## Q4. How were nevus, melanoma, and other tissue regions identified or annotated?

> Locate the description of histopathology/region labels and establish whether per-spot labels are publicly available.

**Answer:**

_…_

**Are per-spot labels public?** _yes / no — where I looked:_

- _…_

**Evidence:**

- _…_

---

## Q5. What preprocessing and analytical methods did the authors use?

> Include filtering, normalization, cell-type deconvolution, differential expression, immune infiltration, spatial
> analyses, pseudotime and ligand-receptor analysis where applicable. Reference scripts.

| Step | Method / tool | Key settings | Paper section | Script |
|---|---|---|---|---|
| Filtering | | | | |
| Normalization | | | | |
| Cell-type deconvolution | | | | |
| Differential expression | | | | |
| Immune infiltration | | | | |
| Spatial analyses | | | | |
| Pseudotime | | | | |
| Ligand–receptor | | | | |

**Notes:**

_…_

---

## Q6. What are the three most important biological findings?

> For each, give the evidence and figure/table number. Consider proliferation/metabolic adaptation, melanocytic
> programs and microenvironment remodeling.

### Finding 1: _…_

- **What they found:** _…_
- **Evidence:** _…_
- **Figure/table:** _…_

### Finding 2: _…_

- **What they found:** _…_
- **Evidence:** _…_
- **Figure/table:** _…_

### Finding 3: _…_

- **What they found:** _…_
- **Evidence:** _…_
- **Figure/table:** _…_

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

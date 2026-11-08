# Annotation caveats and evidence levels

## Which labels exist

| Label | Available? | Where | Use in this project |
|---|---|---|---|
| Patient / section identity per spot | **Yes** | per-section GEO files (`in_tissue` mask) + Table S1 | `patient_id`, `section_id` in all manifests |
| Clinical data per patient (age, sex, Breslow, stage, PRAME/p16 staining) | **Yes** | Supplementary Table S1 | `manifests/tissue_sections.csv` |
| Lesion type of a whole section ("nevus and melanoma") | Describes every section equally | GEO titles | **not used as a label**: every section contains both |
| Nevus / melanoma / cell type per spot | **No** | authors' deconvolution (not public) | `region_label = "not available"` |
| Published spot maps (Fig. 1G, Supp. Fig. S1E, S4) | Images only, no patient IDs | paper | visual comparison only |
| Protein-level cell identity (IMC) | Not in GEO | Zenodo 15582615, adjacent sections, 9 lesions | not used yet |

## Rules followed in the notebooks
1. No spot or section receives a nevus/melanoma label from GEO text or from our own expression analysis.
2. Expression-defined groupings (e.g. "PRAME detected") are named as such and are never called nevus or melanoma.
3. The unit of independence is the **patient** (B38ex and B38_2 count as one patient), not the spot or the GSM.
4. Visual agreement with a published figure is reported as *approximate*, never as an exact reproduction.

## Evidence levels for immune (and other cell-type) statements

| Level | What it is | Example here | What may be claimed |
|---|---|---|---|
| 1. Single marker RNA | counts of one gene in a spot | CD163, PTPRC, CD3E maps | "transcripts of X are present in this spot's cell mixture" |
| 2. Provisional gene score | combination of a few marker genes, not validated in this dataset | `Tcell_assoc_score_provisional`, `macrophage_assoc_score_provisional` | "higher T-cell-associated RNA signal", not "more T cells" |
| 3. Inferred cell composition | reference-based or deconvolution estimate of cell fractions | paper Fig. 5A/5C, Supp. Fig. S9D (not reproduced here) | "estimated fraction", with the method named |
| 4. Validated cell identity | independent measurement of the cell type, e.g. protein (IMC) | paper Fig. 5B/5D, Supp. Fig. S9B/C | cell identity, on the measured (adjacent) section |

**PTPRC** (CD45) is expressed by all leukocytes. A score combining CD163 with PTPRC is therefore not a macrophage
measure; the old notebook's `macrophage_score` has been removed.

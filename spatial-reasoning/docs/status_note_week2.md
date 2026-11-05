# Status note · Week 2 (2–8 November 2026)

| | |
|---|---|
| Student | Aitor · Spatial reasoning (`spatial-reasoning/`) |

| Deadline | **Sunday 8 November 2026, 22:00 (Spain time)** |

## 1. What changed since last week (1 November)

| Date | Change | Instruction point |
|---|---|---|
| 1–4 Nov | Paper worksheet completed: Q1–Q10 and the novelty audit, with figure/script citations (`docs/paper_worksheet/README.md`) | 1 |
| 3 Nov | Paper's spot QC applied to GSE298774 (> 500 genes, < 30% MT; 0-count spots also fail): **39,483 of 61,734 spots kept**, vs 39,481 in the paper | 2 |
| 4 Nov | QC failure maps for A24, B4 and A16; chart of which tissue-like clusters the filter removes; A24 clustering before vs after filtering; cluster names reworded as provisional ("looks like…") | 2, 3 |
| 4 Nov | Three spatial operations (spots within a radius, distance to a region, neighbourhood fraction) with 21 tests on synthetic examples, plus a demo on A24 | 4 |
| 5 Nov | Initial benchmark: 15 natural-language questions (9 tasks, each asked in two wordings), 14 reference answers computed with the tested operations and checked independently | 5 |
| 5 Nov | Setup only: SNMF (a spatial deconvolution method from our group) installed in an isolated R environment (`snmf/`). Not run on our data yet | – |

## 2. What runs and is supported by evidence

| What | Evidence | Where |
|---|---|---|
| QC filter reproduces the paper | 39,483 spots kept vs 39,481 reported; per-patient retention table | `01_data_exploration/notebooks/03_explore_GSE298774.ipynb`, guide `01_data_exploration/docs/03_GSE298774.md` |
| Where QC removes spots | Maps (A24 1.7%, B4 15.5%, A16 46.7% removed); removed spots are mostly blood-, fat- and dermis-like clusters; melanocytic-like clusters lose 0% | `01_data_exploration/results/GSE298774/qc_failed_spots.png`, `qc_removed_by_cluster.png` |
| A24 clustering after filtering | Most clusters keep ≥ 83% of their spots together; one cluster (T-cell response genes) splits | `clusters_A24_before_after.png` + table in notebook 03 |
| Spatial operations work as specified | 21/21 tests pass (boundary, no neighbours, the spot itself, two sections, wrong inputs); the boundary test fails if the rounding tolerance is removed | `src/space_mel/operations.py`, `tests/test_operations.py` (`.venv\Scripts\python.exe -m pytest`) |
| Real coordinates need care | Touching spots in A24 are 99.8–100.6 µm apart, so r = 100 µm gives most spots 1 neighbour instead of 6; r = 150 µm gives 6 to 90% | `02_spatial_operations/results/A24_neighbour_distances.png`, guide `02_spatial_operations/docs/01_spatial_operations.md` |
| Benchmark reference answers | 14 answers (8 toy grid, 6 A24); toy answers checked by counting spots, A24 answers re-checked with a separate brute-force calculation (all match) | `02_spatial_operations/benchmark/benchmark.csv`, `notebooks/02_benchmark.ipynb`, guide `docs/02_benchmark.md` |

## 3. What remains unresolved

- **No independent nevus/melanoma labels per spot.** The paper's labels are expression-derived and not public. All
  regions used this week are defined by expression (e.g. PRAME > 1.5) and are provisional. Benchmark question B15
  ("distance to the nevus") is marked *awaiting annotation*.
- **The 500-gene QC threshold removes low-RNA tissue** (dermis, fat, blood) much more than the lesion, leaving holes
  around it. It may be too strict for that tissue and for shallow patients (B8, B14 and A17 keep < 900 spots each).
- **Signature enrichment** ("is a gene higher near region X?") is not implemented, so it is not in the benchmark.
- **Real-data examples use one patient (A24)** and one threshold per gene.


## 4. Next proposed correction or test

1. **Most important: independent region labels.** Get a pathologist to
   annotate nevus / melanoma on the H&E? I don't really know how could we get ground truth in this. This unblocks the tumour/nevus questions and any validation.

2. Test a gentler or per-patient QC threshold and check whether it fills the holes in the dermis without keeping
   empty spots.
3. Run the operations and benchmark questions on a second patient (B4) to check they work beyond A24.
4. Then, as the next step of the project: a first test of whether an LLM picks the right operation for each
   benchmark question (not started; not part of this week).

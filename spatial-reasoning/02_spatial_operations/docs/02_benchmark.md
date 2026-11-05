# Stage 2 · Benchmark: questions and reference answers

The first version of the natural-language benchmark (point 5 of Myles's week-2 instructions). It is the "exam" the
LLM will take later: simple spatial questions, each with a recipe saying exactly how the correct answer is
calculated. The correct answers are computed with the **tested operations** (`src/space_mel/operations.py`), never by
an LLM.

| Where | What |
|---|---|
| `02_spatial_operations/benchmark/benchmark.csv` | the 15 questions with all their fields and reference answers |
| `02_spatial_operations/notebooks/02_benchmark.ipynb` | the code that computes every answer (all outputs below come from it) |
| `02_spatial_operations/results/benchmark_*.png` | the two figures below |

## What each question records

| Field | Meaning | Example (B06) |
|---|---|---|
| question | the question as a person would ask it | What is the median distance from the CXCL9-high spots to the nearest PRAME-high spot? |
| data | toy grid or patient | A24 |
| inputs | which spots / region | from: CXCL9-high spots; region: PRAME-high spots |
| operation | which function answers it | `distance_to_region` |
| parameters | numbers and units | µm |
| assumptions | what the labels are based on | PRAME-high = PRAME > 1.5; CXCL9-high = CXCL9 > 2 |
| how | the exact recipe | distance of every CXCL9-high spot to the nearest PRAME-high spot, then the median |
| status | answered / awaiting annotation / operation not implemented | answered |
| reference_answer | the correct answer, computed by code | 100.6 µm |

## The 15 questions

| ID | Type | Question | Status | Reference answer |
|---|---|---|---|---|
| B01 | neighbours | Which spots are within 100 µm of spot r0c0? | answered | r-1c-1, r-1c1, r0c-2, r0c2, r1c-1, r1c1 |
| B02 | neighbours | How many neighbours does the spot 'alone' have within 100 µm? | answered | 0 |
| B03 | neighbours | How many spots are within 300 µm of spot AACTGCCGCTACATCT-1? | answered | 30 |
| B04 | neighbours | Which spots touch spot AACTGCCGCTACATCT-1? | answered | 6 spots (listed in the CSV) |
| B05 | distance | How far is spot r2c4 from region R? | answered | 435.9 µm |
| B06 | distance | What is the median distance from the CXCL9-high spots to the nearest PRAME-high spot? | answered | 100.6 µm |
| B07 | distance | How many CXCL9-high spots are more than 500 µm away from every PRAME-high spot? | answered | 10 (of 281) |
| B08 | distance | How far is spot s1 (section A22) from region {s2} (section A24)? | answered | not defined (NaN): different sections |
| B09 | distance | How far are the CXCL9-high spots from the nevus in A24? | **awaiting annotation** | – |
| B10 | neighbourhood | What fraction of the neighbours of spot r0c0 (within 100 µm) are in category C? | answered | 4/6 = 0.67 |
| B11 | neighbourhood | What percentage of the PRAME-high spots touch at least one CXCL9-high spot? | answered | 12.2% (231 of 1,888) |
| B12 | neighbourhood | How many PRAME-high spots have at least half of their touching spots CXCL9-high? | answered | 95 (of 1,888) |
| B13 | neighbourhood | What share of the spots along the melanoma border are CXCL9-high? | **awaiting annotation** | – |
| B14 | signature enrichment | Is CXCL9 higher in spots within 200 µm of the PRAME-high spots than in spots further away? | **operation not implemented** | – |
| B15 | signature enrichment | Is CXCL9 higher next to the nevus than next to the melanoma? | **awaiting annotation; operation not implemented** | – |

- **11 answered** (5 on the toy grid, 6 on A24), **2 awaiting annotation** (need real nevus/melanoma labels),
  **2 need signature enrichment**, which is not built yet (one of them also needs labels).
- Several questions ask the same kind of thing in different words ("within 100 µm", "touch", "neighbours"), to test
  later whether the LLM understands the meaning, not just the keywords.

## The data

**Toy grid:** a small drawn piece of the Visium grid (spots 100 µm apart) plus one isolated spot. Answers can be
checked by eye. Region **R** and category **C** are the orange rings.

![toy grid](../results/benchmark_toy_grid.png)

**A24:** the real patient (filtered spots). Two sets, each defined by **one gene** (expression only; no claim that
they are tumour or immune cells):

- **PRAME-high** = PRAME > 1.5 → 1,888 spots
- **CXCL9-high** = CXCL9 > 2 → 281 spots (91 are both)

![A24 sets](../results/benchmark_A24_sets.png)

**One rule for all questions:** "touching" = within **150 µm** (between the first and second ring of the grid; with
real coordinates, 100 µm misses neighbours, see guide 01).

Real-data answers are **defensible** because each set is exactly what its name says (spots above a gene threshold).
They would *not* be defensible if the question said "melanoma" or "T cells": those are B09, B13 and B15.

## How each answer is computed

Each block is the code from the notebook, followed by the output it gave. Setup (in the notebook): `toy` and
`spots` are the spots tables of the toy grid and A24; `R`, `C`, `prame_high`, `cxcl9_high` are True/False per spot;
`TOUCHING_UM = 150`.

### Neighbours → `spots_within_radius`

**B01** · Which spots are within 100 µm of spot r0c0? (toy)
```python
nb = spots_within_radius(toy, "r0c0", 100)
answers["B01"] = ", ".join(sorted(nb))
print(len(nb), "spots:", answers["B01"])
```
```
6 spots: r-1c-1, r-1c1, r0c-2, r0c2, r1c-1, r1c1
```

**B02** · How many neighbours does the spot 'alone' have within 100 µm? (toy)
```python
nb = spots_within_radius(toy, "alone", 100)
answers["B02"] = len(nb)
```
```
0
```

**B03** · How many spots are within 300 µm of spot AACTGCCGCTACATCT-1? (A24)
```python
nb = spots_within_radius(spots, "AACTGCCGCTACATCT-1", 300)
answers["B03"] = len(nb)
```
```
30
```

**B04** · Which spots touch spot AACTGCCGCTACATCT-1? (A24)
```python
nb = spots_within_radius(spots, "AACTGCCGCTACATCT-1", TOUCHING_UM)
answers["B04"] = ", ".join(sorted(nb))
```
```
6 spots: ATGTTCACTGCAATCC-1, CCGCTCGGTCACAGTC-1, CGGTAGCAGTCATACT-1, CGTGGCGATTGCCACT-1, GCAGGTCAATAGCGAC-1, GGCGTGAGGAGCCGAA-1
```

### Distance to a region → `distance_to_region`

**B05** · How far is spot r2c4 from region R? (toy)
```python
d = distance_to_region(toy, R)
answers["B05"] = f"{d['r2c4']:.1f} µm"
```
```
435.9 µm
```
Check by hand: the nearest R spot is r-1c-3, 350 µm across and 259.8 µm down → √(350² + 259.8²) = 435.9 µm.

**B06** · What is the median distance from the CXCL9-high spots to the nearest PRAME-high spot? (A24)
```python
d = distance_to_region(spots, prame_high)          # distance of every spot to the nearest PRAME-high spot
d_cxcl9 = d[cxcl9_high]                            # keep only the CXCL9-high spots
answers["B06"] = f"{d_cxcl9.median():.1f} µm"
```
```
100.6 µm (over 281 CXCL9-high spots)
```
So the typical CXCL9-high spot touches a PRAME-high spot (91 of them are PRAME-high themselves, distance 0).

**B07** · How many CXCL9-high spots are more than 500 µm away from every PRAME-high spot? (A24)
```python
answers["B07"] = int((d_cxcl9 > 500).sum())        # reuses d_cxcl9 from B06
```
```
10 of 281
```

**B08** · How far is spot s1 (section A22) from region {s2} (section A24)? (two-section toy)
```python
two = pd.DataFrame({"x_um": [0.0, 10.0], "y_um": [0.0, 0.0], "section": ["A22", "A24"]}, index=["s1", "s2"])
d = distance_to_region(two, pd.Series([False, True], index=two.index))
```
```
{'s1': nan, 's2': 0.0} -> not defined (NaN): different sections
```
s1 is only 10 µm from s2, but they are in different tissue sections, so they never connect.

### Neighbourhood composition → `neighbourhood_fraction`

**B10** · What fraction of the neighbours of spot r0c0 (within 100 µm) are in category C? (toy)
```python
f = neighbourhood_fraction(toy, C, 100)
row = f.loc["r0c0"]
answers["B10"] = f"{int(row.n_in_category)}/{int(row.n_neighbours)} = {row.fraction:.2f}"
```
```
4/6 = 0.67
```

**B11** · What percentage of the PRAME-high spots touch at least one CXCL9-high spot? (A24)
```python
f = neighbourhood_fraction(spots, cxcl9_high, TOUCHING_UM)   # for every spot: CXCL9-high neighbours
f_prame = f[prame_high]                                       # keep only the PRAME-high spots
answers["B11"] = f"{100 * (f_prame.n_in_category >= 1).mean():.1f}%"
```
```
12.2% (231 of 1888 PRAME-high spots)
```

**B12** · How many PRAME-high spots have at least half of their touching spots CXCL9-high? (A24)
```python
answers["B12"] = int((f_prame.fraction >= 0.5).sum())        # reuses f_prame from B11
```
```
95 of 1888
```

## How the answers were checked

- **Toy answers** were worked out by hand (B01, B02, B05, B08, B10), and the same cases are in the automatic tests.
- **A24 answers** (B03, B04, B06, B07, B11, B12) were recomputed with a separate brute-force calculation (all
  pairwise distances with plain numpy, not using the operations code). All six match exactly.

## Not answered yet

- **B09, B13 (awaiting annotation):** they need a nevus or melanoma label for every spot. Our only labels are
  expression thresholds, which can't stand in for "nevus" or "melanoma".
- **B14, B15 (signature enrichment):** comparing a gene between "near" and "far" spots needs a fourth operation and a
  statistical test, which were left for later so as not to broaden the project this week. B15 also needs labels.

## Caveats

- One patient (A24) and one threshold per gene: other thresholds give other numbers. The benchmark tests the
  *calculation*, not biology.
- The questions are simple on purpose; harder ones (combining several operations, comparing patients) come later.

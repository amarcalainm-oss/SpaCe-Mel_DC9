# 00 · Concepts behind the exploration notebooks

This guide explains, in plain language, everything that the four notebooks in `01_data_exploration/` have in
common. The dataset guides (`01_GSE316760.md` … `04_GSE221390.md`) focus on what is specific to each dataset and
refer back here for the concepts.

**How to use the guides:** open the notebook and its guide side by side; section numbers match
(notebook section 5 = "5. Coordinate units" in the guide).

---

## 1. What Visium measures

10x Genomics **Visium** is a spatial transcriptomics technology: it measures which genes are active **and where**.

1. A thin tissue section (5–10 µm thick) is stained with **H&E** (haematoxylin = nuclei in purple, eosin =
   cytoplasm and matrix in pink) and photographed.
2. The tissue sits on a **capture area** with a hexagonal grid of **spots**: each spot is **55 µm** wide and spot
   centres are **100 µm** apart. A 6.5 × 6.5 mm capture area has 4,992 spots; an 11 × 11 mm one has 14,336.
3. Each spot has a **barcode** (a 16-letter DNA code, e.g. `AAACAAGTATCTCCCA-1`) that identifies its position.
   RNA (or probes bound to it) from the tissue above is tagged with that barcode.
4. Everything is sequenced and, for each spot, the molecules of each gene are counted → **count matrix**.

**Important:** a 55 µm spot covers **several cells** (roughly 1–10). A spot is not a cell, it is a mixture. If a
spot expresses melanoma genes *and* macrophage genes, both cell types may be underneath.

### Variants that appear in our datasets

| Term | Meaning |
|---|---|
| **FFPE** | Tissue fixed in formalin and embedded in paraffin (the standard hospital archive format). The RNA is degraded, so **probes** are used. |
| **Probe panel** | Instead of reading all RNA, probes designed for specific genes are used. The panel fixes which genes can be measured: **v1 = 17,943 genes** (no mitochondrial genes), **v2 = 18,085 genes** (with 11 `MT-` genes), and a **37,082**-gene panel in GSE298774. |
| **CytAssist** | An instrument that transfers the probes from an ordinary glass slide (where the tissue is) onto the Visium capture area. It lets researchers choose which 6.5 or 11 mm region of a large section is analysed. |
| **Space Ranger** | 10x's software that turns sequencing data into the matrix and positions. Different versions (2.0, 2.1, 3.0) store some numbers differently (see "Coordinate units"). |

---

## 2. Which files GEO provides and what each one means

GEO (Gene Expression Omnibus) is NCBI's public repository. Authors upload Space Ranger's output, but GEO
**flattens the folders** and prefixes every file: `GSM9459774_mel2_tissue_positions.csv.gz`.

| File | Content |
|---|---|
| `filtered_feature_bc_matrix.h5` | The count matrix in a single file (HDF5 format). |
| `matrix.mtx.gz` + `barcodes.tsv.gz` + `features.tsv.gz` | The same matrix in three files: the numbers ("Matrix Market" format, stores only non-zeros), the list of spots (columns) and the list of genes (rows). |
| `tissue_positions.csv` | One row per spot: `barcode`, `in_tissue` (1 = under tissue, 0 = on bare glass), `array_row`/`array_col` (grid position), `pxl_row_in_fullres`/`pxl_col_in_fullres` (position in pixels of the original photo). |
| `scalefactors_json.json` | Factors to go from the original photo to the downscaled ones (`tissue_hires_scalef`, `tissue_lowres_scalef`) and sizes in pixels (`spot_diameter_fullres`, `fiducial_diameter_fullres`). |
| `tissue_hires_image.png` / `tissue_lowres_image.png` | The downscaled H&E photo (~2000 px and ~600 px wide). The full-resolution original is **not** on GEO. |
| `aligned_fiducials.jpg`, `detected_tissue_image.jpg` | Space Ranger control images: the alignment frame and which areas it detected as tissue. |
| `series_matrix.txt.gz` | GEO metadata: title, protocol and processing of each sample. Read with `read_series_matrix`. |

---

## 3. How we load the data (code in `src/space_mel/`)

| Function | What it does |
|---|---|
| `io.load_visium(files_dir, prefix, out_dir, library_id)` | Copies and decompresses one sample's files into `data/processed/visium/…` with the folder layout Squidpy expects (`spatial/tissue_positions.csv`, …) and loads it with `squidpy.read.visium`. Files in `data/raw` are never modified. With `in_tissue_only=True` it keeps only spots with `in_tissue == 1`. |
| `io.load_visium_without_images(…)` | For GSE221390, which has no positions: recovers each spot's position from its barcode (see guide 04). |
| `io.read_series_matrix(path)` | Reads GEO metadata into a table. |
| `spatial.add_spatial_um` / `units_table` | Converts coordinates to micrometres (see section 5). |

---

## 4. The AnnData object

Scanpy and Squidpy keep everything in an **AnnData** object (`adata`). Think of it as a spreadsheet with
attachments:

```
              genes (var) →
spots    ┌──────────────────────┐
(obs)    │   X: expression      │   obs:  table per spot (in_tissue, array_row, QC, cluster…)
  ↓      │   matrix             │   var:  table per gene (Ensembl ID, type…)
         └──────────────────────┘   obsm["spatial"]:    (x, y) position of each spot, in pixels
                                     obsm["spatial_um"]: the same position in µm (added by us)
                                     uns["spatial"]:     images, scale factors, metadata
                                     layers["counts"]:   original counts (saved before normalising)
```

- `adata.n_obs` = number of spots, `adata.n_vars` = number of genes.
- The matrix is **sparse**: it only stores non-zero values, because most genes are not detected in each spot.
  "19% non-zero" means 81% of the table is zeros.
- Counts are **integers**: the number of molecules (UMIs) detected. We check this because non-integer values would
  mean someone had already normalised the data.

---

## 5. Coordinate units: pixels and micrometres

Positions come in **pixels of the original photo**, but the project's questions are about real distances ("how
many µm is the immune infiltrate from the tumour?"). So we need the scale: how many µm one pixel represents.

- **Reliable method (the one we use): the grid.** Neighbouring spot centres are always 100 µm apart. We measure
  that distance in pixels in each sample: `µm per pixel = 100 / neighbour distance (px)`.
- **Unreliable method: `spot_diameter_fullres`.** Space Ranger stores a spot diameter in pixels, but defines it
  differently across versions: in 2.0.1 it corresponds to a 65 µm spot, in 3.0 to a 70 µm one. Using it gives
  ~7% errors. Each notebook compares it only as a check.
- Each sample was photographed at a different scale (0.23–0.39 µm/px), so **never compare pixel distances
  between samples**. That is why we store `obsm["spatial_um"]`.
- Extra check: fitting the full grid → pixel transformation agrees with the grid method within 0.5%.

---

## 6. Quality control (QC)

Computed with `sc.pp.calculate_qc_metrics`:

| Metric | What it is | How to read it |
|---|---|---|
| `total_counts` | Molecules detected in the spot | Low: little tissue, edges, damaged or necrotic areas. Very high: very cellular areas. |
| `n_genes_by_counts` | How many different genes are detected | Goes hand in hand with `total_counts`. |
| `pct_counts_mt` | % of counts from mitochondrial (`MT-`) genes | High (> 20–30%) usually means damaged cells. Only available if the panel includes `MT-` genes (v2 and the 37k panel, not v1). |

**Histograms:** how values are distributed across spots. **Spatial QC maps:** if low values cluster along an edge
or in one area, it is usually a technical issue or poor tissue, not biology.

---

## 7. Normalisation

Spots capture different amounts of RNA, so raw counts cannot be compared directly. We do the standard Scanpy steps:

1. `normalize_total(target_sum=1e4)`: each spot is rescaled as if it had 10,000 counts in total.
2. `log1p`: log of (1 + value). Compresses very high values so a few genes do not dominate.

Marker map values are on this scale (log of normalised counts): 0 = not detected, ~1–2 = moderate, > 3 = high.
Original counts stay in `layers["counts"]`.

---

## 8. Marker genes

A **marker** is a gene expressed almost only in one cell type, so its presence suggests that cell type in the spot.

| Gene | Marks | Notes |
|---|---|---|
| `MLANA`, `PMEL`, `TYR`, `TYRP1`, `TRPM1` | Melanocytes and **differentiated** melanoma (pigment-producing) | Also in nevi (benign moles). |
| `SOX10`, `MITF` | Melanocytic lineage | `SOX10` stays on in melanomas that lose `MLANA`/`PMEL` (dedifferentiated). |
| `PRAME` | **Melanoma vs nevus** | Used by pathologists: high in most melanomas, low in nevi. Not every melanoma expresses it. |
| `MKI67` | Proliferation (dividing cells) | |
| `PTPRC` (CD45) | Any immune cell | |
| `CD3E` / `CD8A` | T cells / cytotoxic T cells | The cells that attack the tumour; the target of anti-PD1 immunotherapy. |
| `CD68`, `CD163` | Macrophages (`CD163`: "M2" macrophages, often pro-tumour) | |
| `CD74`, `HLA-DRA` | Antigen presentation (MHC-II) | Macrophages, dendritic cells, B cells; tumour cells also express them under inflammation (IFN-γ). |
| `IGKC`, `IGHG1` | Plasma cells (antibody-producing) | |
| `COL1A1`, `COL1A2`, `DCN` | Fibroblasts / stroma (connective tissue) | |
| `KRT14`, `KRT5` | Basal epidermis | `KRT1`, `KRT10`, `LOR`, `FLG`: upper epidermal layers. |
| `KRTAP…`, `KRT71`, `KRT31` | Hair follicle | |
| `DCD`, `SCGB2A2`, `MUCL1`, `PIP` | Sweat glands | |
| `FADS2`, `FASN`, `KRT79` | Sebaceous glands | |
| `MPZ`, `S100B` | Nerves (Schwann cells) | `S100B` is also expressed by melanoma. |
| `ACTA2`, `MYH11`, `DES` | Smooth muscle (vessels, hair erector muscle) | |
| `NDRG1`, `SLC2A1`, `BNIP3L`, `VEGFA`, `ERO1A` | **Hypoxia** (lack of oxygen) | Typical of the inside of large tumours. |
| `CCL21`, `LYVE1`, `PROX1` | Lymphatic vessels | |

**How to read a marker map:** each dot is a spot at its position; colour is normalised expression. Look for
**patterns**: a whole region in bright colour (e.g. tumour), a band (epidermis), patches (immune aggregates).
An isolated bright spot is usually noise. Each panel has its own colour scale, so check the numbers on the bar.

---

## 9. Clustering: grouping similar spots

There are no region labels, so we let the data group spots with similar expression:

1. **Highly variable genes (HVG):** keep the 2,000 genes that vary most between spots (the rest is mostly noise).
2. **PCA:** summarises those 2,000 genes into 30 "axes" that capture most of the variation.
3. **Neighbour graph:** each spot is linked to the spots most similar to it (in expression, **not** in space).
4. **Leiden:** an algorithm that finds communities in that graph → **clusters** (0, 1, 2…). The `resolution` (we
   use 0.5) controls how many: higher = more, smaller clusters.
5. **UMAP:** a 2D drawing of the graph for visualisation only. Distances in a UMAP have no precise meaning.

Then, to **interpret** each cluster:

- **Spatial cluster map:** does the cluster form a continuous region (good sign) or is it scattered?
- **Matrixplot:** a cluster × marker colour table. With `standard_scale="var"` each gene is rescaled 0–1 across
  clusters, so it shows **in which cluster each gene is highest**, not whether the level is high in absolute terms.
- **rank_genes_groups** (Wilcoxon test): the genes most **over-expressed** in each cluster vs all other spots.
  Reading the top 8 and comparing with the marker table lets us name the cluster.

**Caution:** a cluster is not a cell type. It is a group of spots (cell mixtures) with similar profiles. The labels
we propose ("tumour", "stroma", "immune") are **hypotheses** to be validated with the H&E image, the literature and
Myles. Also, clusters are computed **per sample**: cluster 3 in one sample has nothing to do with cluster 3 in
another.

---

## 10. What is saved

Each notebook saves one `.h5ad` per sample in `data/processed/` (not uploaded to GitHub): counts in
`layers["counts"]`, normalised expression in `X`, QC metrics and clusters in `obs`, and micrometre coordinates in
`obsm["spatial_um"]`. The next project stage (`02_spatial_operations/`) will start from these files.

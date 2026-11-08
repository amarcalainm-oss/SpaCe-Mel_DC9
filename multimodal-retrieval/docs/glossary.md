# Glossary

Plain-language definitions of the terms used in this folder.

| Term | Meaning |
|---|---|
| **H&E** | Haematoxylin and eosin, the standard tissue stain. Haematoxylin colours cell nuclei blue-purple; eosin colours cytoplasm and collagen pink. Pathologists diagnose most tumours from H&E. |
| **Nevus** | A benign (non-cancerous) mole made of melanocytes. In this study the nevus parts are mostly *intradermal* (in the dermis). |
| **Melanoma** | A malignant (cancerous) tumour of melanocytes. In this dataset each lesion contains a nevus part next to a melanoma part. |
| **Melanocyte** | The pigment-producing cell of the skin; both nevus and melanoma cells are melanocytic. |
| **Epidermis / dermis** | The outer layer of the skin (made of keratinocytes) / the connective-tissue layer below it (fibroblasts, collagen, vessels, immune cells). |
| **FFPE** | Formalin-fixed, paraffin-embedded: how the tissue blocks were preserved (paper, Methods). |
| **Spatial transcriptomics** | Measuring gene expression (RNA) while keeping the position in the tissue. |
| **10x Visium** | The spatial transcriptomics technology used. A glass slide area is covered with a grid of capture spots; RNA from the tissue above each spot is captured and sequenced. |
| **Capture area** | The part of a Visium slide covered by spots: 6.5 × 6.5 mm (4,992 spots) or 11 × 11 mm (14,336 spots). In GSE298774 one capture area = one GEO sample (GSM). |
| **CytAssist** | 10x instrument that transfers the RNA from a standard tissue slide to the Visium capture area. Used in this study (paper, Methods). |
| **Spot** | One capture position, 55 µm in diameter, 100 µm centre-to-centre. Its measurement is the sum of the RNA of all cells above it (the paper states 5–10 cells). **A spot is not a cell.** |
| **Barcode** | The DNA sequence that identifies a spot within a capture area. The same barcodes are used on every capture area, so a spot is uniquely identified only by capture area + barcode (`spot_uid`). |
| **UMI / counts** | Unique molecular identifier: each counted RNA molecule. "Counts" of a gene in a spot = number of its molecules detected there. |
| **Count matrix** | Table of counts: spots × genes. Stored in GEO as `matrix.mtx` + `barcodes.tsv` + `features.tsv`. Most entries are zero (sparse). |
| **Gene panel / probe set** | Visium for FFPE measures a predefined set of genes with probes. Two panels occur in this dataset (37,082 and 18,085 features). |
| **Mitochondrial % (pct_mt)** | Share of a spot's counts from genes encoded in mitochondria (`MT-` genes). Commonly used as a quality indicator. |
| **QC (quality control)** | Removing or flagging spots with too little or unreliable signal. Here: > 500 genes and < 30 % mitochondrial counts (paper, Methods). |
| **Normalisation** | Correcting counts for how much RNA each spot captured, so spots can be compared. Here: counts / spot total × 10,000, then log(1 + x). |
| **Full-resolution pixels** | The pixel coordinates of spots in the original microscope H&E image. That image is **not** in GEO; GEO has down-scaled copies. |
| **hires / lowres image** | Down-scaled copies of the H&E image (longest side ~2000 px / ~600 px). Pixel = full-res pixel × scale factor. |
| **Scale factor** | Number in `scalefactors_json.json` that converts full-resolution pixels to the pixels of a distributed image. |
| **Marker gene** | A gene typically expressed by one cell type (e.g. CD3E for T cells). Its RNA in a spot suggests, but does not prove, that cell type is present. |
| **Gene score** | A combined value from several marker genes. Provisional unless validated. |
| **Deconvolution** | Statistical estimation of which cell types / expression programmes are mixed in each spot. The paper used STdeconvolve (15 profiles). |
| **IMC (imaging mass cytometry)** | Measures ~40 proteins at 1 µm resolution on a tissue section. The paper used it on adjacent sections of 9 lesions to confirm immune cell types. Not in GEO. |
| **PRAME, SOX10, p16** | Immunohistochemistry stains the pathologist used: SOX10 marks melanocytic cells, PRAME is typically higher in melanoma, p16 relates to senescence (paper, Fig. 1B–E). |
| **Patch** | A small square cut out of the H&E image, here centred on a spot. |
| **Manifest** | A table listing every sample / section / spot with its identifiers and properties. |

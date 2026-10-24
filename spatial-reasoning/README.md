# Spatial reasoning in melanoma

**Evaluating Spatially Grounded Natural-Language Reasoning in Melanoma Transcriptomics**
(Aitor, internal student, TECNUN 2026-27)

Can an LLM accurately answer spatially complex questions about melanoma tissue organization when its answers are
grounded in quantitative spatial analysis? E.g. *which regions show high immune gene expression near melanoma
regions, and how far are immune-enriched regions from the tumour?*

## Contents

The work is organised in numbered **stage folders**; everything shared by all stages lives at this level.

| Path | What |
|---|---|
| `01_data_exploration/` | **Stage 1.** Exploring the four Visium datasets with Scanpy/Squidpy |
| ↳ `notebooks/0X_explore_<GSE>.ipynb` | One notebook per dataset: matrices, metadata, images, coordinate units, QC, markers, clusters |
| ↳ `docs/` | **Plain-language guides**: `00_concepts.md` (Visium, AnnData, QC, clustering, markers) and one guide per dataset explaining what was done and how to interpret it |
| ↳ `results/<GSE>/` | Figures from each notebook |
| `src/space_mel/` | Shared code. `io.py`: loading GEO Visium samples (also patient-split and image-less ones) and GEO metadata; `spatial.py`: pixel → µm conversion |
| `docs/datasets.md` | The 10x Visium datasets (GEO), their quirks, and how to convert coordinates to µm |
| `scripts/download_data.ps1` | Downloads the GEO datasets (resumable) |
| `data/` | Raw and processed data (not in git) |

Planned next stages: `02_spatial_operations/` (neighbourhoods, distances, enrichment, spatial filtering) and
`03_llm_reasoning/` (LLM selects, runs and explains the operations).

## Setup

```powershell
python -m pip install --user uv
python -m uv sync                                    # creates .venv with scanpy, squidpy, jupyter
powershell -ExecutionPolicy Bypass -File .\scripts\download_data.ps1   # ~3.3 GB into data/raw (not in git)
.\.venv\Scripts\nbstripout.exe --install --attributes .gitattributes # commit notebooks without outputs
```

Data is not stored in git; a backup lives on the team Google Drive.

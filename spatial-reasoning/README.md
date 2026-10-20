# Spatial reasoning in melanoma

**Evaluating Spatially Grounded Natural-Language Reasoning in Melanoma Transcriptomics**
(Aitor, internal student, TECNUN 2026-27)

Can an LLM accurately answer spatially complex questions about melanoma tissue organization when its answers are
grounded in quantitative spatial analysis? E.g. *which regions show high immune gene expression near melanoma
regions, and how far are immune-enriched regions from the tumour?*

## Contents

| Path | What |
|---|---|
| `docs/datasets.md` | The 10x Visium datasets (GEO), their quirks, and how to convert coordinates to µm |
| `notebooks/01_explore_GSE316760.ipynb` | First exploration: matrices, metadata, images, units, QC, markers, clusters |
| `results/01_GSE316760/` | Figures from that notebook |
| `src/space_mel/io.py` | `load_visium()`: loads a GEO Visium sample with Squidpy |
| `scripts/download_data.ps1` | Downloads the GEO datasets (resumable) |

## Setup

```powershell
python -m pip install --user uv
python -m uv sync                                    # creates .venv with scanpy, squidpy, jupyter
powershell -ExecutionPolicy Bypass -File .\scripts\download_data.ps1   # ~3.3 GB into data/raw (not in git)
.\.venv\Scripts\nbstripout.exe --install --attributes .gitattributes # commit notebooks without outputs
```

Data is not stored in git; a backup lives on the team Google Drive.

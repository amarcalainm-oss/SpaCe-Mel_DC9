# Spatial reasoning in melanoma: project notes

Aitor's internal-student project (TECNUN 2026-27), Angel Rubio's group, supervised day to day by
Myles Tan. Coordination happens on Slack (#spatial-reasoning, #data).

**Provisional title:** Evaluating Spatially Grounded Natural-Language Reasoning in Melanoma Transcriptomics.

**Research question:** Can an LLM accurately answer spatially complex questions about melanoma tissue
organization when its answers are grounded in quantitative spatial analysis?

Target questions:
1. Which regions show high immune-associated gene expression near melanoma-associated regions?
2. Where are immune-enriched regions concentrated, and how far are they from tumour regions?

Plan:
1. Build reusable spatial operations (`src/`): neighbourhood identification, distance calculation,
   region enrichment, spatially constrained filtering.
2. Let an LLM pick the right operations, run them, and explain the evidence.

Key references: Squidpy, GeneGPT, ChatSpatial, SpatialBench (PDFs in Drive `01_papers/`).

## Layout

- Git repo: the team monorepo https://github.com/amarcalainm-oss/SpaCe-Mel_DC9, cloned at
  `C:\TECNUN_LOCAL_MSI\Space-MEL`. Aitor's part is **this folder, `spatial-reasoning/`**; the other top-level
  entries (`app`, `shared`, `multimodal-retrieval`, ...) belong to the wider team. Don't change them unless asked.
- `data/raw/<GSE>/` – GEO downloads (gitignored). `files/` has the extracted files, `download/` the archives.
- `data/processed/` – AnnData `.h5ad` files we build (gitignored).
- `notebooks/` – exploration. `src/` – reusable code. `scripts/` – one-off utilities (e.g. download).
- `results/` – figures and tables. `docs/` – notes, including `docs/datasets.md` (read it before touching data).
- Google Drive (`G:\Mi unidad\TECNUN 2026-27\Alumno_Interno`) holds only data backups, papers and slides.
  Code lives here and will move to GitHub.

## Environment

- Managed with `uv` (installed as `python -m uv`): dependencies in `pyproject.toml` / `uv.lock`, environment in `.venv`.
- Add a package: `python -m uv add <pkg>`. Recreate the environment: `python -m uv sync`.
- Run things with `.venv\Scripts\python.exe`. In VS Code the notebook kernel is registered as **"Space-MEL (.venv)"**
  (Select Kernel → Jupyter Kernel…); the interpreter itself shows as `space-mel`. `.vscode/settings.json` makes it the default.
- Notebooks are committed **without outputs** (nbstripout git filter, set up in `.gitattributes`; the filter
  config lives in `.git/config`, so re-run `.venv\Scripts\nbstripout.exe --install --attributes .gitattributes`
  after a fresh clone). Local notebooks keep their outputs; key figures go to `results/` as PNG.
- `src/space_mel/io.py` has `load_visium()`, which rebuilds a GEO-flattened Visium sample into the Space Ranger
  layout and loads it with `squidpy.read.visium`.

## Progress

- `notebooks/01_explore_GSE316760.ipynb` – first exploration (units, QC, markers, clusters); outputs in
  `results/01_GSE316760/`, AnnData in `data/processed/GSE316760_{mel2,mel3}.h5ad`.

## Conventions

- Python with scanpy + squidpy. Keep spatial distances in micrometres (see `docs/datasets.md`).
- Never modify files in `data/raw/`. Write derived data to `data/processed/`.
- Aitor is new to Claude Code: explain what you're doing and why, in plain terms.

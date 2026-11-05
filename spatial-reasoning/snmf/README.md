# SNMF environment

An isolated R setup for running **SNMF** (Alonso, Ochoa & Rubio, Tecnun), a reference-free,
spatially regularised deconvolution method: <https://github.com/ML4BM-Lab/SNMF>.
The plan is to compare it with STdeconvolve on the nevus/melanoma Visium data (GSE298774).

## What is isolated, and how

- **renv** gives this folder its own R package library (`renv/library/`, gitignored). Nothing is
  installed into your normal R library, so other R projects are unaffected. Delete this folder and
  it is all gone.
- R itself is the system install (`C:\Program Files\R\R-4.5.0`). Nothing is on PATH; call it by full path.
- **torch (GPU)** is the CUDA 12.8 prebuilt build from `torch-cdn.mlverse.org`. It ships its own
  CUDA/cuDNN libraries inside the package, so no system-wide CUDA toolkit was installed. It only
  needs the NVIDIA driver.
- `external/SNMF/` is the upstream source code, cloned from GitHub (gitignored, not ours).
  Installed version: SNMF 0.0.1.1, commit `65422e9` (2026-11-05).
- Disk use: about 7 GB in `renv/library/`, almost all of it torch's CUDA libraries.

## Installation notes (2026-11-05)

- **Windows blocked torch's GPU library.** The CUDA 12.8 torch bundle ships an old copy of the Windows
  system file `bcrypt.dll` (from Windows Server 2022) in `torch/lib/`. Windows Code Integrity refuses to
  load an outdated system file from outside `System32` ("Una directiva de Control de aplicaciones
  bloqueó este archivo", event 3077). Then `lantern.dll`, which needs it, fails too. Fix: rename the
  bundled copy so torch falls back to the system's `bcrypt.dll`:
  `renv/library/windows/R-4.5/x86_64-w64-mingw32/torch/lib/bcrypt.dll` → `bcrypt.dll.blocked-by-windows`.
  This changes no security settings. Redo it after reinstalling torch.
- **renv intercepts `install.packages()`** and may reuse its cached CPU-only torch. Use
  `utils::install.packages()` for the GPU build.
- **`snmf()$H` is not proportions.** It returns the raw k × spots matrix. The function computes
  the per-spot proportions (`H %*% S`, normalised so each spot sums to 1) but discards them. To compute them: `P <- as.matrix(res$H %*% S); P <- t(P) / colSums(P)` (spots × k).
- **Upstream test `tests/installed-dispatch.R`** passes its CPU checks and its GPU run of the installed
  package, then fails at its last step. That step rebuilds SNMF's functions outside the package to compare
  against the developers' scripts (base `t()` doesn't dispatch there), so it doesn't affect normal use.
  `tests/load-data.R` passes.
- **Speed check** on the bundled TNBC toy data (100 genes × 2,500 spots, k = 5, 300 iterations, 1 start):
  GPU 21 s, CPU 30 s. On data this small the GPU barely helps, as the paper also reports (1.2–1.7×).
  To force CPU, hide the GPU: `CUDA_VISIBLE_DEVICES=-1`.

## Using it

Any R session started **from this folder** picks up the environment automatically (`.Rprofile` runs
`renv/activate.R`):

```bash
cd spatial-reasoning/snmf
"/c/Program Files/R/R-4.5.0/bin/Rscript.exe" -e "library(SNMF); torch::cuda_is_available()"
```

In RStudio, open this folder as the project.

## Rebuilding from scratch

```r
renv::restore()   # reinstalls the CRAN packages listed in renv.lock
```

`renv.lock` lists SNMF as a local package and records torch's CRAN (CPU-only) source, so restore can't
rebuild either one. After a restore, reinstall the GPU build of torch (then redo the `bcrypt.dll`
rename above) and SNMF:

```r
utils::install.packages("torch", lib = .libPaths()[1], type = "binary",
  repos = "https://torch-cdn.mlverse.org/packages/cu128/0.17.0/")
# git clone https://github.com/ML4BM-Lab/SNMF.git external/SNMF   (first, from the shell)
utils::install.packages("external/SNMF", repos = NULL, type = "source", lib = .libPaths()[1])
```

"""Export the small data tables the Week 2 slides draw (spot positions, QC flags, A24 regions).

Run from the project root:  .venv\\Scripts\\python.exe presentation_week2\\make_figure_data.py
Embeds the data in presentation_week2/slides.html (between the FIGDATA markers). Nothing here changes data/ or results/.
The benchmark answers drawn on the slides are recomputed with the tested operations and checked against
02_spatial_operations/benchmark/benchmark.csv, so the slides cannot drift from the benchmark table.
"""

import json
import sys
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd
import scanpy as sc
from scipy.spatial import cKDTree

ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "pyproject.toml").exists())
sys.path.insert(0, str(ROOT / "src"))
from space_mel.io import load_visium  # noqa: E402
from space_mel.operations import distance_to_region, neighbourhood_fraction, spots_table, spots_within_radius  # noqa: E402
from space_mel.spatial import um_per_px  # noqa: E402

GSE = "GSE298774"
RAW = ROOT / "data/raw" / GSE / "files"
PROCESSED = ROOT / "data/processed"
SLIDES = ROOT / "presentation_week2/slides.html"
QC_EXAMPLES = {"A24": "GSM9022967", "B4": "GSM9022970", "A16": "GSM9022966"}
X, Y = "AACTGCCGCTACATCT-1", "GACGCTCGAGGAGTGC-1"   # the two A24 spots used in the benchmark
data = {}

# 1. QC maps: every in-tissue spot before filtering, with the rule it fails (paper thresholds).
data["qc_maps"] = {}
for pid, gsm in QC_EXAMPLES.items():
    a = load_visium(RAW, f"{gsm}_{pid}", PROCESSED / f"visium/{GSE}_{pid}", library_id=pid, in_tissue_only=True)
    a.var["mt"] = a.var_names.str.startswith("MT-")
    sc.pp.calculate_qc_metrics(a, qc_vars=["mt"], inplace=True, percent_top=None)
    fail = np.select([a.obs.total_counts == 0, a.obs.n_genes_by_counts <= 500, a.obs.pct_counts_mt >= 30],
                     ["zero", "genes", "mt"], default="")
    xy = a.obsm["spatial"] * um_per_px(a)   # image orientation, same as the notebook figures
    xy -= xy.min(axis=0)
    data["qc_maps"][pid] = {
        "x": np.round(xy[:, 0]).astype(int).tolist(), "y": np.round(xy[:, 1]).astype(int).tolist(),
        "fail": [{"": 0, "genes": 1, "mt": 2, "zero": 3}[f] for f in fail],
        "n": int(a.n_obs), "removed": int((fail != "").sum()),
    }
    print(pid, a.n_obs, "spots,", (fail != "").sum(), "fail QC")

# 2. Shared capture area GSM9022967: which spots belong to A22, to A24, or to neither.
pos = {pid: pd.read_csv(RAW / f"GSM9022967_{pid}_tissue_positions.csv.gz", index_col=0) for pid in ["A22", "A24"]}
base = pos["A24"]
owner = np.where(pos["A24"].in_tissue == 1, 2, np.where(pos["A22"].loc[base.index].in_tissue == 1, 1, 0))
px = base[["pxl_col_in_fullres", "pxl_row_in_fullres"]].to_numpy(float)   # image orientation (x, y)
xy = px * 100.0 / np.median(cKDTree(px).query(px, k=2)[0][:, 1])            # 100 µm between touching spots
xy -= xy.min(axis=0)
data["shared_area"] = {"x": np.round(xy[:, 0]).astype(int).tolist(), "y": np.round(xy[:, 1]).astype(int).tolist(),
                       "owner": owner.tolist()}

# 3. A24 after QC: provisional expression-defined sets and the benchmark spots.
a24 = ad.read_h5ad(PROCESSED / f"{GSE}_A24.h5ad")
spots = spots_table(a24)
gene = lambda g: pd.Series(a24[:, g].X.toarray().ravel(), index=a24.obs_names)  # noqa: E731
prame_high, cxcl9_high = gene("PRAME") > 1.5, gene("CXCL9") > 2
touching = spots_within_radius(spots, X, 150)
dist_y = distance_to_region(spots, prame_high)[Y]
frac_x = neighbourhood_fraction(spots, cxcl9_high, 150).loc[X]
nearest = spots.loc[prame_high].assign(d=lambda t: np.hypot(t.x_um - spots.at[Y, "x_um"], t.y_um - spots.at[Y, "y_um"])).d.idxmin()

bench = pd.read_csv(ROOT / "02_spatial_operations/benchmark/benchmark.csv").set_index("id")
assert bench.at["B07", "reference_answer"] == f"{dist_y:.1f} µm", (bench.at["B07", "reference_answer"], dist_y)
assert bench.at["B11", "reference_answer"].startswith(f"{int(frac_x.n_in_category)}/{int(frac_x.n_neighbours)}")
assert sorted(touching) == sorted(s.strip() for s in bench.at["B03", "reference_answer"].split(":")[1].split(","))
print(f"B07 = {dist_y:.1f} µm, B11 = {int(frac_x.n_in_category)}/{int(frac_x.n_neighbours)}: match benchmark.csv")

origin = spots[["x_um", "y_um"]].min().to_numpy()
r = lambda v: np.round(v, 1).tolist()  # noqa: E731
data["a24"] = {
    "x": r(spots.x_um - origin[0]), "y": r(spots.y_um - origin[1]),
    "set": (prame_high.astype(int) + 2 * cxcl9_high.astype(int)).loc[spots.index].tolist(),   # 1 PRAME, 2 CXCL9, 3 both
    "n": int(len(spots)), "n_prame": int(prame_high.sum()), "n_cxcl9": int(cxcl9_high.sum()),
    "X": r(spots.loc[X, ["x_um", "y_um"]].to_numpy() - origin), "Y": r(spots.loc[Y, ["x_um", "y_um"]].to_numpy() - origin),
    "nearest_prame": r(spots.loc[nearest, ["x_um", "y_um"]].to_numpy() - origin),
    "touching": [r(spots.loc[s, ["x_um", "y_um"]].to_numpy() - origin) + [int(cxcl9_high[s])] for s in touching],
    "dist_y": round(float(dist_y), 1),
}

# 4. Why the radius matters on real coordinates: neighbours within 100 vs 150 µm, per A24 spot.
counts = {rad: neighbourhood_fraction(spots, prame_high, rad).n_neighbours for rad in (100, 150)}
data["neighbour_counts"] = {str(rad): c.value_counts().sort_index().astype(int).to_dict() for rad, c in counts.items()}
xy = spots[["x_um", "y_um"]].to_numpy()
dd, _ = cKDTree(xy).query(xy, k=7)
touch = dd[:, 1:][dd[:, 1:] < 150]
data["touching_range_um"] = [round(float(touch.min()), 1), round(float(touch.max()), 1)]
print("neighbours within 100 µm:", data["neighbour_counts"]["100"], "| within 150 µm:", data["neighbour_counts"]["150"])
print("touching spots are", data["touching_range_um"], "µm apart")

# Embed the data in slides.html between the FIGDATA markers, so the deck stays one self-contained file.
html = SLIDES.read_text(encoding="utf-8")
start, end = "<!--FIGDATA:START-->", "<!--FIGDATA:END-->"
head, rest = html.split(start)
_, tail = rest.split(end)
block = "<script>/* generated by make_figure_data.py, do not edit */ window.FIG = " + json.dumps(data, separators=(",", ":")) + ";</script>"
SLIDES.write_text(head + start + block + end + tail, encoding="utf-8")
print("embedded figure data in", SLIDES, f"({len(block) / 1e3:.0f} kB)")

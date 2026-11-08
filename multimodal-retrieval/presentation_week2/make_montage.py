"""Re-plot 5 pairs of the committed paired-spot dataset (notebook 05 outputs) for the slides.
Reads only files in manifests/: patches, rna_counts.npz, rna_genes.csv, paired_spots.csv, spots.csv.gz."""
import sys
import numpy as np, pandas as pd, scipy.sparse as sps, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from PIL import Image

M, OUT = sys.argv[1], sys.argv[2]
D = f"{M}/paired_spots/GSM9022967_A24"
paired = pd.read_csv(f"{D}/paired_spots.csv")
genes = pd.read_csv(f"{D}/rna_genes.csv")
counts = sps.load_npz(f"{D}/rna_counts.npz").tocsr()
rows = pd.read_csv(f"{D}/rna_rows.csv")
spots = pd.read_csv(f"{M}/spots.csv.gz")
sec = spots[(spots.gsm == "GSM9022967") & (spots.section_id == "A24")]
assert list(rows.spot_uid) == list(paired.spot_uid)

NAVY, INDIGO = "#0E1D40", "#413A8D"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13, "text.color": NAVY,
                     "axes.labelcolor": NAVY, "xtick.color": NAVY, "ytick.color": NAVY})
n = 5
fig = plt.figure(figsize=(12.5, 7.4), dpi=200)
gs = fig.add_gridspec(2, n, height_ratios=[1.45, 1], hspace=0.5, wspace=0.95)
for k in range(n):
    r = paired.iloc[k]
    assert r.rna_row == k
    patch = np.asarray(Image.open(f"{M}/{r.patch_context_file}"))
    half = r.patch_context_px * r.um_per_image_px / 2
    ax = fig.add_subplot(gs[0, k])
    ax.imshow(patch, extent=[-half, half, half, -half], interpolation="nearest")
    dx, dy = sec.x_um - r.x_um, sec.y_um - r.y_um
    near = (dx.abs() < half + 30) & (dy.abs() < half + 30) & ~((dx.abs() < 1) & (dy.abs() < 1))
    for xx, yy in zip(dx[near], dy[near]):
        ax.add_patch(Circle((xx, yy), 27.5, fill=False, ec="white", lw=1.2))
    ax.add_patch(Circle((0, 0), 27.5, fill=False, ec="#E0002A", lw=2.4))
    ax.plot([-half + 12, -half + 112], [half - 14, half - 14], color="black", lw=4, solid_capstyle="butt")
    ax.text(-half + 62, half - 24, "100 µm", ha="center", va="bottom", fontsize=12, color="black",
            bbox=dict(fc="white", ec="none", alpha=0.7, pad=1))
    ax.set_xlim(-half, half); ax.set_ylim(half, -half); ax.set_xticks([]); ax.set_yticks([])
    title = (f"{r.pair_id}\nrow {r.array_row}, col {r.array_col}\n"
             f"({r.x_um:,.0f}, {r.y_um:,.0f}) µm")
    ax.set_xlabel(r.barcode, fontsize=11.5, labelpad=4)
    ax.set_title(title, fontsize=13, linespacing=1.25)

    c = np.asarray(counts[k].todense()).ravel()
    top = np.argsort(c)[::-1][:5]
    bx = fig.add_subplot(gs[1, k]); bx.set_facecolor("#F5F5F5")
    y = np.arange(5)[::-1]
    bx.barh(y, c[top], color=INDIGO, height=0.7)
    bx.set_yticks(y); bx.set_yticklabels(genes.gene_symbol.values[top], fontsize=13)
    for yy, v in zip(y, c[top]):
        bx.text(v, yy, f" {int(v):,}", va="center", fontsize=12, color=NAVY)
    bx.set_xlim(0, c[top].max() * 1.75); bx.set_xticks([])
    for s in ["top", "right", "bottom"]:
        bx.spines[s].set_visible(False)
    bx.spines["left"].set_color("#9AA0C8")
    bx.set_title(f"{int(r.total_counts):,} UMIs\n{int(r.n_genes):,} genes",
                 fontsize=13, linespacing=1.25)
fig.text(0.5, 0.445, "RNA of the same barcode: top 5 genes by UMI count (all 37,082 stored)", ha="center", fontsize=14, color=INDIGO, weight="bold")
fig.savefig(OUT, bbox_inches="tight", facecolor="#F5F5F5")
print("saved", OUT)

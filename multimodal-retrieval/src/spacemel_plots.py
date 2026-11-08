"""
spacemel_plots.py - all figure drawing used by the notebooks.

No data processing happens here: functions receive arrays/DataFrames prepared by
spacemel_io.py and only draw them. Every spatial plot draws spots as circles of their
TRUE physical size (55 um) in image pixels, so the drawing itself shows whether the
spot scale matches the tissue.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import EllipseCollection


def savefig(fig, path, dpi: int = 150) -> None:
    """Save as PNG (small, committed to the repo) and close."""
    from pathlib import Path
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches="tight")


def spot_circles(ax, x, y, diameter_px, values=None, color=None, cmap="viridis",
                 vmin=None, vmax=None, edge_only=False, lw=0.4, alpha=0.9, facecolors=None):
    """Draw spots as circles of diameter_px (data units = image pixels).
    Returns the collection (usable for a colourbar when values are given)."""
    n = len(x)
    d = np.full(n, float(diameter_px))
    coll = EllipseCollection(d, d, np.zeros(n), units="xy",
                             offsets=np.column_stack([x, y]),
                             offset_transform=ax.transData)
    if edge_only:
        coll.set_facecolor("none")
        coll.set_edgecolor(color or "black")
        coll.set_linewidth(lw)
    elif facecolors is not None:
        coll.set_facecolor(facecolors)
        coll.set_edgecolor("none")
    elif values is not None:
        coll.set_array(np.asarray(values, float))
        coll.set_cmap(cmap)
        coll.set_clim(vmin, vmax)
        coll.set_edgecolor("none")
    else:
        coll.set_facecolor(color or "black")
        coll.set_edgecolor("none")
    coll.set_alpha(alpha)
    ax.add_collection(coll)
    return coll


def crop_to(ax, x, y, margin_px):
    """Zoom the axes to the bounding box of the spots (+ margin). Image y axis points down."""
    ax.set_xlim(np.min(x) - margin_px, np.max(x) + margin_px)
    ax.set_ylim(np.max(y) + margin_px, np.min(y) - margin_px)


def scalebar(ax, length_um, um_per_px, label=None, color="black"):
    """Horizontal scale bar in the lower-left corner of the current view."""
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()           # y0 > y1 for images
    L = length_um / um_per_px
    xs = x0 + 0.05 * (x1 - x0)
    ys = y0 - 0.06 * (y0 - y1)
    ax.plot([xs, xs + L], [ys, ys], color=color, lw=3, solid_capstyle="butt")
    ax.text(xs + L / 2, ys - 0.02 * (y0 - y1), label or f"{length_um:g} µm",
            ha="center", va="bottom", color=color, fontsize=8)


def section_map(ax, img, x, y, diameter_px, um_per_px, values=None, title="",
                cmap="viridis", vmin=None, vmax=None, color=None, margin_px=None,
                edge_only=False, scalebar_um=1000, alpha=0.9, facecolors=None):
    """H&E image + true-size spots, zoomed to the section. Returns the spot collection."""
    ax.imshow(img)
    coll = spot_circles(ax, x, y, diameter_px, values=values, color=color, cmap=cmap,
                        vmin=vmin, vmax=vmax, edge_only=edge_only, alpha=alpha,
                        facecolors=facecolors)
    crop_to(ax, x, y, margin_px if margin_px is not None else 10 * diameter_px)
    if scalebar_um:
        scalebar(ax, scalebar_um, um_per_px)
    ax.set_title(title, fontsize=9)
    ax.set_xticks([])
    ax.set_yticks([])
    return coll


def grid_axes(n, ncols=4, size=3.6):
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(size * ncols, size * nrows), squeeze=False)
    for ax in axes.ravel()[n:]:
        ax.axis("off")
    return fig, axes.ravel()[:n]


def violin_by_group(ax, data: dict, title="", log=False, threshold=None, thr_label=None, color="#4e79a7"):
    """One violin per key of `data` (key -> 1-D array), with the median marked."""
    keys = list(data)
    vals = [np.asarray(data[k], float) for k in keys]
    vals = [v[np.isfinite(v)] for v in vals]
    if log:
        vals = [np.log10(v + 1) for v in vals]
    parts = ax.violinplot(vals, showmedians=True, showextrema=False)
    for b in parts["bodies"]:
        b.set_facecolor(color)
        b.set_alpha(0.55)
    ax.set_xticks(range(1, len(keys) + 1))
    ax.set_xticklabels(keys, rotation=60, ha="right", fontsize=8)
    if threshold is not None:
        t = np.log10(threshold + 1) if log else threshold
        ax.axhline(t, color="firebrick", ls="--", lw=1, label=thr_label)
        if thr_label:
            ax.legend(fontsize=8, loc="upper right")
    ax.set_title(title, fontsize=10)

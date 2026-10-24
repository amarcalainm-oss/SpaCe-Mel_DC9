"""Spatial helpers: converting Visium coordinates to micrometres.

Why not use ``scalefactors["spot_diameter_fullres"]``? Space Ranger does not define it consistently: in GSE316760
(Space Ranger 2.0.1) it corresponds to a 65 µm spot, but in GSE300445 (Space Ranger 3.0, CytAssist) using 65 µm
gives distances ~7% off. The physical grid is reliable instead: Visium spot centres are 100 µm apart, on a
hexagonal grid where one ``array_col`` step is 50 µm and one ``array_row`` step is 50·√3 ≈ 86.6 µm.
"""

import numpy as np
import pandas as pd
from anndata import AnnData
from scipy.spatial import cKDTree

SPOT_SPACING_UM = 100.0


def grid_to_um(array_row, array_col) -> np.ndarray:
    """Ideal Visium grid position of each spot, in micrometres, as (x, y) columns."""
    return np.c_[np.asarray(array_col, float) * SPOT_SPACING_UM / 2,
                 np.asarray(array_row, float) * SPOT_SPACING_UM / 2 * np.sqrt(3)]


def um_per_px(adata: AnnData) -> float:
    """Micrometres per full-resolution pixel: 100 µm / median distance between neighbouring spots (in px)."""
    xy = adata.obsm["spatial"]
    nn_px = np.median(cKDTree(xy).query(xy, k=2)[0][:, 1])
    return SPOT_SPACING_UM / nn_px


def add_spatial_um(adata: AnnData, library_id: str) -> dict:
    """Store spot coordinates in micrometres in ``obsm["spatial_um"]`` (same orientation as the image).

    Returns a small dict comparing the grid method with the ``spot_diameter_fullres`` rules, to document
    the check in notebooks. The result is also stored in ``uns["spatial_units"]``.
    """
    scale = um_per_px(adata)
    adata.obsm["spatial_um"] = adata.obsm["spatial"] * scale
    spot_diam = adata.uns["spatial"][library_id]["scalefactors"]["spot_diameter_fullres"]
    info = {
        "um_per_px (grid, used)": scale,
        "um_per_px if 65 um / spot_diameter_fullres": 65 / spot_diam,
        "um_per_px if 55 um / spot_diameter_fullres": 55 / spot_diam,
        "error of 65-um rule (%)": 100 * (65 / spot_diam - scale) / scale,
    }
    adata.uns["spatial_units"] = {"um_per_px": scale, "method": "100 um / median nearest-neighbour spot distance"}
    return info


def units_table(adatas: dict[str, AnnData]) -> pd.DataFrame:
    """Run ``add_spatial_um`` on several samples and return the comparison as a table, one row per sample."""
    rows = {lib: add_spatial_um(a, lib) for lib, a in adatas.items()}
    for lib, a in adatas.items():
        rows[lib]["tissue extent x * y (mm)"] = "{:.2f} x {:.2f}".format(*np.ptp(a.obsm["spatial_um"], axis=0) / 1000)
    return pd.DataFrame(rows).T

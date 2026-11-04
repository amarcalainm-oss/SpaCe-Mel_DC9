"""Deterministic spatial operations on Visium spots (stage 2).

Three operations, all in micrometres and all computed **inside one tissue section at a time**:

1. ``spots_within_radius``    which spots are within r µm of a given spot?
2. ``distance_to_region``     how far is each spot from the nearest spot of a region?
3. ``neighbourhood_fraction`` around each spot, what share of its neighbours belong to a category?

Rules (agreed for this project):

- **Boundary is inclusive:** a spot exactly r µm away is a neighbour (distance <= r). A tiny tolerance
  (``TOLERANCE_UM``) absorbs floating-point rounding, so 100.0000000001 µm still counts for r = 100.
- **A spot is not its own neighbour.** A spot inside a region is at distance 0 from that region.
- **No neighbours** gives an empty list, and a neighbourhood fraction of NaN ("0 of 0" is undefined, not 0%).
- **A section with no region spots** gives NaN distances there ("no region in this section"), not a huge number.
- **Sections never connect:** spots of different sections (e.g. A22 and A24 on one capture area) are never
  neighbours, and a distance is only measured to region spots of the same section.

Every operation works on a *spots table* (see ``spots_table``): one row per spot, indexed by barcode, with
columns ``x_um``, ``y_um`` and ``section``. Regions and categories are boolean Series on the same index.
"""

import numpy as np
import pandas as pd
from anndata import AnnData
from scipy.spatial import cKDTree

TOLERANCE_UM = 1e-6


def spots_table(adata: AnnData, section: str | None = None) -> pd.DataFrame:
    """One row per spot: ``x_um``, ``y_um`` (from ``obsm["spatial_um"]``) and ``section``.

    ``section`` is the name of an ``obs`` column holding each spot's tissue section. If None, the AnnData is
    one section (our ``.h5ad`` files hold one patient each) and its library id is used as the name.
    """
    xy = adata.obsm["spatial_um"]
    if section is None:
        name = next(iter(adata.uns["spatial"]), "section")
        sections = np.full(adata.n_obs, name, dtype=object)
    else:
        sections = adata.obs[section].astype(str).to_numpy()
    return pd.DataFrame({"x_um": xy[:, 0], "y_um": xy[:, 1], "section": sections}, index=adata.obs_names.copy())


def spots_within_radius(spots: pd.DataFrame, spot_id: str, radius_um: float) -> pd.Index:
    """Barcodes of the spots within ``radius_um`` of ``spot_id`` (same section only, the spot itself excluded)."""
    _check_spots(spots)
    _check_radius(radius_um)
    if spot_id not in spots.index:
        raise KeyError(f"spot {spot_id!r} is not in the spots table")
    same = spots[spots.section == spots.at[spot_id, "section"]]
    dist = np.hypot(same.x_um - spots.at[spot_id, "x_um"], same.y_um - spots.at[spot_id, "y_um"])
    inside = (dist <= radius_um + TOLERANCE_UM) & (same.index != spot_id)
    return same.index[inside]


def distance_to_region(spots: pd.DataFrame, in_region: pd.Series) -> pd.Series:
    """Distance (µm) from each spot to the nearest region spot of its own section.

    0 for spots inside the region; NaN for every spot of a section that has no region spots.
    """
    _check_spots(spots)
    in_region = _aligned_mask(spots, in_region, "in_region")
    result = pd.Series(np.nan, index=spots.index, name="distance_um")
    for _, sec in spots.groupby("section", sort=False):
        region = sec[in_region[sec.index]]
        if region.empty:
            continue                                   # no region in this section: leave NaN
        tree = cKDTree(region[["x_um", "y_um"]].to_numpy())
        dist, _ = tree.query(sec[["x_um", "y_um"]].to_numpy(), k=1)
        result[sec.index] = dist
    return result


def neighbourhood_fraction(spots: pd.DataFrame, in_category: pd.Series, radius_um: float) -> pd.DataFrame:
    """For each spot: how many neighbours it has within ``radius_um``, how many are in the category, and the fraction.

    Neighbours follow ``spots_within_radius`` (same section, inclusive boundary, the spot itself excluded).
    The fraction is NaN for spots with no neighbours.
    """
    _check_spots(spots)
    _check_radius(radius_um)
    in_category = _aligned_mask(spots, in_category, "in_category")
    out = pd.DataFrame({"n_neighbours": 0, "n_in_category": 0}, index=spots.index)
    for _, sec in spots.groupby("section", sort=False):
        tree = cKDTree(sec[["x_um", "y_um"]].to_numpy())
        neighbours = tree.query_ball_point(sec[["x_um", "y_um"]].to_numpy(), r=radius_um + TOLERANCE_UM)
        is_cat = in_category[sec.index].to_numpy()
        for i, (barcode, nb) in enumerate(zip(sec.index, neighbours)):
            nb = [j for j in nb if j != i]             # a spot is not its own neighbour
            out.at[barcode, "n_neighbours"] = len(nb)
            out.at[barcode, "n_in_category"] = int(is_cat[nb].sum())
    with np.errstate(invalid="ignore", divide="ignore"):
        out["fraction"] = out.n_in_category / out.n_neighbours.where(out.n_neighbours > 0)
    return out


def _check_spots(spots: pd.DataFrame) -> None:
    missing = {"x_um", "y_um", "section"} - set(spots.columns)
    if missing:
        raise ValueError(f"spots table is missing columns {sorted(missing)}; build it with spots_table()")
    if not np.isfinite(spots[["x_um", "y_um"]].to_numpy(float)).all():
        raise ValueError("spot coordinates must be finite numbers (µm)")


def _check_radius(radius_um: float) -> None:
    if not radius_um > 0:
        raise ValueError(f"radius must be a positive number of µm, got {radius_um}")


def _aligned_mask(spots: pd.DataFrame, mask: pd.Series, name: str) -> pd.Series:
    """A boolean Series on exactly the spots' index (refuses masks that miss spots, to avoid silent errors)."""
    mask = pd.Series(mask)
    if not spots.index.isin(mask.index).all():
        raise ValueError(f"{name} must have a True/False value for every spot in the spots table")
    mask = mask.reindex(spots.index)
    if mask.isna().any():
        raise ValueError(f"{name} has missing values; use True/False for every spot")
    return mask.astype(bool)

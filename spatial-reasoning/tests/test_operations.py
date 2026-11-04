"""Tests for the spatial operations on tiny synthetic examples whose answers can be worked out by hand.

Run from the spatial-reasoning folder:  .venv\\Scripts\\python.exe -m pytest
"""

import numpy as np
import pandas as pd
import pytest

from space_mel.operations import distance_to_region, neighbourhood_fraction, spots_within_radius
from space_mel.spatial import grid_to_um


def make_spots(points, section="S1"):
    """Spots table from {barcode: (x_um, y_um)}; all in one section unless ``section`` is a dict."""
    df = pd.DataFrame(points, index=["x_um", "y_um"]).T.astype(float)
    df["section"] = [section[b] if isinstance(section, dict) else section for b in df.index]
    return df


# A line of five spots, 100 µm apart:   a(0) - b(100) - c(200) - d(300) - e(400)
LINE = make_spots({"a": (0, 0), "b": (100, 0), "c": (200, 0), "d": (300, 0), "e": (400, 0)})


def mask(spots, true_ids):
    return pd.Series(spots.index.isin(true_ids), index=spots.index)


# --- 1. spots within a radius -----------------------------------------------------------------------------------

def test_radius_simple_case():
    # from c (200 µm), radius 150 µm reaches b and d (100 µm away) but not a and e (200 µm away)
    assert set(spots_within_radius(LINE, "c", 150)) == {"b", "d"}


def test_radius_boundary_is_inclusive():
    # exactly 100 µm away counts as "within 100 µm"
    assert set(spots_within_radius(LINE, "c", 100)) == {"b", "d"}


def test_radius_boundary_survives_rounding():
    # 100 µm computed with rounding error (100.0000000001) still counts; 100.001 µm does not
    spots = make_spots({"o": (0, 0), "almost": (100 + 1e-10, 0), "outside": (100.001, 0)})
    assert set(spots_within_radius(spots, "o", 100)) == {"almost"}


def test_radius_excludes_the_spot_itself():
    assert "c" not in spots_within_radius(LINE, "c", 1000)


def test_radius_no_neighbours_gives_empty_result():
    spots = make_spots({"alone": (0, 0), "far": (1000, 0)})
    result = spots_within_radius(spots, "alone", 100)
    assert len(result) == 0


def test_radius_on_the_visium_hexagonal_grid():
    # on the real Visium grid every spot has 6 neighbours at 100 µm (one "ring")
    rows, cols = np.meshgrid(np.arange(-3, 4), np.arange(-6, 7), indexing="ij")
    keep = (rows + cols) % 2 == 0                      # Visium uses every other (row, col) position
    xy = grid_to_um(rows[keep], cols[keep])
    ids = [f"r{r}c{c}" for r, c in zip(rows[keep], cols[keep])]
    spots = make_spots(dict(zip(ids, map(tuple, xy))))
    assert len(spots_within_radius(spots, "r0c0", 100)) == 6
    assert len(spots_within_radius(spots, "r0c0", 99)) == 0


# --- 2. distance to a region ------------------------------------------------------------------------------------

def test_distance_known_values():
    # region = {a}; distances along the line are 0, 100, 200, 300, 400
    d = distance_to_region(LINE, mask(LINE, ["a"]))
    assert d.tolist() == [0, 100, 200, 300, 400]


def test_distance_is_zero_inside_the_region():
    d = distance_to_region(LINE, mask(LINE, ["b", "c"]))
    assert d["b"] == 0 and d["c"] == 0


def test_distance_uses_the_nearest_region_spot():
    # region = {a, e}: c is 200 µm from both, d is 100 µm from e
    d = distance_to_region(LINE, mask(LINE, ["a", "e"]))
    assert d["c"] == 200 and d["d"] == 100


def test_distance_diagonal():
    # a 3-4-5 triangle: the spot at (300, 400) is 500 µm from the region spot at (0, 0)
    spots = make_spots({"r": (0, 0), "p": (300, 400)})
    assert distance_to_region(spots, mask(spots, ["r"]))["p"] == pytest.approx(500)


def test_distance_section_without_region_is_nan():
    spots = make_spots({"a": (0, 0), "b": (100, 0), "x": (0, 0), "y": (100, 0)},
                       section={"a": "S1", "b": "S1", "x": "S2", "y": "S2"})
    d = distance_to_region(spots, mask(spots, ["a"]))
    assert d["b"] == 100
    assert np.isnan(d["x"]) and np.isnan(d["y"])


# --- 3. neighbourhood fraction ----------------------------------------------------------------------------------

def test_fraction_known_values():
    # category = {b}. Within 100 µm: a has neighbour b (1/1); c has b and d (1/2); e has d (0/1)
    f = neighbourhood_fraction(LINE, mask(LINE, ["b"]), 100)
    assert f.loc["a", "fraction"] == 1.0
    assert f.loc["c", "fraction"] == 0.5
    assert f.loc["e", "fraction"] == 0.0
    assert f.loc["c", "n_neighbours"] == 2 and f.loc["c", "n_in_category"] == 1


def test_fraction_does_not_count_the_spot_itself():
    # b is in the category, but its own neighbours (a, c) are not: its fraction is 0, not 1/3
    f = neighbourhood_fraction(LINE, mask(LINE, ["b"]), 100)
    assert f.loc["b", "fraction"] == 0.0 and f.loc["b", "n_neighbours"] == 2


def test_fraction_no_neighbours_is_nan():
    spots = make_spots({"alone": (0, 0), "far": (1000, 0)})
    f = neighbourhood_fraction(spots, mask(spots, ["far"]), 100)
    assert f.loc["alone", "n_neighbours"] == 0
    assert np.isnan(f.loc["alone", "fraction"])


def test_fraction_boundary_is_inclusive():
    f = neighbourhood_fraction(LINE, mask(LINE, ["b"]), 100)
    assert f.loc["a", "n_neighbours"] == 1          # b is exactly 100 µm from a


# --- sections never connect -------------------------------------------------------------------------------------

TWO_SECTIONS = make_spots({"s1": (0, 0), "s2": (10, 0)}, section={"s1": "A22", "s2": "A24"})


def test_sections_are_not_neighbours():
    assert len(spots_within_radius(TWO_SECTIONS, "s1", 100)) == 0


def test_sections_not_used_for_distance():
    d = distance_to_region(TWO_SECTIONS, mask(TWO_SECTIONS, ["s2"]))
    assert d["s2"] == 0 and np.isnan(d["s1"])        # s1 is 10 µm away but in another section


def test_sections_not_used_for_fraction():
    f = neighbourhood_fraction(TWO_SECTIONS, mask(TWO_SECTIONS, ["s2"]), 100)
    assert f.loc["s1", "n_neighbours"] == 0


# --- wrong inputs give clear errors -----------------------------------------------------------------------------

def test_bad_radius():
    with pytest.raises(ValueError, match="positive"):
        spots_within_radius(LINE, "c", 0)


def test_unknown_spot():
    with pytest.raises(KeyError):
        spots_within_radius(LINE, "zzz", 100)


def test_mask_must_cover_every_spot():
    with pytest.raises(ValueError, match="every spot"):
        distance_to_region(LINE, pd.Series([True], index=["a"]))

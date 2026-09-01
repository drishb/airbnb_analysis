"""
Smoke tests for `src/figures.py` (task 7.x). The full pipeline is the only
other thing that exercises these; here each function is called on a small
synthetic frame and the PNG it writes is checked for existence, non-empty
size, and the required 150 dpi (req 60).
"""
import numpy as np
import pandas as pd
import pytest
from PIL import Image

from src import config, figures


@pytest.fixture(autouse=True)
def _figures_to_tmp(tmp_path, monkeypatch):
    """Redirect every figure write into a tmp dir so tests never touch
    `outputs/figures/`."""
    monkeypatch.setattr(config, "FIGURE_DIR", tmp_path)
    return tmp_path


def _retained(n=12):
    """Synthetic retained-neighbourhood table with the columns the maps
    read: centroid coordinates, listing count, and a few indicators."""
    rng = np.random.default_rng(0)
    idx = pd.Index([f"N{i:02d}" for i in range(n)], name="neighbourhood")
    tbl = pd.DataFrame(
        {
            "centroid_lat": rng.uniform(33.4, 34.6, n),
            "centroid_lon": rng.uniform(-118.7, -117.8, n),
            "listing_count": rng.integers(100, 2000, n),
            "price_median": rng.uniform(80, 400, n),
            "host_hhi": rng.uniform(0.01, 0.45, n),
            "tour_reviews_per_month_mean": rng.uniform(0.3, 3.0, n),
            "reg_min30_share": rng.uniform(0.0, 0.7, n),
            "rev_capped_median": rng.uniform(500, 9000, n),
            "rev_uncapped_median": rng.uniform(500, 18000, n),
        },
        index=idx,
    )
    return tbl


def _listings(n=400):
    rng = np.random.default_rng(1)
    return pd.DataFrame(
        {
            "latitude": rng.uniform(33.3, 34.8, n),
            "longitude": rng.uniform(-118.9, -117.7, n),
            "minimum_nights": rng.choice([1, 2, 3, 5, 30, 31, 60, 200], n),
        }
    )


def _assert_png(path):
    assert path.exists() and path.stat().st_size > 0
    dpi = Image.open(path).info.get("dpi")
    assert dpi is not None and round(dpi[0]) == config.FIGURE_DPI


def test_centroid_bubble_map_continuous(_figures_to_tmp):
    tbl = _retained()
    path = figures.centroid_bubble_map(
        tbl, tbl["price_median"], title="t", legend_label="price ($)",
        name="m_price.png",
    )
    _assert_png(path)


def test_centroid_bubble_map_categorical(_figures_to_tmp):
    tbl = _retained()
    labels = pd.Series(np.arange(len(tbl)) % 4, index=tbl.index)
    path = figures.centroid_bubble_map(
        tbl, labels, title="clusters", legend_label="cluster",
        name="m_clusters.png", categorical=True,
        category_labels={0: "a", 1: "b", 2: "c", 3: "d"},
    )
    _assert_png(path)


def test_centroid_bubble_map_drops_rows_missing_from_values(_figures_to_tmp):
    tbl = _retained()
    partial = tbl["price_median"].iloc[:5]  # only 5 of 12 have a value
    # must not raise on the 7 rows with no indicator value
    path = figures.centroid_bubble_map(
        tbl, partial, title="t", legend_label="l", name="m_partial.png",
    )
    _assert_png(path)


def test_hexbin_density(_figures_to_tmp):
    _assert_png(figures.hexbin_density(_listings(), name="hex.png"))


def test_min_nights_histogram(_figures_to_tmp):
    _assert_png(figures.min_nights_histogram(_listings(), name="hist.png"))


def test_revenue_scatter(_figures_to_tmp):
    _assert_png(
        figures.revenue_capped_vs_uncapped(_retained(), name="rev.png")
    )

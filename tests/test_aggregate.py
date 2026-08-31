import numpy as np
import pandas as pd
import pytest

from src import aggregate, config


def _tbl(counts):
    """
    Synthetic neighbourhood table: every clustering feature (non-null,
    arbitrary values) plus the columns exclusion depends on. Indexed by
    neighbourhood like the real table from `build_table`.
    """
    feats = aggregate.feature_columns()
    idx = pd.Index([f"N{i:02d}" for i in range(len(counts))], name="neighbourhood")
    tbl = pd.DataFrame({c: np.linspace(1.0, 2.0, len(counts)) for c in feats}, index=idx)
    tbl.insert(0, "listing_count", counts)
    tbl.insert(
        1,
        "low_confidence",
        tbl["listing_count"] < config.MIN_LISTINGS_PER_NEIGHBOURHOOD,
    )
    tbl.insert(2, "neighbourhood_group", "City of Los Angeles")
    return tbl


# --- feature_columns ---------------------------------------------------


def test_feature_columns_match_family_map():
    expected = [c for cols in config.INDICATOR_FAMILIES.values() for c in cols]
    assert aggregate.feature_columns() == expected
    assert len(aggregate.feature_columns()) == 31


# --- exclusion logic (req 39) ----------------------------------------


def test_exclude_default_uses_config_threshold():
    tbl = _tbl([99, 100, 101, 500])
    out = aggregate.exclude_low_confidence(tbl)
    # n == 100 is retained (>= threshold), n == 99 is not
    assert list(out.index) == ["N01", "N02", "N03"]


def test_exclude_threshold_override():
    tbl = _tbl([40, 60, 120, 250])
    assert len(aggregate.exclude_low_confidence(tbl, threshold=50)) == 3
    assert len(aggregate.exclude_low_confidence(tbl, threshold=200)) == 1


def test_exclude_never_mutates_input():
    tbl = _tbl([10, 100, 300])
    before = tbl.copy(deep=True)
    out = aggregate.exclude_low_confidence(tbl)
    pd.testing.assert_frame_equal(tbl, before)
    # the returned view is a copy: writing to it must not reach `tbl`
    out.loc["N01", "listing_count"] = -1
    pd.testing.assert_frame_equal(tbl, before)


# --- threshold behaviour (req 41, task 4.6) -------------------------


def test_sensitivity_thresholds_are_monotonic():
    tbl = _tbl([20, 55, 99, 120, 210, 400, 800])
    sizes = [
        len(aggregate.exclude_low_confidence(tbl, t))
        for t in config.SENSITIVITY_THRESHOLDS
    ]
    assert config.SENSITIVITY_THRESHOLDS == [50, 100, 200]
    # a stricter threshold can only retain fewer neighbourhoods
    assert sizes == sorted(sizes, reverse=True)
    assert sizes == [6, 4, 3]


# --- feature_frame ---------------------------------------------------


def test_feature_frame_is_retained_rows_by_features():
    tbl = _tbl([10, 100, 100, 300])
    frame = aggregate.feature_frame(tbl)
    assert frame.shape == (3, len(aggregate.feature_columns()))
    assert list(frame.columns) == aggregate.feature_columns()
    assert "N00" not in frame.index


def test_feature_frame_raises_on_null_in_retained():
    tbl = _tbl([100, 200])
    tbl.loc["N00", "price_gini"] = np.nan
    with pytest.raises(ValueError, match="null features"):
        aggregate.feature_frame(tbl)


def test_feature_frame_tolerates_null_in_excluded():
    tbl = _tbl([10, 200])
    tbl.loc["N00", "price_gini"] = np.nan  # excluded row -> must not raise
    frame = aggregate.feature_frame(tbl)
    assert list(frame.index) == ["N01"]


# --- CSV export (req 42, req 39) -----------------------------------


def test_export_retains_low_confidence_neighbourhoods(tmp_path):
    tbl = _tbl([5, 50, 100, 400])
    path = tmp_path / "neighbourhood_indicators.csv"
    aggregate.export_table(tbl, path=path)
    rt = pd.read_csv(path)
    assert len(rt) == 4  # every neighbourhood in the export, flagged or not
    assert rt.columns[0] == "neighbourhood"
    assert set(rt["neighbourhood"]) == set(tbl.index)


def test_export_is_byte_identical_on_rerun(tmp_path):
    tbl = _tbl([5, 50, 100, 400])
    a, b = tmp_path / "a.csv", tmp_path / "b.csv"
    aggregate.export_table(tbl, path=a)
    aggregate.export_table(tbl, path=b)
    assert a.read_bytes() == b.read_bytes()

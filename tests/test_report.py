"""
Tests for `src/report.py` (tasks 8.3, 8.8).

`write_limitations` is checked for the PRD §10 field coverage that success
metric 11 depends on, and for run-to-run determinism. `write_success_metrics`
is driven with fake pipeline objects and pre-seeded output files so the
pass/fail logic (not the real numbers) is what gets exercised.
"""
import types

import numpy as np
import pandas as pd
import pytest

from src import aggregate, config, report


@pytest.fixture(autouse=True)
def _outputs_to_tmp(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(config, "FIGURE_DIR", tmp_path / "figures")
    (tmp_path / "figures").mkdir()
    return tmp_path


def _df(n=500):
    rng = np.random.default_rng(0)
    last = pd.to_datetime("2020-06-01") + pd.to_timedelta(
        rng.integers(-400, 60, n), unit="D"
    )
    reviewed = rng.random(n) > 0.2
    return pd.DataFrame(
        {
            "name": ["cozy place"] * (n - 2) + [None, None],
            "host_name": ["h"] * (n - 3) + [None, None, None],
            "number_of_reviews": np.where(reviewed, rng.integers(1, 80, n), 0),
            "last_review": pd.Series(last).where(reviewed),
            "reviews_per_month": pd.Series(rng.uniform(0.1, 5, n)).where(reviewed),
            "price": rng.integers(40, 900, n),
            "availability_365": rng.integers(0, 365, n),
            "minimum_nights": rng.choice([1, 2, 3, 30, 31, 400], n),
            "neighbourhood_group": rng.choice(
                ["City of Los Angeles", "Other Cities", "Unincorporated Areas"], n
            ),
        }
    )


# --- write_success_metrics (task 8.8) -------------------------------


def _tbl():
    feats = aggregate.feature_columns()
    idx = pd.Index([f"N{i:03d}" for i in range(264)], name="neighbourhood")
    counts = np.where(np.arange(264) < 79, 300, 40)
    tbl = pd.DataFrame(
        {c: np.linspace(1.0, 2.0, 264) for c in feats}, index=idx
    )
    tbl.insert(0, "listing_count", counts)
    tbl.insert(1, "low_confidence", tbl["listing_count"] < 100)
    tbl.insert(2, "neighbourhood_group", "City of Los Angeles")
    return tbl


def _sensitivity():
    return pd.DataFrame([
        {"threshold_low": 50, "threshold_high": 100, "n_common": 79, "n_changed": 18, "pct_changed": 22.8},
        {"threshold_low": 100, "threshold_high": 200, "n_common": 45, "n_changed": 18, "pct_changed": 40.0},
        {"threshold_low": 50, "threshold_high": 200, "n_common": 45, "n_changed": 19, "pct_changed": 42.2},
    ])


def _seed_output_files(out):
    (out / "excluded_neighbourhoods.md").write_text(
        "(a) Rate instability\n(b) Mechanical HHI inflation\n"
        "(c) Clustering distortion\nListings in excluded neighbourhoods\n"
        "Threshold sensitivity\n50 100 200\n",
        encoding="utf-8",
    )
    (out / "topic_model.md").write_text("Hypothesis check\n", encoding="utf-8")
    for name in ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]:
        (out / "figures" / f"{name}.png").write_bytes(b"x")


def _fakes(r2, sil):
    results = types.SimpleNamespace(
        rsquared=r2,
        pvalues=pd.Series([0.0, 0.01, 0.2, 0.001]),  # 3 of 4 significant
    )
    diag = pd.DataFrame(
        {"inertia": [1.0], "silhouette": [sil]},
        index=pd.Index([config.CLUSTER_K], name="k"),
    )
    pca_result = {"ari": 0.31}
    labels = dict(config.CLUSTER_LABELS)
    return results, diag, pca_result, labels


# --- write_limitations (req 67) --------------------------------------


def test_limitations_covers_every_section_10_field():
    tbl = _tbl()
    results, diag, pca_result, _ = _fakes(r2=0.33, sil=0.19)
    text = report.write_limitations(_df(), tbl, results, diag, pca_result, _sensitivity())
    for field in ["last_review", "reviews_per_month", "`name`", "host_name",
                  "`price`", "availability_365", "minimum_nights",
                  "neighbourhood_group", "Geometry", "cross-section"]:
        assert field in text, f"limitations.md missing §10 field: {field}"


def test_limitations_is_deterministic():
    df = _df()
    tbl = _tbl()
    results, diag, pca_result, _ = _fakes(r2=0.33, sil=0.19)
    sensitivity = _sensitivity()
    a = report.write_limitations(df, tbl, results, diag, pca_result, sensitivity)
    b = report.write_limitations(df, tbl, results, diag, pca_result, sensitivity)
    assert a == b


def test_success_metrics_all_pass_when_thresholds_met(_outputs_to_tmp):
    out = _outputs_to_tmp
    tbl = _tbl()
    aggregate.export_table(tbl)
    _seed_output_files(out)
    results, diag, pca_result, labels = _fakes(r2=0.40, sil=0.30)
    sensitivity = _sensitivity()
    report.write_limitations(_df(), tbl, results, diag, pca_result, sensitivity)

    text = report.write_success_metrics(
        tbl, results, diag, pca_result, labels, sensitivity)

    assert "11 of 11 met" in text
    assert "FAIL" not in text
    assert not (out / "_repro_check.csv").exists()  # scratch file cleaned up


def test_success_metrics_flags_r2_and_silhouette_misses(_outputs_to_tmp):
    out = _outputs_to_tmp
    tbl = _tbl()
    aggregate.export_table(tbl)
    _seed_output_files(out)
    results, diag, pca_result, labels = _fakes(r2=0.33, sil=0.19)
    sensitivity = _sensitivity()
    report.write_limitations(_df(), tbl, results, diag, pca_result, sensitivity)

    text = report.write_success_metrics(
        tbl, results, diag, pca_result, labels, sensitivity)

    assert "9 of 11 met" in text
    # metrics 3 and 4 are the FAIL rows
    assert "| 3 | Hedonic" in text and "| 4 | Clustering" in text
    lines = [ln for ln in text.splitlines() if ln.startswith("| ")]
    verdicts = {ln.split("|")[1].strip(): ln.split("|")[3].strip()
                for ln in lines if ln.split("|")[1].strip().isdigit()}
    assert verdicts["3"] == "FAIL"
    assert verdicts["4"] == "FAIL"
    assert verdicts["1"] == "PASS"

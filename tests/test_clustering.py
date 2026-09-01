import numpy as np
import pandas as pd
import pytest

from src import clustering, config


def _feature_frame(n=120, seed=0):
    """
    Synthetic retained-neighbourhood feature frame: every clustering
    feature, each column drawn on its own arbitrary scale so
    standardisation has something to do. Indexed like the real frame.
    """
    rng = np.random.default_rng(seed)
    feats = [c for cols in config.INDICATOR_FAMILIES.values() for c in cols]
    idx = pd.Index([f"N{i:03d}" for i in range(n)], name="neighbourhood")
    data = {
        c: rng.normal(loc=10.0 * (j + 1), scale=3.0 * (j + 1), size=n)
        for j, c in enumerate(feats)
    }
    return pd.DataFrame(data, index=idx)


# --- standardisation (req 49) ---------------------------------------


def test_standardize_zero_mean_unit_variance():
    z = clustering.standardize(_feature_frame())
    assert np.allclose(z.mean(), 0.0, atol=1e-9)
    assert np.allclose(z.std(ddof=0), 1.0, atol=1e-9)
    assert list(z.columns) == list(_feature_frame().columns)


# --- family weighting (req 50) ------------------------------------------


def test_family_weight_divides_by_sqrt_family_size():
    z = clustering.standardize(_feature_frame())
    w = clustering.family_weight(z)
    for family, cols in config.INDICATOR_FAMILIES.items():
        ratio = (w[cols] / z[cols]).to_numpy()
        assert np.allclose(ratio, 1.0 / np.sqrt(len(cols)), atol=1e-12)


def test_family_weight_equalises_family_variance():
    """The property req 50 exists to create: every family contributes the
    same total feature variance after weighting."""
    w = clustering.family_weight(clustering.standardize(_feature_frame()))
    totals = {
        fam: float(w[cols].var(ddof=0).sum())
        for fam, cols in config.INDICATOR_FAMILIES.items()
    }
    assert np.allclose(list(totals.values()), 1.0, atol=1e-9)


def test_family_weight_equalises_distance_contribution():
    """
    Task 6.9: the weighting must equalise each family's contribution to the
    squared Euclidean distance K-means minimises. For any two rows, the
    per-family sum of squared coordinate differences should average to the
    same value across families - unlike in unweighted standardised space,
    where a 9-feature family contributes ~9x a 1-feature family.
    """
    z = clustering.standardize(_feature_frame(n=400, seed=3))
    w = clustering.family_weight(z)

    def mean_family_contribution(frame):
        X = frame.to_numpy()
        # all pairwise squared diffs, per feature: E[(xi-xj)^2] = 2*Var
        sq = np.zeros(frame.shape[1])
        for a in range(0, 200):
            d = X[a] - X[200 + a]
            sq += d * d
        sq /= 200
        return {
            fam: float(sq[[frame.columns.get_loc(c) for c in cols]].sum())
            for fam, cols in config.INDICATOR_FAMILIES.items()
        }

    unweighted = mean_family_contribution(z)
    weighted = mean_family_contribution(w)

    # unweighted: contribution tracks family size (spread is wide)
    sizes = [len(c) for c in config.INDICATOR_FAMILIES.values()]
    assert max(unweighted.values()) / min(unweighted.values()) > 3.0
    assert max(sizes) / min(sizes) > 3.0

    # weighted: contributions are within a tight band of each other
    vals = list(weighted.values())
    assert max(vals) / min(vals) < 1.6


# --- k selection + fit (req 51, 52) -----------------------------------


def test_fit_kmeans_is_reproducible_and_sized():
    w = clustering.family_weight(clustering.standardize(_feature_frame()))
    _, a = clustering.fit_kmeans(w, k=4)
    _, b = clustering.fit_kmeans(w, k=4)
    assert a.equals(b)
    assert a.nunique() == 4
    assert list(a.index) == list(w.index)


# --- label guards (req 55) -------------------------------------------


def test_label_clusters_rejects_wrong_cluster_count():
    bad = pd.DataFrame(
        {"n_neighbourhoods": [1, 2, 3]},
        index=pd.Index([0, 1, 2], name="cluster"),
    )
    with pytest.raises(ValueError, match="do not match"):
        clustering.label_clusters(bad)

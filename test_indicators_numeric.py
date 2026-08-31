import numpy as np
import pandas as pd
from src import indicators_numeric as ind


def test_gini_perfect_equality():
    assert abs(ind.gini(np.array([10.0]*20))) < 1e-9


def test_gini_maximal_inequality():
    x = np.array([0.0]*19 + [100.0])
    assert ind.gini(x) > 0.9


def test_gini_known_value():
    """Gini of [1,2,3,4,5] is 0.2667 by hand."""
    assert abs(ind.gini(np.array([1,2,3,4,5])) - 0.26666667) < 1e-6


def test_hhi_single_host_is_one():
    assert ind.hhi(pd.Series([7,7,7,7])) == 1.0


def test_hhi_floor_is_one_over_n():
    """Four distinct hosts, one listing each -> HHI = 4*(0.25^2) = 0.25."""
    assert abs(ind.hhi(pd.Series([1,2,3,4])) - 0.25) < 1e-9


def test_top5_share():
    s = pd.Series([1,1,1,2,2,3,4,5,6,7])
    # top 5 hosts hold 3+2+1+1+1 = 8 of 10
    assert abs(ind.top_n_share(s, 5) - 0.8) < 1e-9


def test_revenue_capped_never_exceeds_uncapped():
    df = pd.DataFrame({
        "neighbourhood": ["A"]*4,
        "number_of_reviews": [10, 10, 10, 10],
        "price": [100]*4,
        "minimum_nights": [1, 3, 30, 365],
        "availability_365": [0, 100, 200, 365],
    })
    out = ind.revenue_occupancy(df)
    assert out["rev_capped_median"].iat[0] <= out["rev_uncapped_median"].iat[0]


def test_inactivity_uses_covid_cutoff():
    df = pd.DataFrame({
        "neighbourhood": ["A"]*4,
        "number_of_reviews": [0, 5, 5, 5],
        "last_review": pd.to_datetime([None, "2019-01-01", "2020-06-01", "2020-07-01"]),
    })
    out = ind.inactivity(df)
    assert out["inactivity_never_reviewed_share"].iat[0] == 0.25
    assert out["inactivity_stale_since_covid_share"].iat[0] == 0.25


def test_revenue_excludes_unreviewed_listings():
    """Task 2.0 decision: the estimator is undefined without reviews, so
    unreviewed listings are excluded rather than counted as zero."""
    df = pd.DataFrame({
        "neighbourhood": ["A"]*5,
        "number_of_reviews": [0, 0, 0, 10, 20],
        "price": [100]*5,
        "minimum_nights": [2]*5,
        "availability_365": [100]*5,
    })
    out = ind.revenue_occupancy(df)
    # 3 of 5 unreviewed: median over all would be 0, over reviewed is 1500
    assert out["rev_uncapped_median"].iat[0] > 0
    assert out["rev_supporting_listings"].iat[0] == 2


def test_revenue_supporting_count_zero_when_none_reviewed():
    df = pd.DataFrame({
        "neighbourhood": ["A"]*3,
        "number_of_reviews": [0, 0, 0],
        "price": [100]*3,
        "minimum_nights": [2]*3,
        "availability_365": [100]*3,
    })
    out = ind.revenue_occupancy(df)
    assert out["rev_supporting_listings"].iat[0] == 0
    assert np.isnan(out["rev_uncapped_median"].iat[0])

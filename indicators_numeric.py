"""
Numeric indicator computation, aggregated to neighbourhood level.
Implements PRD requirements 7-27 and 35-36.

Every public function takes the cleaned listing frame and returns a
DataFrame indexed by neighbourhood. `compute_all` joins them.
"""

import numpy as np
import pandas as pd

from . import config, geo


# --- helpers -------------------------------------------------------------

def gini(x: np.ndarray) -> float:
    """
    Gini coefficient of a non-negative array (PRD req 26).
    Uses the sorted-rank formulation; returns NaN for fewer than 2 values.
    """
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    if len(x) < 2 or x.sum() == 0:
        return np.nan
    x = np.sort(x)
    n = len(x)
    idx = np.arange(1, n + 1)
    return float((2 * idx - n - 1).dot(x) / (n * x.sum()))


def hhi(host_ids: pd.Series) -> float:
    """
    Herfindahl-Hirschman Index over host shares within a neighbourhood
    (PRD req 11). Ranges from 1/n (perfectly dispersed) to 1 (one host owns
    everything). The 1/n floor is why small neighbourhoods are excluded in
    task 4.0 — a 10-listing area cannot register as unconcentrated.
    """
    shares = host_ids.value_counts(normalize=True)
    return float((shares ** 2).sum())


def top_n_share(host_ids: pd.Series, n: int = 5) -> float:
    """Combined listing share of the n largest hosts (PRD req 13)."""
    counts = host_ids.value_counts()
    return float(counts.head(n).sum() / counts.sum())


# --- indicator families --------------------------------------------------

def tourism(df: pd.DataFrame) -> pd.DataFrame:
    """PRD req 7, 10: booking velocity, entire-home share, landmark distances."""
    g = df.groupby("neighbourhood")
    out = pd.DataFrame({
        "tour_reviews_per_month_mean": g["reviews_per_month"].mean(),
        "tour_reviews_per_month_median": g["reviews_per_month"].median(),
        "tour_reviews_total_mean": g["number_of_reviews"].mean(),
        "tour_entire_home_share": g["room_type"].apply(
            lambda s: (s == "Entire home/apt").mean()),
    })
    # req 10: aggregate all five distances to a neighbourhood median
    for col in [c for c in df.columns if c.startswith("dist_")]:
        out[f"tour_{col}_median"] = g[col].median()
    return out


def host_concentration(df: pd.DataFrame) -> pd.DataFrame:
    """PRD req 11-14."""
    g = df.groupby("neighbourhood")
    return pd.DataFrame({
        "host_hhi": g["host_id"].apply(hhi),
        "host_share_10plus": g["calculated_host_listings_count"].apply(
            lambda s: (s >= 10).mean()),
        "host_top5_share": g["host_id"].apply(top_n_share),
        "host_multilisting_share": g["calculated_host_listings_count"].apply(
            lambda s: (s > 1).mean()),
    })


def regulatory(df: pd.DataFrame) -> pd.DataFrame:
    """
    PRD req 15. A minimum stay of 30+ nights exempts a listing from LA's
    2019 Home-Sharing Ordinance, so a high share here indicates housing
    converted to long-term rental rather than tourism supply.
    """
    g = df.groupby("neighbourhood")
    return pd.DataFrame({
        "reg_min30_share": g["minimum_nights"].apply(
            lambda s: (s >= config.LONG_STAY_THRESHOLD).mean()),
        "reg_min_nights_median": g["minimum_nights"].median(),
    })


def tenure(df: pd.DataFrame) -> pd.DataFrame:
    """
    PRD req 18-19. Months a listing has been accumulating reviews, as a
    crude proxy for how long it has existed. Only defined for reviewed
    listings, so the supporting count is recorded alongside.
    """
    d = df.copy()
    d["tenure_months"] = np.where(
        d["reviews_per_month"] > 0,
        d["number_of_reviews"] / d["reviews_per_month"],
        np.nan,
    )
    g = d.groupby("neighbourhood")
    return pd.DataFrame({
        "tenure_months_median": g["tenure_months"].median(),
        "tenure_supporting_listings": g["tenure_months"].count(),
    })


def revenue_occupancy(df: pd.DataFrame) -> pd.DataFrame:
    """
    PRD req 20-25. Two revenue variants, kept strictly separate.

    The Inside Airbnb formula multiplies by minimum_nights, which inflates
    estimates for the ~32% of listings sitting at 30+. The capped variant
    limits that multiplier; both are reported and never combined.

    Revenue medians are taken over *reviewed listings only*. The estimator
    is undefined for a listing with no reviews — it is not estimating zero
    revenue, it is estimating nothing. Including unreviewed listings as
    zeros drags the median to exactly 0 wherever more than half a
    neighbourhood is unreviewed (Avalon: 59.1% unreviewed, median $0),
    which asserts something the formula cannot support. The supporting
    count is reported alongside, matching the pattern used for tenure.
    """
    d = df.copy()
    base = d["number_of_reviews"] * config.REVIEWS_PER_STAY * d["price"]
    d["rev_uncapped"] = base * d["minimum_nights"]
    d["rev_capped"] = base * d["minimum_nights"].clip(upper=config.REVENUE_NIGHTS_CAP)
    d["booked_days_proxy"] = 365 - d["availability_365"]

    reviewed = d.loc[d["number_of_reviews"] > 0]
    gr = reviewed.groupby("neighbourhood")
    g = d.groupby("neighbourhood")

    out = pd.DataFrame({
        "rev_uncapped_median": gr["rev_uncapped"].median(),
        "rev_capped_median": gr["rev_capped"].median(),
        "rev_supporting_listings": gr["rev_uncapped"].count(),
        "occ_booked_days_median": g["booked_days_proxy"].median(),
        "occ_zero_availability_share": g["availability_365"].apply(
            lambda s: (s == 0).mean()),
    })
    out = out.reindex(g.size().index)
    out["rev_supporting_listings"] = out["rev_supporting_listings"].fillna(0).astype(int)

    # req 23: where the two variants diverge most, the estimate is least
    # trustworthy. Ratio rather than difference so it is scale-free.
    out["rev_divergence_ratio"] = (
        out["rev_uncapped_median"] / out["rev_capped_median"].replace(0, np.nan)
    )
    # req 25: flag neighbourhoods where the occupancy proxy is unreliable
    out["occ_proxy_unreliable"] = out["occ_zero_availability_share"] > 0.30
    return out


def price_structure(df: pd.DataFrame) -> pd.DataFrame:
    """PRD req 26-27. Raw price, not winsorised — these are descriptive."""
    g = df.groupby("neighbourhood")
    q1 = g["price"].quantile(0.25)
    q3 = g["price"].quantile(0.75)
    out = pd.DataFrame({
        "price_median": g["price"].median(),
        "price_iqr": q3 - q1,
        "price_cv": g["price"].std() / g["price"].mean(),
        "price_gini": g["price"].apply(lambda s: gini(s.to_numpy())),
    })

    # req 27: median price per room type, as separate columns
    by_type = (df.pivot_table(index="neighbourhood", columns="room_type",
                              values="price", aggfunc="median"))
    by_type.columns = [
        "price_median_" + c.lower().replace("/", "_").replace(" ", "_")
        for c in by_type.columns
    ]
    return out.join(by_type)


def inactivity(df: pd.DataFrame) -> pd.DataFrame:
    """
    PRD req 35-36. Named *inactivity* throughout, never decline: the scrape
    is mid-pandemic and these figures reflect COVID, not local character.
    """
    cutoff = pd.Timestamp(config.COVID_CUTOFF)
    d = df.copy()
    d["never_reviewed"] = d["number_of_reviews"] == 0
    d["stale_since_covid"] = d["last_review"].notna() & (d["last_review"] < cutoff)

    g = d.groupby("neighbourhood")
    return pd.DataFrame({
        "inactivity_never_reviewed_share": g["never_reviewed"].mean(),
        "inactivity_stale_since_covid_share": g["stale_since_covid"].mean(),
    })


# --- assembly ------------------------------------------------------------

def compute_all(df: pd.DataFrame) -> pd.DataFrame:
    """
    Attach distance columns, compute every numeric indicator family, and
    join into one neighbourhood-indexed table.
    """
    df = geo.add_distance_columns(df)

    parts = [
        tourism(df),
        host_concentration(df),
        regulatory(df),
        tenure(df),
        revenue_occupancy(df),
        price_structure(df),
        inactivity(df),
    ]
    out = parts[0]
    for p in parts[1:]:
        out = out.join(p, how="outer")

    out.insert(0, "listing_count", df.groupby("neighbourhood").size())
    out.insert(1, "neighbourhood_group",
               df.groupby("neighbourhood")["neighbourhood_group"].agg(
                   lambda s: s.mode().iat[0]))
    out.insert(2, "centroid_lat", df.groupby("neighbourhood")["latitude"].mean())
    out.insert(3, "centroid_lon", df.groupby("neighbourhood")["longitude"].mean())
    return out

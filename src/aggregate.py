"""
Neighbourhood table assembly, low-confidence flagging, and exclusion.
Implements PRD requirements 37-39 (this file grows through task 4.0:
threshold sensitivity and CSV export follow).

The table is the single join point for every indicator computed upstream:
numeric families from `indicators_numeric` and topic loadings from
`indicators_text`. One row per neighbourhood, indexed by neighbourhood name.
"""

import pandas as pd

from . import config, indicators_numeric, indicators_text


def feature_columns() -> list[str]:
    """
    Every clustering feature, families concatenated in INDICATOR_FAMILIES
    order. The single source of truth for what task 6.0 standardises.
    """
    return [c for cols in config.INDICATOR_FAMILIES.values() for c in cols]


def build_table(df: pd.DataFrame, loadings: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    PRD req 37: one neighbourhood-level table, one row per neighbourhood,
    every indicator as a column.
    PRD req 38: a listing-count column (already produced by
    `indicators_numeric.compute_all`) and a low-confidence flag at
    n < MIN_LISTINGS_PER_NEIGHBOURHOOD.

    `loadings` is the per-neighbourhood topic-loading frame from
    `indicators_text.write_report`. It is accepted as an argument because
    fitting the topic model is the slowest stage in the pipeline and the
    caller (run_analysis) already has it; passed None, it is computed here.

    All 264 neighbourhoods are retained. The flag marks the small ones;
    exclusion from ranked output happens later (req 39), never here.
    """
    numeric = indicators_numeric.compute_all(df)
    if loadings is None:
        loadings = indicators_text.write_report(df)

    tbl = numeric.join(loadings, how="left")

    if len(tbl) != df["neighbourhood"].nunique():
        raise ValueError(
            f"neighbourhood table has {len(tbl)} rows, expected "
            f"{df['neighbourhood'].nunique()} — the numeric/text join dropped rows"
        )

    low_conf = tbl["listing_count"] < config.MIN_LISTINGS_PER_NEIGHBOURHOOD
    tbl.insert(1, "low_confidence", low_conf)

    _validate_columns(tbl)

    print(f"[aggregate] neighbourhood table {tbl.shape[0]} x {tbl.shape[1]} "
          f"({int((~low_conf).sum())} at n >= "
          f"{config.MIN_LISTINGS_PER_NEIGHBOURHOOD}, {int(low_conf.sum())} flagged)")
    return tbl


def _validate_columns(tbl: pd.DataFrame) -> None:
    """
    Every column is either a clustering feature or descriptive-only, and the
    two sets do not overlap. Guards against a new indicator column being
    added upstream without a home in config - it would otherwise slip
    silently into or out of the clustering feature set.
    """
    feats = set(feature_columns())
    desc = set(config.DESCRIPTIVE_ONLY_COLUMNS)
    overlap = feats & desc
    if overlap:
        raise ValueError(f"columns in both feature and descriptive sets: {sorted(overlap)}")
    unclassified = [c for c in tbl.columns if c not in feats and c not in desc]
    if unclassified:
        raise ValueError(
            f"columns with no home in config (add to INDICATOR_FAMILIES or "
            f"DESCRIPTIVE_ONLY_COLUMNS): {unclassified}"
        )
    missing = [c for c in feats if c not in tbl.columns]
    if missing:
        raise ValueError(f"INDICATOR_FAMILIES names columns not in the table: {missing}")


def exclude_low_confidence(tbl: pd.DataFrame, threshold: int | None = None) -> pd.DataFrame:
    """
    PRD req 39: the rows that survive into ranked output, clustering, and
    maps. Every one of the 264 stays in `tbl` (the exported table); this is
    the filtered view the downstream stages consume, never a mutation.

    `threshold` overrides MIN_LISTINGS_PER_NEIGHBOURHOOD for the n = 50 / 100
    / 200 sensitivity analysis (req 41, task 4.6).
    """
    threshold = config.MIN_LISTINGS_PER_NEIGHBOURHOOD if threshold is None else threshold
    return tbl[tbl["listing_count"] >= threshold].copy()


def feature_frame(tbl: pd.DataFrame, threshold: int | None = None) -> pd.DataFrame:
    """
    Retained neighbourhoods x the 31 clustering features, in family order.
    The exact matrix task 6.0 standardises and weights. Raises if any
    retained neighbourhood has a null feature - imputation is not wanted
    here, a null means an indicator is genuinely undefined and the
    neighbourhood should have been excluded.
    """
    retained = exclude_low_confidence(tbl, threshold)
    frame = retained[feature_columns()]
    nulls = frame.isna().sum()
    if nulls.any():
        raise ValueError(
            f"retained neighbourhoods have null features: {nulls[nulls > 0].to_dict()}"
        )
    return frame

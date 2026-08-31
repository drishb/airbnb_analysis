"""
Neighbourhood table assembly and low-confidence flagging.
Implements PRD requirements 37-38 (this file grows through task 4.0:
exclusion, threshold sensitivity, and CSV export follow).

The table is the single join point for every indicator computed upstream:
numeric families from `indicators_numeric` and topic loadings from
`indicators_text`. One row per neighbourhood, indexed by neighbourhood name.
"""

import pandas as pd

from . import config, indicators_numeric, indicators_text


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

    print(f"[aggregate] neighbourhood table {tbl.shape[0]} x {tbl.shape[1]} "
          f"({int((~low_conf).sum())} at n >= "
          f"{config.MIN_LISTINGS_PER_NEIGHBOURHOOD}, {int(low_conf.sum())} flagged)")
    return tbl

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


def export_table(tbl: pd.DataFrame, path=None) -> None:
    """
    PRD req 42 (and req 39: every one of the 264 neighbourhoods, not just
    the retained ones). Writes the full table to
    `outputs/neighbourhood_indicators.csv`.

    Column order is the table as `build_table` assembled it: the count /
    flag / geo columns, then the eight indicator families in
    `INDICATOR_FAMILIES` order with their descriptive-only siblings, then
    the topic loadings. Rows are alphabetical by neighbourhood (the
    groupby order upstream).

    No `float_format` is applied - pandas writes full round-trip precision,
    which is deterministic given deterministic inputs, so reruns are
    byte-identical (success metric 10). Null indicator values for excluded
    neighbourhoods are written as empty fields.
    """
    path = path or (config.OUTPUT_DIR / "neighbourhood_indicators.csv")
    tbl.to_csv(path, index=True, index_label="neighbourhood", encoding="utf-8")
    print(f"[aggregate] neighbourhood table -> {path} "
          f"({tbl.shape[0]} rows x {tbl.shape[1]} columns)")


def write_exclusion_report(
    tbl: pd.DataFrame,
    sensitivity: pd.DataFrame | None = None,
    path=None,
) -> None:
    """
    PRD req 40: the excluded-neighbourhood report - full list with listing
    counts, the total listings the exclusion removes, and the three stated
    reasons for the n >= 100 threshold.

    `sensitivity` is the n = 50 / 100 / 200 cluster-stability table from
    task 4.6 (req 41). Passed None, the report says that run is pending
    rather than omitting the section.
    """
    n = config.MIN_LISTINGS_PER_NEIGHBOURHOOD
    total_listings = int(tbl["listing_count"].sum())
    excluded = tbl[tbl["low_confidence"]].sort_values(
        ["listing_count"], ascending=False, kind="stable"
    )
    removed = int(excluded["listing_count"].sum())
    pct = 100 * removed / total_listings

    # Concrete figures for the reasons, taken from the actual excluded set.
    smallest = int(excluded["listing_count"].min())
    near_miss = excluded[excluded["listing_count"] >= n - 10]

    lines = [
        "# Excluded Neighbourhoods",
        "",
        f"The neighbourhood table retains all **{len(tbl)}** neighbourhoods. "
        f"Ranked tables, clustering, and maps use only the "
        f"**{int((~tbl['low_confidence']).sum())}** with at least **{n}** "
        f"listings. This report covers the **{len(excluded)}** that are "
        "excluded from those outputs.",
        "",
        "## What the exclusion removes",
        "",
        f"- Neighbourhoods excluded: **{len(excluded)}** of {len(tbl)} "
        f"({100 * len(excluded) / len(tbl):.0f}%)",
        f"- Listings in excluded neighbourhoods: **{removed:,}** of "
        f"{total_listings:,} (**{pct:.1f}%**)",
        f"- Excluded neighbourhoods hold **{smallest}** to "
        f"**{int(excluded['listing_count'].max())}** listings each; "
        f"{len(near_miss)} sit within 10 of the threshold "
        f"({', '.join(f'{ix} ({int(r)})' for ix, r in near_miss['listing_count'].items())}).",
        "",
        f"The exclusion trades {pct:.1f}% of listing volume for indicator "
        "stability. The retained neighbourhoods still cover "
        f"{100 - pct:.1f}% of the market by listing count.",
        "",
        f"## Why n >= {n}",
        "",
        "Three problems affect small neighbourhoods, and all three get worse "
        "as n falls.",
        "",
        "### (a) Rate instability",
        "",
        "Every share indicator - entire-home share, 30-night-minimum share, "
        "no-review share - can only take values that are multiples of 1/n. A "
        f"neighbourhood with 12 listings produces entire-home shares in steps "
        "of 8.3%, and moving one listing shifts the value by that much. The "
        "ranking would then order neighbourhoods partly on which side of a "
        "rounding step they happen to land.",
        "",
        "### (b) Mechanical HHI inflation",
        "",
        "The Herfindahl-Hirschman index has a floor of 1/n. A 10-listing "
        "neighbourhood cannot score below 0.10 even if all 10 hosts are "
        "distinct - it would read as moderately concentrated purely from "
        "being small. Host concentration is one of the eight indicator "
        "families, so this pushes small neighbourhoods toward the "
        '"commercialised" end of the segmentation as an artifact of size.',
        "",
        "### (c) Clustering distortion",
        "",
        "K-means minimises within-cluster variance. A small neighbourhood "
        "with an extreme indicator value - easy to produce when n is small - "
        "pulls a centroid toward itself and can end up alone in its own "
        "cluster, spending a segment on noise instead of a real market type.",
        "",
        "## Threshold sensitivity (req 41)",
        "",
    ]

    if sensitivity is None:
        lines += [
            "_Pending: the n = 50 / 100 / 200 cluster-stability comparison is "
            "produced by task 4.6 once the clustering stage (task 6.0) exists. "
            "It will report how many neighbourhoods change cluster assignment "
            "between thresholds; if that number is small, the choice of 100 is "
            "not load-bearing._",
            "",
        ]
    else:
        lines += [sensitivity.to_markdown(index=False), ""]

    lines += [
        f"## Full list of excluded neighbourhoods ({len(excluded)})",
        "",
        "| Neighbourhood | Listings | Group |",
        "|---|---:|---|",
    ]
    for name, row in excluded.iterrows():
        lines.append(
            f"| {name} | {int(row['listing_count'])} | {row['neighbourhood_group']} |"
        )
    lines.append("")

    path = path or (config.OUTPUT_DIR / "excluded_neighbourhoods.md")
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[aggregate] exclusion report -> {path} "
          f"({len(excluded)} neighbourhoods, {pct:.1f}% of listings)")

"""
Data ingestion, validation, and cleaning.
Implements PRD requirements 1-6.
"""

import pandas as pd
import numpy as np

from . import config


class SchemaError(Exception):
    """Raised when the input CSV does not match the expected schema."""


def load_raw(path=None) -> pd.DataFrame:
    """
    PRD req 1: load the CSV and validate the expected 16 columns are present,
    failing with a clear message if not.
    PRD req 2: parse last_review as a datetime.
    """
    path = path or config.DATA_FILE
    if not path.exists():
        raise FileNotFoundError(
            f"Input CSV not found at {path}. "
            f"Place listings_California.csv in {path.parent}/"
        )

    df = pd.read_csv(path, parse_dates=["last_review"])

    missing = [c for c in config.EXPECTED_COLUMNS if c not in df.columns]
    unexpected = [c for c in df.columns if c not in config.EXPECTED_COLUMNS]
    if missing:
        raise SchemaError(
            f"Input CSV is missing {len(missing)} expected column(s): {missing}. "
            f"Found columns: {list(df.columns)}"
        )
    if unexpected:
        raise SchemaError(
            f"Input CSV has {len(unexpected)} unexpected column(s): {unexpected}. "
            f"Expected exactly: {config.EXPECTED_COLUMNS}"
        )

    return df


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    PRD req 3: drop rows where price == 0, and log how many were dropped.
    PRD req 4: winsorise price at 1st/99th pct into a separate column,
               retaining the raw value for descriptive statistics.
    PRD req 5: preserve nulls in last_review and reviews_per_month.

    Returns the cleaned frame and a dict of cleaning statistics.
    """
    stats = {"rows_in": len(df)}

    zero_price = int((df["price"] == 0).sum())
    df = df.loc[df["price"] > 0].copy()
    stats["zero_price_dropped"] = zero_price
    stats["rows_after_zero_price_drop"] = len(df)

    lo = df["price"].quantile(config.WINSORIZE_LOWER_PCT)
    hi = df["price"].quantile(config.WINSORIZE_UPPER_PCT)
    df["price_winsorized"] = df["price"].clip(lower=lo, upper=hi)
    df["log_price"] = np.log(df["price_winsorized"])

    stats["winsorize_lower_bound"] = float(lo)
    stats["winsorize_upper_bound"] = float(hi)
    stats["winsorized_low_count"] = int((df["price"] < lo).sum())
    stats["winsorized_high_count"] = int((df["price"] > hi).sum())

    # Task 1.8 decision: flag island listings rather than dropping them.
    # Catalina is absent from the coastline polyline, so any coast distance
    # computed for these would be measured to the mainland — wrong by ~30 km
    # for listings that are beachfront. Task 2.3 sets their coast distance
    # to NaN on the strength of this flag.
    df["is_island"] = df["neighbourhood"].isin(config.ISLAND_NEIGHBOURHOODS)
    stats["island_listings"] = int(df["is_island"].sum())

    # req 5: no imputation. Asserted rather than assumed, because a later
    # refactor that fills these would silently destroy the inactivity
    # indicator in section 4.9.
    assert df["last_review"].isna().sum() > 0, "last_review nulls were filled"
    assert df["reviews_per_month"].isna().sum() > 0, "reviews_per_month nulls were filled"
    stats["last_review_nulls"] = int(df["last_review"].isna().sum())
    stats["reviews_per_month_nulls"] = int(df["reviews_per_month"].isna().sum())

    return df, stats


def _never_reviewed(df: pd.DataFrame) -> pd.Series:
    """Rows where all three review fields agree that the listing is unreviewed."""
    return (
        (df["number_of_reviews"] == 0)
        & df["last_review"].isna()
        & df["reviews_per_month"].isna()
    )


def _consistency_ok(df: pd.DataFrame) -> bool:
    """True when the three review fields encode exactly the same set of rows."""
    return (
        int((df["number_of_reviews"] == 0).sum())
        == int(df["last_review"].isna().sum())
        == int(df["reviews_per_month"].isna().sum())
        == int(_never_reviewed(df).sum())
    )


def quality_report(df_raw: pd.DataFrame, df_clean: pd.DataFrame, stats: dict) -> str:
    """
    PRD req 6: emit a data-quality report with null counts, zero counts,
    and outlier bounds per column.
    """
    lines = [
        "# Data Quality Report",
        "",
        f"- Rows in raw file: **{stats['rows_in']:,}**",
        f"- Rows after cleaning: **{len(df_clean):,}**",
        f"- Dropped for `price == 0`: **{stats['zero_price_dropped']}**",
        "",
        "## Per-column summary (raw file)",
        "",
        "| Column | dtype | Nulls | Null % | Zeros | Min | Max |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]

    n = len(df_raw)
    for col in config.EXPECTED_COLUMNS:
        s = df_raw[col]
        nulls = int(s.isna().sum())
        if pd.api.types.is_numeric_dtype(s):
            zeros = int((s == 0).sum())
            lo, hi = f"{s.min():,.4g}", f"{s.max():,.4g}"
        elif pd.api.types.is_datetime64_any_dtype(s):
            zeros = "—"
            lo = s.min().date() if nulls < n else "—"
            hi = s.max().date() if nulls < n else "—"
        else:
            zeros = "—"
            lo = hi = "—"
        lines.append(
            f"| `{col}` | {s.dtype} | {nulls:,} | {100*nulls/n:.1f}% | {zeros} | {lo} | {hi} |"
        )

    lines += [
        "",
        "## Price treatment",
        "",
        f"- Winsorisation bounds ({config.WINSORIZE_LOWER_PCT:.0%} / "
        f"{config.WINSORIZE_UPPER_PCT:.0%}): "
        f"**${stats['winsorize_lower_bound']:,.0f}** to "
        f"**${stats['winsorize_upper_bound']:,.0f}**",
        f"- Listings clipped at the low bound: **{stats['winsorized_low_count']:,}**",
        f"- Listings clipped at the high bound: **{stats['winsorized_high_count']:,}**",
        "- `price` retains raw values for descriptive statistics; "
        "`price_winsorized` and `log_price` are used for modelling.",
        "",
        "## Preserved nulls (not imputed)",
        "",
        f"- `last_review`: **{stats['last_review_nulls']:,}** nulls",
        f"- `reviews_per_month`: **{stats['reviews_per_month_nulls']:,}** nulls",
        "",
        "These are retained deliberately. A listing with no reviews has never "
        "been booked through the platform, which is the market-inactivity "
        "signal computed in section 4.9. Imputing them would erase it.",
        "",
        "## Review-field consistency check",
        "",
        "Three fields encode the same underlying fact — that a listing has "
        "never been reviewed — and they agree exactly:",
        "",
        "| Condition | Listings |",
        "|---|---:|",
        f"| `number_of_reviews == 0` | {int((df_raw['number_of_reviews']==0).sum()):,} |",
        f"| `last_review` is null | {int(df_raw['last_review'].isna().sum()):,} |",
        f"| `reviews_per_month` is null | {int(df_raw['reviews_per_month'].isna().sum()):,} |",
        f"| All three simultaneously | {int((_never_reviewed(df_raw)).sum()):,} |",
        "",
        f"**Agreement: {'exact' if _consistency_ok(df_raw) else 'MISMATCH — investigate'}.** "
        "The three are one signal, not three. Treating them as independent "
        "indicators would triple-count zero-review listings in any composite "
        "score, so downstream code uses `number_of_reviews == 0` alone.",
        "",
        "## Island listings",
        "",
        f"- Flagged as `is_island`: **{stats['island_listings']:,}** listings in "
        f"{', '.join(config.ISLAND_NEIGHBOURHOODS)}.",
        "- Santa Catalina Island sits roughly 35 km offshore and is excluded "
        "from the coastline polyline. Distance-to-coast is set to null for "
        "these listings rather than measured to the mainland.",
        "- All other indicators are computed for them normally.",
        "",
        "## Structural caveats",
        "",
        "- Single cross-sectional snapshot, scraped approximately August 2020. "
        "No change over time is measurable.",
        "- Scrape falls mid-pandemic. Inactivity figures reflect COVID conditions, "
        "not local market character.",
        "- Geographic coverage is Los Angeles County only, despite the filename.",
        f"- `availability_365 == 0` on "
        f"**{100*(df_raw['availability_365']==0).mean():.1f}%** of listings, and is "
        "ambiguous: fully booked, or host-blocked calendar.",
        f"- `minimum_nights >= {config.LONG_STAY_THRESHOLD}` on "
        f"**{100*(df_raw['minimum_nights']>=config.LONG_STAY_THRESHOLD).mean():.1f}%** "
        "of listings. The spike at exactly 30 is a regulatory artifact, not an "
        "organic distribution.",
        "",
    ]
    return "\n".join(lines)


def run(path=None) -> pd.DataFrame:
    """Load, validate, clean, and write the quality report."""
    df_raw = load_raw(path)
    df_clean, stats = clean(df_raw)

    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = config.OUTPUT_DIR / "data_quality_report.md"
    report_path.write_text(quality_report(df_raw, df_clean, stats))

    print(f"[ingest] {stats['rows_in']:,} rows in, {len(df_clean):,} after cleaning "
          f"({stats['zero_price_dropped']} zero-price dropped)")
    print(f"[ingest] quality report -> {report_path}")
    return df_clean

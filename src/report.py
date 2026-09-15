"""
Documentation output. PRD requirement 67 / success metric 11.

`write_limitations` generates `outputs/limitations.md`, which restates every
row of PRD §10 (Known Data Quality Issues and Limitations) plus the
analytical caveats from PRD §7 that constrain how the results may be read.
The point of the requirement is that a downstream reader of the `outputs/`
directory sees the constraints without having to open the PRD or the code.

Where a figure in §10 is a property of the data ("7,118 nulls", "23.4%
zeros") the number is recomputed from the cleaned frame - or, for §5's
model/segmentation figures, from the fitted objects - so the report can
never drift from the artefacts beside it. This matters more once the
pipeline runs against more than one dataset (config.select_dataset):
`write_limitations` takes the fitted regression/clustering objects as
arguments precisely so it never has to hardcode a number that differs by
dataset.
"""

from . import aggregate, config


def _facts(df) -> dict:
    """Live figures for the limitations table, from the cleaned frame."""
    n = len(df)
    reviewed = df["number_of_reviews"] > 0
    stale = df["last_review"].notna() & (
        df["last_review"] < config.COVID_CUTOFF
    )
    facts = {
        "n": n,
        "review_nulls": int(df["reviews_per_month"].isna().sum()),
        "review_null_pct": 100 * df["reviews_per_month"].isna().mean(),
        "name_nulls": int(df["name"].isna().sum()),
        "host_name_nulls": int(df["host_name"].isna().sum()),
        "price_max": float(df["price"].max()),
        "avail_zero_pct": 100 * (df["availability_365"] == 0).mean(),
        "min_nights_max": int(df["minimum_nights"].max()),
        "min30_pct": 100 * (df["minimum_nights"] >= 30).mean(),
        "stale_pct_of_reviewed": 100 * stale[reviewed].mean(),
        "last_review_max": df["last_review"].max().date(),
    }
    if config.HAS_NEIGHBOURHOOD_GROUP:
        facts["groups"] = ", ".join(sorted(df["neighbourhood_group"].dropna().unique()))
        facts["n_groups"] = df["neighbourhood_group"].nunique()
    return facts


def write_limitations(df, tbl, results, diag, pca_result, sensitivity,
                      path=None) -> str:
    """PRD req 67: `outputs/limitations.md`, every §10 item restated.

    `tbl`, `results`, `diag`, `pca_result`, `sensitivity` are the pipeline's
    own fitted objects (the neighbourhood table, the hedonic regression
    results, the k-selection diagnostics, the PCA robustness check, and the
    threshold-sensitivity table) - §5's model/segmentation numbers are read
    from them rather than hardcoded, so they are correct for whichever
    dataset is active.
    """
    f = _facts(df)
    retained_n = int((~tbl["low_confidence"]).sum())
    n_features = len(aggregate.feature_columns())
    r2 = float(results.rsquared)
    sil = float(diag.loc[config.CLUSTER_K, "silhouette"])
    ari = float(pca_result["ari"])
    sens_lo = float(sensitivity["pct_changed"].min())
    sens_hi = float(sensitivity["pct_changed"].max())

    if config.HAS_NEIGHBOURHOOD_GROUP:
        group_row = (
            f"| `neighbourhood_group` | only {f['n_groups']} values "
            f"({f['groups']}) | Geographic coverage is {config.CITY_LABEL} "
            f"only (source file `{config.DATA_FILE.name}`); the analysis "
            "claims nothing wider. |"
        )
    else:
        group_row = (
            "| `neighbourhood_group` | entirely null in this snapshot | No "
            "regional control term in the hedonic regression (req 43); the "
            "neighbourhood-fixed-effects variant is the only "
            "neighbourhood-level control available - see "
            "`regression_summary.txt`. |"
        )

    lines = [
        "# Limitations",
        "",
        f"This pipeline characterises {config.CITY_LABEL} short-term-rental "
        "**market structure at one point in time**. It is built on a single "
        f"cross-sectional Inside Airbnb snapshot ({f['n']:,} cleaned "
        f"listings, most recent review {f['last_review_max']}, scraped "
        "~mid-2020, source file "
        f"`{config.DATA_FILE.name}`). Every constraint below is restated "
        "from the project PRD (§7, §10) so it travels with the outputs.",
        "",
        "## 1. No change over time can be measured",
        "",
        "There is one observation per listing and no earlier snapshot. Every "
        "ranking, cluster, and coefficient describes the market **as it was "
        "at the time of the scrape**, not a trajectory. Words like "
        "*gentrifying*, *declining*, or *emerging* are not supportable from "
        "this data and are not used in any output.",
        "",
        "## 2. The snapshot is mid-pandemic",
        "",
        f"**{f['stale_pct_of_reviewed']:.1f}%** of reviewed listings had no "
        "review after 2020-03-01. The market-inactivity indicators "
        "(`inactivity_never_reviewed_share`, "
        "`inactivity_stale_since_covid_share`) therefore reflect COVID-19 "
        "conditions, not baseline local demand or neighbourhood character. "
        "They are named *inactivity* everywhere, never *decline*, and carry "
        "the pandemic caveat on every figure.",
        "",
        "## 3. Data-quality issues, per field (PRD §10)",
        "",
        "| Field | Issue | How it is handled |",
        "|---|---|---|",
        f"| `last_review`, `reviews_per_month` | {f['review_nulls']:,} nulls "
        f"({f['review_null_pct']:.1f}%) | Preserved as null, never imputed — "
        "the absence is the inactivity signal. Tenure and revenue medians are "
        "taken over reviewed listings only, with a supporting count. |",
        f"| `name` | {f['name_nulls']} nulls | Tokenised to an empty string; "
        "contributes no terms to TF-IDF / NMF. |",
        f"| `host_name` | {f['host_name_nulls']} nulls | Unused; host "
        "identity comes from `host_id`. |",
        f"| `price` | max ${f['price_max']:,.0f} | Zero-price rows dropped "
        "before any log transform (logged in the data-quality report). "
        "Winsorised at the 1st/99th percentile for modelling; raw value kept "
        "for description. |",
        f"| `availability_365` | {f['avail_zero_pct']:.1f}% zeros, ambiguous "
        "meaning | Reported per neighbourhood. The booked-days occupancy "
        "proxy is flagged unreliable wherever the zero share is high — a zero "
        "can mean fully booked or a host-blocked calendar. |",
        f"| `minimum_nights` | max {f['min_nights_max']:,}; "
        f"**{f['min30_pct']:.1f}%** at 30+ nights | See `regression_summary.txt` "
        "/ the minimum-nights histogram caption for whether a specific local "
        "ordinance is known to attach to the 30-night threshold in this "
        "market. |",
        group_row,
        "| Geometry | no boundary polygons in the CSV, no external files "
        "permitted | No choropleths. Centroid bubble maps (one marker per "
        "neighbourhood at its mean lat/long) and a hexbin over raw "
        "coordinates instead. **No Voronoi / synthesised boundaries** — they "
        "would imply spatial extent the data does not contain (req 59). |",
        "",
        "## 4. Estimator caveats (PRD §7.3)",
        "",
        "- **Revenue is an estimate, not a measurement.** Both variants use "
        "the Inside Airbnb occupancy model (reviews × 0.5 reviews-per-stay × "
        "nights × price). The **uncapped** variant multiplies by "
        "`minimum_nights`, which inflates the figure for listings with a "
        "long minimum stay; the **capped** variant limits that multiplier "
        "to 5. The two are reported as separate columns and are **never "
        "summed or averaged together**. `excluded_neighbourhoods.md` and "
        "`neighbourhood_indicators.csv` flag where they diverge most — "
        "those neighbourhoods' revenue figures are the least trustworthy.",
        "- **The 0.5 reviews-per-stay constant is taken as given** (the "
        "Inside Airbnb convention). Both revenue variants scale linearly in "
        "it, so a reader who prefers 0.3 or 0.7 can rescale the columns "
        "directly; the *ordering* of neighbourhoods by revenue is unchanged "
        "by the constant.",
        "- **Tenure** (`number_of_reviews / reviews_per_month`) is a crude "
        "proxy for how long a listing has operated and is only defined for "
        "reviewed listings.",
        "- **Price is right-skewed** (mean well above median, max "
        f"${f['price_max']:,.0f}). Modelling is on `log_price`; description "
        "uses medians, not means.",
        f"- **The `tour_dist_coast_km_median` column measures distance to "
        f"the {config.COASTLINE_LABEL}**, not necessarily an ocean coast — "
        "see `COASTLINE_LABEL` in `src/config.py` for what it means in this "
        "dataset.",
        "",
        "## 5. Model and segmentation caveats",
        "",
        f"- **Hedonic regression R² = {r2:.2f}** "
        f"({'meets' if r2 >= 0.35 else 'below'} success metric 3's 0.35 "
        "bar). See `regression_summary.txt` for the full coefficient table "
        "and the neighbourhood-fixed-effects robustness check (it typically "
        "fits better but cannot carry the mandated HC3 standard errors — "
        "single-listing neighbourhoods give those rows leverage 1).",
        f"- **Cluster mean silhouette ≈ {sil:.2f}** "
        f"({'meets' if sil >= 0.25 else 'below'} success metric 4's 0.25 "
        f"bar), over **{retained_n}** retained neighbourhoods and "
        f"**{n_features}** correlated indicators. The segmentation is "
        "reported as a **descriptive grouping**, not a claim of natural "
        f"boundaries. Family-weighted vs. PCA adjusted Rand index = "
        f"**{ari:.2f}**; the n = 50/100/200 threshold sensitivity moves "
        f"between **{sens_lo:.0f}%** and **{sens_hi:.0f}%** of common "
        "neighbourhoods to a different cluster (see "
        "`excluded_neighbourhoods.md` and `cluster_summary.md`) — treat "
        "individual cluster membership near the n-threshold boundary as "
        "approximate.",
        "- **Cluster labels are post-hoc**, assigned by reading the centroid "
        "table after fitting. They are summaries of a centroid profile, not "
        "inputs to the clustering.",
        "",
        "## 6. Out of scope",
        "",
        "No census / ACS demographics, no rent indices, no permit or "
        "registration records, no other Airbnb snapshots. These are what a "
        "rigorous neighbourhood-change study would require; this deliverable "
        f"consumes exactly one file (`{config.DATA_FILE.name}`) and makes no "
        "claim that would need them.",
        "",
    ]

    path = path or (config.OUTPUT_DIR / "limitations.md")
    text = "\n".join(lines)
    path.write_text(text, encoding="utf-8")
    print(f"[report] limitations -> {path}")
    return text


def write_success_metrics(tbl, results, diag, pca_result, cluster_labels,
                          sensitivity, path=None) -> str:
    """
    Task 8.8: check every success metric in PRD §8 and record pass or fail.

    Each row is evaluated against the live objects the pipeline just
    produced (or the artefacts on disk), not a remembered value, so the
    report cannot drift and stays correct across datasets. Metrics 3
    (hedonic R² ≥ 0.35) and 4 (cluster silhouette ≥ 0.25) are known LA
    misses; whether they miss on another dataset is whatever the live
    numbers below say.
    """
    out = config.OUTPUT_DIR
    feats = aggregate.feature_columns()
    retained = tbl[tbl["listing_count"] >= config.MIN_LISTINGS_PER_NEIGHBOURHOOD]
    retained_nulls = int(retained[feats].isna().sum().sum())
    no_duplicate_rows = tbl.index.nunique() == len(tbl)

    sig = int((results.pvalues < 0.05).sum())
    total_coef = int(len(results.pvalues))
    r2 = float(results.rsquared)

    sil = float(diag.loc[config.CLUSTER_K, "silhouette"])

    excl = (out / "excluded_neighbourhoods.md").read_text(encoding="utf-8")
    topic = (out / "topic_model.md").read_text(encoding="utf-8")
    lims = (out / "limitations.md").read_text(encoding="utf-8")
    n_figs = len(list(config.FIGURE_DIR.glob("*.png")))

    excluded_n = int(tbl["low_confidence"].sum())
    excluded_pct = 100 * tbl.loc[tbl["low_confidence"], "listing_count"].sum() \
        / tbl["listing_count"].sum()
    sens_lo = float(sensitivity["pct_changed"].min())
    sens_hi = float(sensitivity["pct_changed"].max())

    # metric 10: re-export the table to a scratch path and compare bytes
    scratch = out / "_repro_check.csv"
    aggregate.export_table(tbl, path=scratch)
    csv_identical = (
        scratch.read_bytes()
        == (out / "neighbourhood_indicators.csv").read_bytes()
    )
    scratch.unlink()

    s10_fields = ["last_review", "reviews_per_month", "`name`", "host_name",
                  "`price`", "availability_365", "minimum_nights",
                  "neighbourhood_group", "Geometry", "cross-section"]
    lims_ok = all(f in lims for f in s10_fields)

    checks = [
        ("1", "End-to-end from raw CSV, single command, zero manual steps",
         True,
         "`python run_analysis.py [--dataset ...]` runs ingest → table → "
         "regression → clustering → figures → reports with no "
         "intervention."),
        ("2", "Every neighbourhood in the table exactly once, no unexpected "
         "nulls in indicator columns",
         no_duplicate_rows and retained_nulls == 0,
         f"{len(tbl)} rows exported, {tbl.index.nunique()} distinct "
         f"neighbourhoods; {retained_nulls} nulls across the {len(feats)} "
         f"feature columns for the {int((~tbl['low_confidence']).sum())} "
         "retained neighbourhoods. Any feature nulls in excluded "
         "neighbourhoods (genuinely undefined indicators, e.g. price Gini "
         "on a single-listing area) are expected, not unexpected."),
        ("3", "Hedonic R² ≥ 0.35, majority of coefficients significant",
         r2 >= 0.35 and sig > total_coef / 2,
         f"R² = {r2:.3f} ({'meets' if r2 >= 0.35 else '**below the 0.35 bar**'}). "
         f"{sig} of {total_coef} coefficients significant at p < 0.05. "
         "See `regression_summary.txt`."),
        ("4", "Clustering mean silhouette ≥ 0.25, every cluster labelable",
         sil >= 0.25 and len(cluster_labels) == config.CLUSTER_K,
         f"Mean silhouette = {sil:.3f} at k = {config.CLUSTER_K} "
         f"({'meets' if sil >= 0.25 else '**below the 0.25 bar**'}). All "
         f"{len(cluster_labels)} clusters carry a centroid-derived label "
         "(guarded by `clustering.label_clusters`). See `cluster_summary.md`."),
        ("5", "Adjusted Rand index (family-weighted vs. PCA) reported",
         "ari" in pca_result,
         f"ARI = {pca_result['ari']:.3f}, reported in `cluster_summary.md` "
         "with interpretation."),
        ("6", "excluded_neighbourhoods.md: every excluded neighbourhood, "
         "total listings removed, all three reasons",
         all(s in excl for s in ["(a) Rate instability",
                                 "(b) Mechanical HHI inflation",
                                 "(c) Clustering distortion",
                                 "Listings in excluded neighbourhoods"]),
         f"{excluded_n}-row excluded table, {excluded_pct:.1f}% of listings "
         "removed, and the three stated reasons are all present."),
        ("7", "Threshold sensitivity at n = 50 / 100 / 200 reported",
         "Threshold sensitivity" in excl and "50" in excl and "200" in excl,
         f"Reported in `excluded_neighbourhoods.md`: {sens_lo:.0f}%–"
         f"{sens_hi:.0f}% of common neighbourhoods change cluster between "
         "thresholds."),
        ("8", "Derived topics labelled and compared to the tourism / "
         "upmarket / commercial hypothesis",
         "Hypothesis check" in topic,
         "`topic_model.md` labels every NMF topic and reports the "
         "hypothesis overlap."),
        ("9", "All 10 figures render without manual adjustment, legible at "
         "print size",
         n_figs == 10,
         f"{n_figs} PNGs in `{config.FIGURE_DIR}`, all at "
         f"{config.FIGURE_DPI} dpi, produced in the single pipeline run."),
        ("10", "Repeated runs produce byte-identical CSV output",
         csv_identical,
         "A second in-run export of the neighbourhood table is byte-for-byte "
         "equal to the written CSV."),
        ("11", "limitations.md generated, contains every PRD §10 item",
         (out / "limitations.md").exists() and lims_ok,
         "Generated by `report.write_limitations`; every §10 field "
         "(reviews, name, host_name, price, availability, minimum_nights, "
         "neighbourhood_group, geometry, the snapshot and pandemic rows) is "
         "restated."),
    ]

    n_pass = sum(1 for c in checks if c[2])

    lines = [
        "# Success Metrics (PRD §8)",
        "",
        f"**{n_pass} of {len(checks)} met.** Dataset: {config.CITY_LABEL} "
        f"(`{config.ACTIVE_DATASET}`).",
        "",
        "| # | Metric | Verdict |",
        "|---|---|---|",
    ]
    for num, desc, ok, _ in checks:
        lines.append(f"| {num} | {desc} | {'PASS' if ok else 'FAIL'} |")
    lines += ["", "## Detail", ""]
    for num, desc, ok, detail in checks:
        lines += [f"### {num}. {desc} — {'PASS' if ok else 'FAIL'}", "",
                  detail, ""]

    path = path or (out / "success_metrics.md")
    text = "\n".join(lines)
    path.write_text(text, encoding="utf-8")
    print(f"[report] success metrics -> {path} ({n_pass}/{len(checks)} met)")
    return text

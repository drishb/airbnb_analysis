# Limitations

This pipeline characterises LA County short-term-rental **market structure at one point in time**. It is built on a single cross-sectional Inside Airbnb snapshot (33,067 cleaned listings, most recent review 2020-08-21, scraped ~August 2020). Every constraint below is restated from the project PRD (§7, §10) so it travels with the outputs.

## 1. No change over time can be measured

There is one observation per listing and no earlier snapshot. Every ranking, cluster, and coefficient describes the market **as it was in August 2020**, not a trajectory. Words like *gentrifying*, *declining*, or *emerging* are not supportable from this data and are not used in any output.

## 2. The snapshot is mid-pandemic

**44.7%** of reviewed listings had no review after 2020-03-01. The market-inactivity indicators (`inactivity_never_reviewed_share`, `inactivity_stale_since_covid_share`) therefore reflect COVID-19 conditions, not baseline local demand or neighbourhood character. They are named *inactivity* everywhere, never *decline*, and carry the pandemic caveat on every figure.

## 3. Data-quality issues, per field (PRD §10)

| Field | Issue | How it is handled |
|---|---|---|
| `last_review`, `reviews_per_month` | 7,107 nulls (21.5%) | Preserved as null, never imputed — the absence is the inactivity signal. Tenure and revenue medians are taken over reviewed listings only, with a supporting count. |
| `name` | 2 nulls | Tokenised to an empty string; contributes no terms to TF-IDF / NMF. |
| `host_name` | 9 nulls | Unused; host identity comes from `host_id`. |
| `price` | 11 zeros; max $24,999 | Zeros dropped before any log transform (logged in the data-quality report). Winsorised at the 1st/99th percentile for modelling; raw value kept for description. |
| `availability_365` | 23.4% zeros, ambiguous meaning | Reported per neighbourhood. The booked-days occupancy proxy is flagged unreliable wherever the zero share is high — a zero can mean fully booked or a host-blocked calendar. |
| `minimum_nights` | max 1,125; non-organic spike at exactly 30 (32.1% at 30+) | The spike is treated as the regulatory-evasion signal itself, not smoothed away. The histogram is capped at 90 and annotated at 30. |
| `neighbourhood_group` | only 3 values (City of Los Angeles, Other Cities, Unincorporated Areas) | The filename says "California"; the data is LA County only and the analysis claims nothing wider. |
| Geometry | no boundary polygons in the CSV, no external files permitted | No choropleths. Centroid bubble maps (one marker per neighbourhood at its mean lat/long) and a hexbin over raw coordinates instead. **No Voronoi / synthesised boundaries** — they would imply spatial extent the data does not contain (req 59). |

## 4. Estimator caveats (PRD §7.3)

- **Revenue is an estimate, not a measurement.** Both variants use the Inside Airbnb occupancy model (reviews × 0.5 reviews-per-stay × nights × price). The **uncapped** variant multiplies by `minimum_nights`, which inflates the figure for the ~32% of listings at 30+ nights; the **capped** variant limits that multiplier to 5. The two are reported as separate columns and are **never summed or averaged together**. `excluded_neighbourhoods.md` and `neighbourhood_indicators.csv` flag where they diverge most — those neighbourhoods' revenue figures are the least trustworthy.
- **The 0.5 reviews-per-stay constant is taken as given** (the Inside Airbnb convention). Both revenue variants scale linearly in it, so a reader who prefers 0.3 or 0.7 can rescale the columns directly; the *ordering* of neighbourhoods by revenue is unchanged by the constant.
- **Tenure** (`number_of_reviews / reviews_per_month`) is a crude proxy for how long a listing has operated and is only defined for reviewed listings.
- **Price is right-skewed** (mean well above median, max $24,999). Modelling is on `log_price`; description uses medians, not means.

## 5. Model and segmentation caveats

- **Hedonic regression R² = 0.33**, below success metric 3's 0.35 bar. The req-43 formula is fixed. A 264-neighbourhood fixed-effects variant fits better (R² 0.48) but cannot carry the mandated HC3 errors (single-listing neighbourhoods give leverage 1), so it is reported only as a robustness note. See `regression_summary.txt`.
- **Cluster mean silhouette ≈ 0.19**, below success metric 4's 0.25 bar. 79 neighbourhoods described by 31 correlated indicators do not form tight, well-separated groups. The segmentation is a **descriptive grouping**, not a claim of natural boundaries, and the family-weighted vs. PCA adjusted Rand index (~0.30) plus the n = 50/100/200 threshold sensitivity (up to ~42% of common neighbourhoods change cluster) say the same: the broad shape is stable, mid-distribution membership is not. Treat individual cluster membership near the n = 100 boundary as approximate.
- **Cluster labels are post-hoc**, assigned by reading the centroid table after fitting. They are summaries of a centroid profile, not inputs to the clustering.

## 6. Out of scope

No census / ACS demographics, no rent indices, no permit or registration records, no other Airbnb snapshots. These are what a rigorous neighbourhood-change study would require; this deliverable consumes exactly one file (`listings_California.csv`) and makes no claim that would need them.

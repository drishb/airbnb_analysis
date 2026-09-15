# Limitations

This pipeline characterises Rio de Janeiro short-term-rental **market structure at one point in time**. It is built on a single cross-sectional Inside Airbnb snapshot (35,724 cleaned listings, most recent review 2020-06-19, scraped ~mid-2020, source file `listings-RIo_de_Janeiro.csv`). Every constraint below is restated from the project PRD (§7, §10) so it travels with the outputs.

## 1. No change over time can be measured

There is one observation per listing and no earlier snapshot. Every ranking, cluster, and coefficient describes the market **as it was at the time of the scrape**, not a trajectory. Words like *gentrifying*, *declining*, or *emerging* are not supportable from this data and are not used in any output.

## 2. The snapshot is mid-pandemic

**73.5%** of reviewed listings had no review after 2020-03-01. The market-inactivity indicators (`inactivity_never_reviewed_share`, `inactivity_stale_since_covid_share`) therefore reflect COVID-19 conditions, not baseline local demand or neighbourhood character. They are named *inactivity* everywhere, never *decline*, and carry the pandemic caveat on every figure.

## 3. Data-quality issues, per field (PRD §10)

| Field | Issue | How it is handled |
|---|---|---|
| `last_review`, `reviews_per_month` | 14,988 nulls (42.0%) | Preserved as null, never imputed — the absence is the inactivity signal. Tenure and revenue medians are taken over reviewed listings only, with a supporting count. |
| `name` | 58 nulls | Tokenised to an empty string; contributes no terms to TF-IDF / NMF. |
| `host_name` | 5 nulls | Unused; host identity comes from `host_id`. |
| `price` | max $132,358 | Zero-price rows dropped before any log transform (logged in the data-quality report). Winsorised at the 1st/99th percentile for modelling; raw value kept for description. |
| `availability_365` | 31.4% zeros, ambiguous meaning | Reported per neighbourhood. The booked-days occupancy proxy is flagged unreliable wherever the zero share is high — a zero can mean fully booked or a host-blocked calendar. |
| `minimum_nights` | max 1,123; **1.8%** at 30+ nights | See `regression_summary.txt` / the minimum-nights histogram caption for whether a specific local ordinance is known to attach to the 30-night threshold in this market. |
| `neighbourhood_group` | entirely null in this snapshot | No regional control term in the hedonic regression (req 43); the neighbourhood-fixed-effects variant is the only neighbourhood-level control available - see `regression_summary.txt`. |
| Geometry | no boundary polygons in the CSV, no external files permitted | No choropleths. Centroid bubble maps (one marker per neighbourhood at its mean lat/long) and a hexbin over raw coordinates instead. **No Voronoi / synthesised boundaries** — they would imply spatial extent the data does not contain (req 59). |

## 4. Estimator caveats (PRD §7.3)

- **Revenue is an estimate, not a measurement.** Both variants use the Inside Airbnb occupancy model (reviews × 0.5 reviews-per-stay × nights × price). The **uncapped** variant multiplies by `minimum_nights`, which inflates the figure for listings with a long minimum stay; the **capped** variant limits that multiplier to 5. The two are reported as separate columns and are **never summed or averaged together**. `excluded_neighbourhoods.md` and `neighbourhood_indicators.csv` flag where they diverge most — those neighbourhoods' revenue figures are the least trustworthy.
- **The 0.5 reviews-per-stay constant is taken as given** (the Inside Airbnb convention). Both revenue variants scale linearly in it, so a reader who prefers 0.3 or 0.7 can rescale the columns directly; the *ordering* of neighbourhoods by revenue is unchanged by the constant.
- **Tenure** (`number_of_reviews / reviews_per_month`) is a crude proxy for how long a listing has operated and is only defined for reviewed listings.
- **Price is right-skewed** (mean well above median, max $132,358). Modelling is on `log_price`; description uses medians, not means.
- **The `tour_dist_coast_km_median` column measures distance to the Atlantic coastline & Guanabara Bay**, not necessarily an ocean coast — see `COASTLINE_LABEL` in `src/config.py` for what it means in this dataset.

## 5. Model and segmentation caveats

- **Hedonic regression R² = 0.26** (below success metric 3's 0.35 bar). See `regression_summary.txt` for the full coefficient table and the neighbourhood-fixed-effects robustness check (it typically fits better but cannot carry the mandated HC3 standard errors — single-listing neighbourhoods give those rows leverage 1).
- **Cluster mean silhouette ≈ 0.17** (below success metric 4's 0.25 bar), over **32** retained neighbourhoods and **31** correlated indicators. The segmentation is reported as a **descriptive grouping**, not a claim of natural boundaries. Family-weighted vs. PCA adjusted Rand index = **0.38**; the n = 50/100/200 threshold sensitivity moves between **4%** and **58%** of common neighbourhoods to a different cluster (see `excluded_neighbourhoods.md` and `cluster_summary.md`) — treat individual cluster membership near the n-threshold boundary as approximate.
- **Cluster labels are post-hoc**, assigned by reading the centroid table after fitting. They are summaries of a centroid profile, not inputs to the clustering.

## 6. Out of scope

No census / ACS demographics, no rent indices, no permit or registration records, no other Airbnb snapshots. These are what a rigorous neighbourhood-change study would require; this deliverable consumes exactly one file (`listings-RIo_de_Janeiro.csv`) and makes no claim that would need them.

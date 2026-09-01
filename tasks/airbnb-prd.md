l# PRD: LA County Airbnb Market Structure Analysis Pipeline

## 1. Introduction/Overview

A reusable Python pipeline that ingests the Inside Airbnb `listings_California.csv` snapshot (33,078 LA County listings, scraped ~August 2020) and produces a neighbourhood-level characterisation of short-term rental market structure.

**The problem:** A market researcher evaluating LA County neighbourhoods has 33,078 raw listing rows and no way to tell which areas are tourist-driven, which are dominated by professional operators, and which have quietly converted housing stock into de-facto long-term corporate rentals. Reading the raw CSV answers none of this.

**The goal:** Aggregate the listing-level data into 264 neighbourhood profiles across eight indicator families, fit descriptive and inferential models over them, and emit tables, static maps, and charts that let a researcher rank and segment neighbourhoods on evidence rather than reputation.

**Critical scope note:** The dataset is a single cross-sectional snapshot taken mid-pandemic. This pipeline characterises market structure _at one point in time_. It cannot measure change over time — see §7 and §10.

---

## 2. Goals

1. Produce a clean neighbourhood-level feature table: 264 rows × ~22 engineered indicators, with small-sample neighbourhoods flagged and their exclusion documented.
2. Compute indicators across eight families: tourism intensity, host concentration, regulatory evasion, listing tenure, revenue/occupancy, price structure, text-derived signals, and market inactivity.
3. Fit a hedonic log-price regression identifying which listing attributes drive price, with robust standard errors.
4. Segment neighbourhoods into interpretable clusters via family-weighted K-means, with labels assigned post-hoc from centroid inspection.
5. Render static geospatial figures showing indicator distribution across the county.
6. Run end-to-end from a single command on the raw CSV, with no manual intervention.
7. Surface every data-quality caveat (§10) in the output rather than burying it in code comments.

---

## 3. User Stories

- As a **market researcher**, I want a ranked table of neighbourhoods by tourism intensity, so that I can identify which areas depend on visitor demand.
- As a **market researcher**, I want to see host concentration per neighbourhood, so that I can distinguish owner-operated markets from ones controlled by professional operators.
- As a **market researcher**, I want to know what share of listings in each neighbourhood use a 30-night minimum, so that I can identify where housing stock has been converted to long-term corporate rental to sidestep short-term rental regulation.
- As a **market researcher**, I want neighbourhoods grouped into a handful of market types, so that I can reason about categories instead of 264 individual areas.
- As a **market researcher**, I want to know which listing attributes actually drive nightly price, so that I can estimate what a property in a given area might command.
- As a **market researcher**, I want to know which neighbourhoods were excluded from rankings and why, so that I do not mistake an omission for an absence of activity.
- As a **market researcher**, I want maps of the key indicators, so that I can see spatial patterns that neighbourhood boundaries obscure.
- As a **market researcher**, I want the pipeline's limitations stated in its own output, so that I do not over-claim in downstream work.

---

## 4. Functional Requirements

### 4.1 Data ingestion and cleaning

1. The system must load `listings_California.csv` and validate that the expected 16 columns are present, failing with a clear message if not.
2. The system must parse `last_review` as a datetime.
3. The system must drop the 11 rows where `price == 0` before any log transformation, and log how many rows were dropped.
4. The system must winsorise `price` at the 1st and 99th percentiles for modelling, retaining the raw value in a separate column for descriptive statistics.
5. The system must preserve nulls in `last_review` and `reviews_per_month` (7,118 rows) rather than imputing them — their absence is itself a signal (§4.9).
6. The system must emit a data-quality report listing null counts, zero counts, and outlier bounds per column.

### 4.2 Tourism intensity indicators

7. The system must compute per neighbourhood: mean and median `reviews_per_month`, mean `number_of_reviews`, and the share of listings that are `Entire home/apt`.
8. The system must compute, for each listing, the great-circle (haversine) distance from its lat/long to each of five landmarks: the Pacific coastline, Hollywood, Downtown LA, Universal Studios, and Disneyland.
9. Distance to coast must be computed as the nearest point on a hardcoded simplified coastline polyline with at least 8 vertices spanning Malibu, Santa Monica, Venice, LAX, Manhattan Beach, Palos Verdes, San Pedro, and Long Beach. No external shapefile dependency.
10. The system must aggregate all five distances to a neighbourhood median.

### 4.3 Host concentration indicators

11. The system must compute a Herfindahl-Hirschman Index over `host_id` listing shares within each neighbourhood.
12. The system must compute the share of listings in each neighbourhood held by hosts with `calculated_host_listings_count >= 10`.
13. The system must compute the combined share held by the top 5 hosts in each neighbourhood.
14. The system must compute the share of listings held by any multi-listing host (`calculated_host_listings_count > 1`).

### 4.4 Regulatory evasion indicators

15. The system must compute, per neighbourhood, the share of listings with `minimum_nights >= 30`.
16. The system must produce a histogram of `minimum_nights` capped at 90, annotated to show the spike at exactly 30.
17. The system must document in its output that LA's 2019 Home-Sharing Ordinance caps short-term rentals at 120 nights/year and requires primary residence, and that a 30-night minimum exempts a listing from those rules.

### 4.5 Listing tenure indicator

18. The system must compute, for each listing with review data, an estimated tenure in months as `number_of_reviews / reviews_per_month`.
19. The system must aggregate tenure to a neighbourhood median and record the count of listings the estimate is based on.

### 4.6 Revenue and occupancy indicators

20. The system must compute **two** estimated-annual-revenue variants per listing, using the Inside Airbnb reviews-per-stay convention of 0.5:
    - **Uncapped:** `number_of_reviews × 0.5 × minimum_nights × price`
    - **Capped:** `number_of_reviews × 0.5 × min(minimum_nights, 5) × price`
21. Both variants must appear as separate columns in the neighbourhood table and must never be summed, averaged together, or presented as a single figure.
22. The system must produce a scatter plot of capped vs. uncapped revenue per neighbourhood, so the divergence introduced by the 32.1% of listings at 30+ nights is visible rather than assumed away.
23. The system must state in the output which neighbourhoods show the largest capped/uncapped gap, as these are the ones where the revenue estimate is least trustworthy.
24. The system must compute a booked-days proxy as `365 - availability_365`.
25. The system must report the share of listings with `availability_365 == 0` per neighbourhood, and must label the occupancy proxy as ambiguous wherever that share is high — a zero can mean fully booked or a host-blocked calendar.

### 4.7 Price structure indicators

26. The system must compute per neighbourhood: median price, interquartile range, coefficient of variation, and Gini coefficient of price.
27. The system must compute median price separately per `room_type` within each neighbourhood.

### 4.8 Text-derived indicators (data-driven)

28. The system must tokenise the `name` field — lowercased, punctuation stripped, English stopwords removed — with the 2 null names handled without error.
29. The system must fit a TF-IDF vectoriser over the full 33,078-title corpus using unigrams and bigrams, with `min_df` set to exclude terms appearing in fewer than 20 listings.
30. The system must compute, for each neighbourhood, the mean TF-IDF vector across its listings, and extract the top 15 terms by score — these are the terms that distinguish that neighbourhood's listings from the corpus as a whole.
31. The system must apply NMF or LDA topic modelling over the TF-IDF matrix to derive 5–8 latent topics, with the topic count selected by coherence score and the justification recorded.
32. The system must output a topic-term table showing the top-weighted terms per topic, and must assign each topic a human-readable label _after_ inspecting those terms.
33. The system must compute per-neighbourhood topic loadings — the mean topic distribution across that neighbourhood's listings — and include them as indicator columns.
34. Keyword categories must **not** be hardcoded. The tourism / upmarket / commercial groupings are hypotheses to be tested against the derived topics, not inputs to the analysis. The output must state whether the derived topics corroborate or contradict them.

### 4.9 Market inactivity indicators

35. The system must compute per neighbourhood: share of listings with no reviews at all, and share whose most recent review predates 2020-03-01.
36. The system must label these fields as _inactivity_ in all column names and chart titles, and must annotate them with the pandemic caveat wherever they appear.

### 4.10 Aggregation and neighbourhood exclusion

37. The system must produce a single neighbourhood-level table with one row per neighbourhood and all indicators above as columns.
38. The system must include a listing-count column and flag every neighbourhood with fewer than 100 listings as low-confidence.
39. The system must exclude low-confidence neighbourhoods from all ranked outputs, clustering, and maps, while retaining every one of them in the full exported table.
40. The system must generate an `excluded_neighbourhoods.md` report containing:
    - The full list of excluded neighbourhoods with their listing counts
    - The count and percentage of total listings the exclusion removes
    - A written statement of the three reasons for the n≥100 threshold: **(a) Rate instability** — a neighbourhood with 12 listings can only produce entire-home shares in increments of 8.3%, and a single listing changes the value by that much. **(b) Mechanical HHI inflation** — the Herfindahl index has a floor of 1/n. A 10-listing neighbourhood cannot register as unconcentrated even if all 10 hosts are distinct, so it would rank as "commercialised" purely from being small. **(c) Clustering distortion** — K-means minimises within-cluster variance. High-variance small neighbourhoods pull centroids toward noise and can capture entire clusters on their own.
41. The system must run the full ranking and clustering at thresholds of 50, 100, and 200, and report in `excluded_neighbourhoods.md` how many neighbourhoods change cluster assignment between them. If assignments are stable, the threshold choice is not load-bearing and this should be stated.
42. The system must export the neighbourhood table to CSV.

### 4.11 Hedonic price regression

43. The system must fit an OLS model of the form `log(price) ~ room_type + minimum_nights + availability_365 + calculated_host_listings_count + number_of_reviews + neighbourhood_group`.
44. The system must use heteroskedasticity-robust (HC3) standard errors.
45. The system must output the full coefficient table with standard errors, t-statistics, p-values, R², and n.
46. The system must produce residual diagnostic plots: residuals vs. fitted, and a Q-Q plot.
47. The system must report coefficients on log-price in interpretable form — as approximate percentage effects on price, not raw log units.
48. The regression must run on all listings, not only those in retained neighbourhoods, since it operates at listing level and does not aggregate.

### 4.12 Clustering

49. The system must standardise all neighbourhood features (zero mean, unit variance) before clustering.
50. The system must apply **family weighting**: each feature's standardised value is divided by √(number of features in its indicator family) before distance computation. Rationale in §7.
51. The system must select k using both an elbow plot and silhouette scores, testing k from 2 to 10, and must record the justification for the chosen k.
52. The system must fit K-means with a fixed random seed for reproducibility.
53. The system must additionally run PCA-based clustering (components retaining ≥85% variance) as a robustness check, and report the adjusted Rand index between the family-weighted and PCA solutions.
54. The system must output a centroid table showing each cluster's mean value per feature, in original units, not standardised ones.
55. The system must assign each cluster a descriptive human-readable label derived from its centroid profile _after_ fitting, and must document that labels were assigned post-hoc.
56. The system must list member neighbourhoods per cluster.

### 4.13 Geospatial output

57. The system must render, for at least median price, host concentration (HHI), tourism intensity, 30-night-minimum share, and cluster assignment:
    - **Centroid bubble maps** — one marker per retained neighbourhood at its mean lat/long, sized by listing count, coloured by the indicator.
58. The system must render a hexbin density map over raw lat/long, independent of neighbourhood labels, so spatial patterns that boundaries obscure remain visible.
59. The system must **not** generate Voronoi tessellations or any other synthesised boundary geometry. Fabricated polygons imply spatial extent the data does not contain.
60. The system must export all maps as PNG at ≥150 dpi.

### 4.14 Single data source

61. The pipeline must consume exactly one _data_ input: `listings_California.csv`. No shapefiles, no GeoJSON, no census or permit joins, no API calls for analysis data. Standard Python package resources (stopword lists, tokenisers) are not analysis data and are permitted.
62. Landmark coordinates (Hollywood, Downtown LA, Universal Studios, Disneyland) and the coastline polyline vertices must be defined as literal constants in a single configuration module, with a source comment for each.
63. Stopword removal may use scikit-learn's built-in `stop_words='english'` or an NLTK list. If NLTK is used, `nltk.download('stopwords')` must be run once during environment setup and documented in the README — not called from analysis code at runtime.
64. The analysis pipeline must run correctly with no network access once the environment is set up. Package installation and one-time corpus setup are exempt.

### 4.15 Outputs and reproducibility

65. The system must run end-to-end from a single entry point (e.g. `python run_analysis.py`).
66. The system must write all artefacts to a single `outputs/` directory: neighbourhood CSV, regression summary, cluster summary, exclusion report, topic model output, all figures, and the data-quality report.
67. The system must generate a `limitations.md` in the output directory restating every constraint in §10.
68. The system must pin dependency versions in `requirements.txt`.
69. The system must set random seeds globally — NumPy, scikit-learn, and any NMF/LDA initialisation — so repeated runs produce identical results.

---

## 5. Non-Goals (Out of Scope)

1. **Interactive dashboards or web deployment.** Static PNG output only. Do not build a Streamlit, Dash, or Flask application.
2. **Interactive maps.** No folium, no plotly. Matplotlib only.
3. **Joining external data.** Census ACS data, permit records, and rent indices are out of scope for this deliverable, despite being what rigorous neighbourhood-change measurement requires.

---

## 6. Design Considerations

- **Output directory layout:**

    ```
    outputs/
      neighbourhood_indicators.csv
      data_quality_report.md
      excluded_neighbourhoods.md
      regression_summary.txt
      cluster_summary.md
      topic_model.md
      limitations.md
      figures/
        map_median_price.png
        map_host_hhi.png
        map_tourism_intensity.png
        map_min_nights_30.png
        map_clusters.png
        hexbin_listing_density.png
        hist_minimum_nights.png
        scatter_revenue_capped_vs_uncapped.png
        elbow_silhouette.png
        residual_diagnostics.png
    ```

- All maps share a consistent colourmap and legend format. Use a perceptually uniform sequential map (viridis) for continuous indicators and a categorical map for clusters.
- Every figure carries a caption noting the snapshot date (August 2020) and the pandemic caveat.
- Neighbourhood tables are sorted descending by the indicator being ranked, with the low-confidence flag visible.

---

## 7. Technical Considerations

- **Stack:** Python 3.11+, `pandas`, `numpy`, `statsmodels`, `scikit-learn`, `matplotlib`.
- **No `geopandas`, no `shapely`.** Both exist to handle boundary geometry, and there is no boundary geometry available (§4.14). All spatial output is matplotlib scatter and hexbin over raw lat/long. Nearest-point-on-polyline for the coast distance is a few lines of NumPy — a geometry library is not warranted for it.
- **`nltk` optional.** Its stopword list and lemmatiser are fine to use; run `nltk.download()` once at setup rather than from analysis code, so the pipeline itself stays offline-runnable. scikit-learn's built-in list is sufficient if you'd rather skip the dependency.
- **No gretl.** It is built for time-series and panel econometrics, has no geospatial or text-processing support, and would require a second toolchain for work pandas must do anyway. Course permits free choice of tooling.

### 7.1 Why family weighting rather than PCA (requirement 50)

The indicator families contribute unequal column counts: host concentration has 4 features, listing tenure has 1. In standardised Euclidean space, K-means gives host concentration four times the influence of tenure purely because of how many columns were written for it. That is a measurement artifact driving the segmentation.

Two fixes exist. PCA removes the redundancy but replaces the original features with linear combinations, which destroys requirement 55 — you can no longer read a centroid table and say "high tourism, low concentration," because the axes no longer correspond to anything nameable. Family weighting by 1/√(family size) equalises each family's total contribution to the distance metric while leaving the features themselves intact and interpretable.

Family weighting is therefore primary; PCA runs as a robustness check (requirement 53). If the adjusted Rand index between the two is high, the segmentation is not an artifact of the weighting choice.

### 7.2 Why bubbles and hexbins rather than choropleths (requirements 57–59)

A choropleth shades polygons. The CSV contains points and text labels and no boundary geometry, and the course constraint permits no additional input files. Choropleths are therefore not buildable, not merely deprioritised.

Voronoi tessellation is explicitly rejected as a substitute. It would synthesise polygons from centroids and produce a map that looks authoritative while depicting boundaries that do not exist — the worst outcome available, since it is both wrong and convincing.

The two permitted forms are honest about what the data is. Centroid bubbles say "these listings share a label and this is roughly where they are." Hexbins discard the labels entirely and show where listings actually sit, which recovers the spatial detail the missing polygons would have carried. Together they cover most of what a choropleth would have shown.

Coast distance does not need a coastline shapefile. Eight hardcoded vertices approximate the LA County shore to well under a kilometre, and the analysis operates at neighbourhood scale where that error is irrelevant.

### 7.3 Other constraints

- **Price skew:** mean 225 vs. median 109, max 24,999. Always log-transform for modelling; report medians, not means, for description.
- **Revenue estimate sensitivity:** the Inside Airbnb formula multiplies by `minimum_nights`, and 32.1% of listings sit at 30+. This inflates estimates for exactly the segment most in need of characterisation, which is why both variants are required rather than one arbitrary cap.
- **TF-IDF `min_df`:** set to 20 to keep the vocabulary manageable over 33k short titles. Sensitivity-check at 10 and 50.
- **Topic model choice:** NMF is preferred over LDA for short documents. Airbnb titles average under 10 tokens, and LDA's Dirichlet prior behaves poorly at that length. If both are run, report the coherence scores for each.
- **Runtime:** 33k rows is small. Everything except the topic model should run in under two minutes; no optimisation work is warranted.

---

## 8. Success Metrics

1. Pipeline runs end-to-end from the raw CSV with a single command, with zero manual steps.
2. Neighbourhood table contains all 264 neighbourhoods with no unexpected nulls in computed indicator columns.
3. Hedonic regression achieves R² ≥ 0.35 with the majority of coefficients significant at p < 0.05 — a plausible bar for cross-sectional hedonic price models on this feature set.
4. Clustering produces a solution with mean silhouette score ≥ 0.25, and every cluster receives a label an independent reader can match to its centroid profile without being told.
5. Adjusted Rand index between family-weighted and PCA clustering solutions is reported, whatever its value.
6. `excluded_neighbourhoods.md` lists every excluded neighbourhood, states the total listings removed, and gives all three stated reasons.
7. Threshold sensitivity results at n = 50 / 100 / 200 are reported.
8. Derived topics are labelled and explicitly compared against the tourism / upmarket / commercial hypothesis.
9. All 10 figures render without manual adjustment and are legible at print size.
10. Repeated runs produce byte-identical CSV output.
11. `limitations.md` is generated and contains every item in §10.

---

## 9. Open Questions

_Both resolved — see below._

**Resolved:**

- **Reviews-per-stay constant (Q1)** — taken as given (the Inside Airbnb 0.5 convention). No 0.3 / 0.7 sweep: both revenue variants are exactly linear in the constant, so it rescales every neighbourhood's estimate by the same factor and changes no ranking or cluster. `limitations.md` §4 states this and tells a reader who prefers another value to rescale the two revenue columns directly. (task 8.8)
- **Neighbourhood fixed effects (Q2)** — **no.** Fitted both: `neighbourhood_group` (3 levels, HC3) gives R² 0.330 / adj 0.329; the 264-dummy variant gives R² 0.481 / adj 0.477 but is **inadmissible** — 7 single-listing neighbourhoods take leverage 1 once their dummy enters the design, so every HC3 standard error (req 44) is infinite. The req-43 model stays primary; FE is kept as a robustness note in `regression_summary.txt`. Consequence: success metric 3 is not met and the miss is accepted. (task 5.6)

- External files — none permitted; CSV is the sole input (§4.14)
- Choropleths — not buildable without boundary geometry; centroid bubbles + hexbin instead (§4.13, §7.2)
- Revenue cap — both capped and uncapped variants (§4.6)
- Keyword sets — TF-IDF + topic model, data-driven (§4.8)
- Neighbourhood threshold — n ≥ 100 with documented rationale and sensitivity check (§4.10)
- Clustering approach — family weighting, PCA as robustness check (§4.12, §7.1)
- Coastline geometry — hardcoded 8-vertex polyline (§4.2)

---

## 10. Known Data Quality Issues and Limitations

| Field                              | Issue                                                            | Handling                                                                                                                |
| ---------------------------------- | --------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `last_review`, `reviews_per_month` | 7,118 nulls (21.5%)                                              | Preserved as null; drives inactivity indicator                                                                          |
| `name`                             | 2 nulls                                                          | Skipped in tokenisation                                                                                                 |
| `host_name`                        | 9 nulls                                                          | Unused; no handling needed                                                                                              |
| `price`                            | 11 zeros; max 24,999                                             | Zeros dropped before log; winsorised at 1/99 for modelling                                                              |
| `availability_365`                 | 23.4% zeros, ambiguous meaning                                   | Reported; occupancy proxy flagged where share is high                                                                   |
| `minimum_nights`                   | Max 1,125; non-organic spike at exactly 30                       | Spike is itself the regulatory-evasion signal                                                                           |
| `neighbourhood_group`              | Only 3 values, LA County only                                    | Filename says "California"; analysis covers LA County                                                                   |
| Geometry                           | No boundary polygons in the CSV, and no external files permitted | Centroid bubbles + hexbin; choropleths not buildable                                                                    |
| All rows                           | Single snapshot, August 2020                                     | No temporal comparison possible; cross-sectional ranking only                                                           |
| All rows                           | Mid-pandemic scrape                                              | 44.7% of reviewed listings had no review since March 2020; inactivity figures reflect COVID, not local market character |

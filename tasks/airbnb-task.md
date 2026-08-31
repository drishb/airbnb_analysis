# Tasks: LA County Airbnb Market Structure Analysis Pipeline

Source PRD: `airbnb-prd.md`

**Codebase state:** Greenfield. No existing project, modules, or conventions to reuse. All structure is established by task 1.0.

## Relevant Files

- `run_analysis.py` - Single entry point (PRD req 65). Sets global seeds, creates output dirs, calls each stage in order.
- `src/config.py` - All literal constants: paths, seeds, thresholds, landmark coordinates, coastline polyline, indicator family map (PRD req 62).
- `src/ingest.py` - CSV load, schema validation, cleaning, data quality report (PRD req 1-6).
- `tests/test_ingest.py` - Unit tests for schema validation and cleaning logic.
- `src/geo.py` - Haversine distance and nearest-point-on-polyline. Pure NumPy, no geometry library (PRD req 8-9).
- `tests/test_geo.py` - Unit tests for distance calculations against known coordinate pairs.
- `src/indicators_numeric.py` - Tourism, host concentration, regulatory evasion, tenure, revenue, price, and inactivity indicators (PRD req 7-27, 35-36).
- `tests/test_indicators_numeric.py` - Unit tests for HHI, Gini, and revenue variants on hand-checked fixtures.
- `src/indicators_text.py` - Tokenisation, TF-IDF, NMF topic model, per-neighbourhood topic loadings (PRD req 28-34).
- `tests/test_indicators_text.py` - Unit tests for tokenisation and null-name handling.
- `src/aggregate.py` - Neighbourhood table assembly, low-confidence flagging, exclusion report, threshold sensitivity (PRD req 37-42).
- `tests/test_aggregate.py` - Unit tests for exclusion logic and threshold behaviour.
- `src/regression.py` - Hedonic log-price OLS with HC3 errors and diagnostics (PRD req 43-48).
- `src/clustering.py` - Family-weighted K-means, k selection, PCA robustness check, centroid labelling (PRD req 49-56).
- `tests/test_clustering.py` - Unit tests for the family weighting transform.
- `src/figures.py` - All matplotlib output: bubble maps, hexbin, histograms, diagnostics (PRD req 16, 22, 46, 57-60).
- `src/report.py` - Writes `limitations.md` and assembles markdown outputs (PRD req 67).
- `requirements.txt` - Pinned dependency versions (PRD req 68).
- `README.md` - Setup instructions including one-time `nltk.download()` if NLTK is used (PRD req 63).

### Notes

- This is a Python project, so tests live in a top-level `tests/` directory rather than alongside source files — the Python convention, and a deviation from the `generate-tasks.md` template which assumes Jest.
- Run tests with `pytest`. Run a single file with `pytest tests/test_ingest.py`.
- Run the full pipeline with `python run_analysis.py` from the project root.
- Every stage writes to `outputs/`. Delete that directory to force a clean run.
- Verify PRD req 64 by disconnecting from the network and re-running after environment setup.

## Tasks

- [x] 1.0 Project scaffolding, configuration, and data ingestion

    - [x] 1.1 Create the directory structure: `src/`, `tests/`, `data/`, `outputs/figures/`, and `src/__init__.py`.
    - [x] 1.2 Write `src/config.py` with paths, `RANDOM_SEED`, `EXPECTED_COLUMNS`, winsorisation percentiles, and analysis thresholds (req 38, 41, 20).
    - [x] 1.3 Add `LANDMARKS` and `COASTLINE` literal constants to `config.py`, each with a source comment (req 62).
    - [x] 1.4 Write `load_raw()` in `src/ingest.py`: read the CSV, parse `last_review` as datetime, validate the 16 expected columns, raise a clear `SchemaError` on mismatch (req 1-2).
    - [x] 1.5 Write `clean()`: drop `price == 0` rows with a logged count, add `price_winsorized` and `log_price` columns, assert nulls were preserved (req 3-5).
    - [x] 1.6 Write `quality_report()`: per-column null/zero/min/max table, price treatment summary, preserved-null explanation, structural caveats (req 6).
    - [x] 1.7 Write `run_analysis.py` with `set_seeds()` and a `main()` that calls ingestion (req 65, 69).
    - [x] 1.8 Four decisions resolved: Catalina excluded from the polyline and flagged via `is_island`; winsorisation left at 1/99; column validation stays strict; review-field consistency showcased in the quality report.
    - [x] 1.9 Write `tests/test_ingest.py` covering missing-column failure, unexpected-column behaviour, zero-price drop count, and null preservation.
    - [x] 1.10 Generate `requirements.txt` with pinned versions (req 68).

- [x] 2.0 Numeric indicator computation

    - [x] 2.1 Write `src/geo.py` with a vectorised haversine function, unit-tested against two known coordinate pairs.
    - [x] 2.2 Add `nearest_point_on_polyline()` to `src/geo.py`: per-segment projection in NumPy, returning distance to the closest point on the `COASTLINE` polyline (req 9).
    - [x] 2.3 Compute per-listing distance to all four landmarks and to the coast; aggregate to neighbourhood medians (req 8, 10).
    - [x] 2.4 Compute tourism indicators per neighbourhood: mean and median `reviews_per_month`, mean `number_of_reviews`, entire-home share (req 7).
    - [x] 2.5 Compute host concentration: HHI over `host_id` shares, share held by hosts with 10+ listings, top-5-host share, multi-listing-host share (req 11-14).
    - [x] 2.6 Compute the `minimum_nights >= 30` share per neighbourhood (req 15).
    - [x] 2.7 Compute listing tenure as `number_of_reviews / reviews_per_month`, aggregate to a neighbourhood median, and record the supporting listing count (req 18-19).
    - [x] 2.8 Compute both revenue variants — uncapped and capped at 5 nights — as separate columns that are never combined (req 20-21). Medians taken over reviewed listings only; `rev_supporting_listings` records the count.
    - [x] 2.9 Identify and record the neighbourhoods with the largest capped/uncapped revenue divergence (req 23).
    - [x] 2.10 Compute the booked-days proxy and the `availability_365 == 0` share, flagging neighbourhoods where the proxy is unreliable (req 24-25).
    - [x] 2.11 Compute price structure: median, IQR, coefficient of variation, and Gini per neighbourhood, plus median price by room type (req 26-27). Hotel- and shared-room medians are descriptive only — too sparse for clustering, listed in `config.DESCRIPTIVE_ONLY_COLUMNS`.
    - [x] 2.12 Compute inactivity: no-review share and pre-March-2020 last-review share, with _inactivity_ in every column name (req 35-36).
    - [x] 2.13 Write `tests/test_indicators_numeric.py` verifying HHI and Gini against hand-computed fixtures.

- [x] 3.0 Text-derived indicators

    - [x] 3.1 Write tokenisation in `src/indicators_text.py`: lowercase, strip punctuation, remove stopwords, handle the 2 null names without error (req 28).
    - [x] 3.2 Fit a TF-IDF vectoriser over all listing titles with unigrams and bigrams and `min_df=20` (req 29). Place names and room-type nouns are suppressed; the unsuppressed baseline is retained and reported as the evidence for that choice.
    - [x] 3.3 Compute the mean TF-IDF vector per neighbourhood and extract the top 15 distinguishing terms (req 30).
    - [x] 3.4 Fit NMF over the TF-IDF matrix for k in 5-8, select k by coherence score, and record the justification (req 31). k=5 selected; the margin over the runner-up is reported because coherence discriminates weakly here.
    - [x] 3.5 Write the topic-term table and assign each topic a human-readable label after inspecting its terms (req 32).
    - [x] 3.6 Compute per-neighbourhood topic loadings as indicator columns (req 33).
    - [x] 3.7 Compare the derived topics against the tourism / upmarket / commercial hypothesis and state in `topic_model.md` whether they corroborate or contradict it (req 34).
    - [x] 3.8 Run `min_df` sensitivity at 10 and 50 and record whether the topics are stable (PRD §7.3).

- [ ] 4.0 Neighbourhood aggregation and exclusion reporting

    - [x] 4.1 Assemble all indicators into a single neighbourhood table, one row per neighbourhood (req 37).
    - [x] 4.2 Add a listing-count column and a low-confidence flag at n < 100 (req 38).
    - [ ] 4.3 Populate `INDICATOR_FAMILIES` in `config.py` now that every indicator column name is known — needed by task 6.0's weighting.
    - [ ] 4.4 Implement exclusion: filter low-confidence neighbourhoods from ranked output, clustering, and maps, while retaining all 264 in the exported table (req 39).
    - [ ] 4.5 Write `excluded_neighbourhoods.md` with the excluded list, listing counts, total listings removed, and the three stated reasons — rate instability, mechanical HHI inflation, clustering distortion (req 40).
    - [ ] 4.6 Run the full ranking and clustering at n = 50, 100, and 200 and report how many neighbourhoods change cluster assignment between thresholds (req 41).
    - [ ] 4.7 Export the neighbourhood table to `outputs/neighbourhood_indicators.csv` (req 42).
    - [ ] 4.8 Write `tests/test_aggregate.py` for exclusion logic and threshold behaviour.

- [ ] 5.0 Hedonic price regression

    - [ ] 5.1 Build the model frame: `log_price` against room type, minimum nights, availability, host listing count, review count, and neighbourhood group, on all listings rather than only retained neighbourhoods (req 43, 48).
    - [ ] 5.2 Fit OLS with HC3 robust standard errors (req 44).
    - [ ] 5.3 Write the coefficient table with standard errors, t-statistics, p-values, R-squared, and n to `outputs/regression_summary.txt` (req 45).
    - [ ] 5.4 Convert log coefficients to approximate percentage price effects and include both forms in the output (req 47).
    - [ ] 5.5 Produce residuals-vs-fitted and Q-Q diagnostic plots (req 46).
    - [ ] 5.6 Decide the open question on neighbourhood fixed effects: fit with and without 264 dummies, compare adjusted R-squared, and record the choice (PRD §9.2).

- [ ] 6.0 Neighbourhood clustering

    - [ ] 6.1 Standardise all neighbourhood features to zero mean and unit variance (req 49).
    - [ ] 6.2 Implement family weighting: divide each standardised feature by the square root of its family size, using `INDICATOR_FAMILIES` (req 50).
    - [ ] 6.3 Run k from 2 to 10, produce elbow and silhouette plots, select k, and record the justification (req 51).
    - [ ] 6.4 Fit K-means with the fixed seed (req 52).
    - [ ] 6.5 Run PCA-based clustering retaining 85% variance and compute the adjusted Rand index against the family-weighted solution (req 53).
    - [ ] 6.6 Write the centroid table in original units, not standardised ones (req 54).
    - [ ] 6.7 Assign post-hoc cluster labels from centroid profiles and document that they were assigned after fitting (req 55).
    - [ ] 6.8 List member neighbourhoods per cluster in `outputs/cluster_summary.md` (req 56).
    - [ ] 6.9 Write `tests/test_clustering.py` verifying that the weighting transform equalises family contribution to the distance metric.

- [ ] 7.0 Figure generation

    - [ ] 7.1 Write a shared figure helper in `src/figures.py`: consistent viridis colourmap, 150 dpi, and a caption on every figure noting the August 2020 snapshot and the pandemic caveat (req 61, PRD §6).
    - [ ] 7.2 Build the centroid bubble map function — one marker per retained neighbourhood at its mean lat/long, sized by listing count, coloured by indicator (req 57).
    - [ ] 7.3 Render bubble maps for median price, host HHI, tourism intensity, 30-night-minimum share, and cluster assignment (req 57).
    - [ ] 7.4 Render the hexbin density map over raw lat/long, independent of neighbourhood labels (req 58).
    - [ ] 7.5 Render the `minimum_nights` histogram capped at 90, annotated at the spike at exactly 30 (req 16).
    - [ ] 7.6 Render the capped-vs-uncapped revenue scatter (req 22).
    - [ ] 7.7 Verify no Voronoi or synthesised boundary geometry appears anywhere in the codebase (req 59).
    - [ ] 7.8 Confirm all 10 figures render at 150 dpi and are legible at print size (req 60).

- [ ] 8.0 Output assembly, reproducibility, and documentation

    - [ ] 8.1 Wire every stage into `run_analysis.py` in dependency order (req 65).
    - [ ] 8.2 Confirm all artefacts land in `outputs/` per the PRD §6 layout (req 66).
    - [ ] 8.3 Write `src/report.py` to generate `limitations.md` containing every item in PRD §10 (req 67).
    - [ ] 8.4 Pin all dependency versions in `requirements.txt` (req 68).
    - [ ] 8.5 Seed NumPy, scikit-learn, and NMF initialisation globally, then verify two consecutive runs produce byte-identical CSV output (req 69, success metric 10).
    - [ ] 8.6 Write `README.md` with setup steps, including one-time `nltk.download()` if NLTK is used (req 63).
    - [ ] 8.7 Verify the pipeline runs with no network access after environment setup (req 64).
    - [ ] 8.8 Check every success metric in PRD §8 and record pass or fail for each.

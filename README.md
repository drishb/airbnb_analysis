# LA County Airbnb Market Structure Analysis

Pipeline for the PRD in `tasks/airbnb-prd.md`. Task list in `tasks/airbnb-task.md`.
Every design choice and its reasoning is in `DECISIONS.md`.

It ingests one Inside Airbnb snapshot (`listings_California.csv`, ~33k LA
County listings, scraped ~August 2020) and produces neighbourhood-level
indicator tables, a hedonic price regression, a family-weighted K-means
segmentation, and ten static figures — all from a single command.

**Status:** tasks 1.0–8.0 complete. `pytest` → 45 passing.

## Setup

```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt      # Windows
# .venv/bin/pip install -r requirements.txt        # macOS / Linux

mkdir -p data && cp /path/to/listings_California.csv data/
```

No other input file is needed. Landmark coordinates and the coastline
polyline are literal constants in `src/config.py`. Stopword removal uses
scikit-learn's built-in English list — **no `nltk.download()` and no
network access is required** once the packages are installed.

## Run

```bash
python run_analysis.py          # full pipeline, writes everything to outputs/
pytest                          # 45 tests
pytest tests/test_geo.py        # one file
```

Delete `outputs/` to force a completely clean run. Repeated runs produce
byte-identical `neighbourhood_indicators.csv` and a byte-identical
`regression_summary.txt` (the wall-clock fields in the statsmodels block
are blanked for this reason).

## Outputs (`outputs/`)

```
neighbourhood_indicators.csv     264 neighbourhoods × 44 columns (all retained + flagged)
data_quality_report.md           null/zero/outlier table, price treatment, caveats
excluded_neighbourhoods.md       the 185 n<100 neighbourhoods, why, threshold sensitivity
regression_summary.txt           hedonic OLS: coefficients, HC3 errors, % price effects, FE note
cluster_summary.md               k selection, centroid table, member lists, PCA robustness
topic_model.md                   TF-IDF + NMF topics, hypothesis check, min_df sensitivity
limitations.md                   every PRD §10 constraint, restated
figures/
  map_median_price.png              map_host_hhi.png            map_tourism_intensity.png
  map_min_nights_30.png             map_clusters.png            hexbin_listing_density.png
  hist_minimum_nights.png           scatter_revenue_capped_vs_uncapped.png
  elbow_silhouette.png              residual_diagnostics.png
```

## Layout (`src/`)

```
config.py               all constants: paths, seed, thresholds, landmarks,
                        coastline, indicator families, suppressed vocabulary, cluster labels
ingest.py               load, validate, clean, quality report (req 1–6)
geo.py                  haversine + nearest-point-on-polyline, NumPy only (req 8–9)
indicators_numeric.py   7 numeric indicator families → neighbourhood table (req 7–27, 35–36)
indicators_text.py      TF-IDF + NMF topic model, per-neighbourhood loadings (req 28–34)
aggregate.py            table assembly, low-confidence flag, exclusion, CSV export (req 37–42)
regression.py           hedonic log-price OLS, HC3, % effects, fixed-effects comparison (req 43–48)
clustering.py           standardise → family-weight → K-means, PCA check, labels (req 49–56)
figures.py              all matplotlib output: maps, hexbin, histograms, diagnostics (req 16, 22, 46, 57–60)
report.py               limitations.md (req 67)
```

## Notes

- Dataset is LA County only, despite the "California" filename
  (`neighbourhood_group` has just 3 values).
- Single snapshot, ~August 2020, mid-pandemic. **No change over time is
  measurable** — every output is cross-sectional.
- No external data files. No `geopandas`, no `shapely` — there is no
  boundary geometry to manipulate, so maps are centroid bubbles + a hexbin,
  never choropleths and never Voronoi.
- Two success metrics are not met and the misses are documented in the
  relevant output files: hedonic R² = 0.33 (< 0.35 bar) and cluster mean
  silhouette ≈ 0.19 (< 0.25 bar). See `regression_summary.txt` and
  `cluster_summary.md`.

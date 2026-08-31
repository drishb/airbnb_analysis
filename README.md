# LA County Airbnb Market Structure Analysis

Pipeline for the PRD in `tasks/airbnb-prd.md`. Task list in `tasks/airbnb-task.md`.
Every design choice and its reasoning is in `DECISIONS.md`.

**Status:** tasks 1.0–3.0 complete. 29 tests passing. Tasks 4.0–8.0 not built.

## Setup

```bash
pip install -r requirements.txt
mkdir -p data && cp /path/to/listings_California.csv data/
```

No other input file is needed. Landmark coordinates and the coastline
polyline are literal constants in `src/config.py`.

## Run

```bash
python run_analysis.py     # full pipeline
pytest                     # 29 tests
pytest tests/test_geo.py   # one file
```

## Layout

```
run_analysis.py             entry point, sets global seeds
src/config.py               all constants: paths, thresholds, landmarks,
                            coastline, suppressed vocabulary
src/ingest.py               load, validate, clean, quality report
src/geo.py                  haversine + nearest-point-on-polyline (NumPy only)
src/indicators_numeric.py   7 indicator families -> 264 x 37 table
src/indicators_text.py      TF-IDF + NMF topic model
tests/                      pytest
outputs/                    generated artefacts
```

## Built so far

| Task | Module | Output |
|---|---|---|
| 1.0 | `ingest.py` | 33,067 clean rows, `data_quality_report.md` |
| 2.0 | `geo.py`, `indicators_numeric.py` | 264 x 37 neighbourhood table, 79 above n>=100 |
| 3.0 | `indicators_text.py` | 5 topics, 264 x 5 loadings, `topic_model.md` |

## Still to build

4.0 aggregation and exclusion reporting · 5.0 hedonic regression ·
6.0 clustering · 7.0 figures · 8.0 output assembly

## Notes

- Dataset is LA County only, despite the filename.
- Single snapshot, ~August 2020, mid-pandemic. No change over time is measurable.
- No external data files. No geopandas, no shapely — there is no boundary
  geometry to manipulate.

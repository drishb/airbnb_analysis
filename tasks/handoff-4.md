# Handoff — resume at task 5.4

Read `tasks/airbnb-prd.md` and `tasks/airbnb-task.md` first. This file
covers what changed since the earlier `airbnb handoff.md` (which took
things to the end of task 3.0). Working style rules there still apply:
one sub-task at a time, surface decisions, wait for agreement, mark done.

## Environment

- `.venv/` at repo root, Python 3.14, all `requirements.txt` pins installed.
  `tabulate==0.10.0` is in requirements (`df.to_markdown()` in `indicators_text`).
- Data present at `data/listings_California.csv` (33,078 rows). Not committed.
- Run: `.venv/Scripts/python.exe -m pytest -q` → **39 passed**
  (was 29; +10 from `tests/test_aggregate.py`).
- `.venv/Scripts/python.exe run_analysis.py` still only runs ingestion;
  stages 2.0+ are not wired into it yet (that is task 8.1).

## Structure

`src/*.py` (package, `from . import config`), `tests/test_*.py`,
`outputs/`, `data/`. `src/__init__.py`, `.gitignore` present.

Caveat carried over: an IDE auto-save race once truncated `src/config.py`
right after an edit. Re-check file length after editing `config.py`.

## Progress

| Task | Status |
|---|---|
| 1.0–3.0 | done (unchanged) |
| 4.1 assemble table | done |
| 4.2 low-confidence flag | done |
| 4.3 `INDICATOR_FAMILIES` | done |
| 4.4 exclusion helpers | done |
| 4.5 `excluded_neighbourhoods.md` | done |
| 4.6 threshold sensitivity | **deferred** — needs clustering (6.0) |
| 4.7 export CSV | **done** |
| 4.8 `tests/test_aggregate.py` | **done** |
| 5.1 model frame | **done** |
| 5.2 fit OLS + HC3 | **done** |
| 5.3 `regression_summary.txt` | **done** |
| 5.4 % price effects | **next** |
| 5.5 residual diagnostics plots | after 5.4 |
| 5.6 neighbourhood fixed-effects decision | after 5.5 |

Task 4.0 is left unchecked in `airbnb-task.md` because 4.6 is still open.

## 4.3 decision (unchanged, agreed with user)

`INDICATOR_FAMILIES` in `config.py` is an explicit 8-family map,
**31 clustering features**: tourism 9 · host_concentration 4 · regulatory 2
· tenure 1 · revenue_occupancy 4 · price 4 · inactivity 2 · text 5.
`DESCRIPTIVE_ONLY_COLUMNS` is 13 entries. The two sets cover all 44 table
columns exactly; `build_table` → `_validate_columns` raises on drift.

## `src/aggregate.py` — current API

- `build_table(df, loadings=None) -> 264 x 44` — numeric ⨝ topic loadings,
  inserts `low_confidence` at col 1, runs `_validate_columns`.
- `feature_columns() -> list[str]` — the 31, in family order.
- `exclude_low_confidence(tbl, threshold=None) -> DataFrame` — filtered
  view for ranked output / clustering / maps. Never mutates `tbl`,
  returns a real copy. `threshold` param exists for 4.6.
- `feature_frame(tbl, threshold=None) -> retained x 31` — raises on any
  null feature in a *retained* row; tolerates nulls in excluded rows.
- `export_table(tbl, path=None)` — **new (4.7)**. Writes all 264 rows to
  `outputs/neighbourhood_indicators.csv`. Index written as a
  `neighbourhood` column (`index_label="neighbourhood"`). Column order =
  table as `build_table` assembled it (count/flag/geo, then families in
  `INDICATOR_FAMILIES` order with descriptive siblings interleaved, then
  `topic_*_loading`). Rows alphabetical by neighbourhood. **No
  `float_format`** — full round-trip precision; verified byte-identical
  across two runs (success metric 10). Excluded-neighbourhood nulls → empty
  fields.
- `write_exclusion_report(tbl, sensitivity=None, path=None)` — writes
  `outputs/excluded_neighbourhoods.md`. `sensitivity` is the 4.6 table;
  None → section says "pending task 4.6".

Numbers: 79 retained / 185 excluded at n≥100. Exclusion removes 5,658 of
33,067 listings (17.1%). Thresholds: 50→127, 100→79, 200→45 retained.

### `tests/test_aggregate.py` (4.8) — 10 tests

`feature_columns()` matches `INDICATOR_FAMILIES` and is 31 long; default
threshold retains n≥100 not n=99; override to 50/200; `exclude_low_confidence`
does not mutate and returns a copy that can be written without touching
`tbl`; `SENSITIVITY_THRESHOLDS` retain monotonically fewer; `feature_frame`
raises on a null feature in a retained row, tolerates one in an excluded
row; `export_table` keeps low-confidence rows and is byte-identical on
rerun. Fixture builds a synthetic table directly (no full pipeline run).

## `src/regression.py` — new file (task 5.0), current API

- `FORMULA` — `log_price ~ C(room_type, Treatment("Entire home/apt")) +
  minimum_nights + availability_365 + calculated_host_listings_count +
  number_of_reviews + C(neighbourhood_group, Treatment("City of Los
  Angeles"))`. Exact form from req 43. Reference levels made explicit
  (patsy's alphabetical default happens to pick the same two — modal room
  type, largest group); coefficients read "versus that baseline".
- `MODEL_COLUMNS` — the 7 columns the formula needs.
- `build_model_frame(df) -> 33067 x 7` — all cleaned listings, no
  neighbourhood exclusion (req 48). Raises if `log_price` absent or any
  model column null. Confirmed zero nulls (`number_of_reviews` is 0 not
  null for unreviewed; `reviews_per_month` — the null-bearing field — is
  not in the model).
- `fit_model(frame)` — `smf.ols(FORMULA, data=frame).fit(cov_type="HC3")`
  (req 44). HC3 at fit time, so `.bse/.tvalues/.pvalues/.conf_int()` are
  robust; point estimates and R² unchanged. Returns the
  `RegressionResultsWrapper`.
- `write_summary(results, path=None) -> str` — **5.3**. Annotated header
  (formula, reference levels, HC3 + winsorised-response notes) + the
  `statsmodels` summary → `outputs/regression_summary.txt`. Robust cov →
  the per-coefficient statistic is asymptotic **z**, labelled as such
  (req 45 says "t-statistics"; z is the correct robust analogue).

### Fit results (current, `neighbourhood_group` only — no 264 dummies)

- n = 33,067 · **R² = 0.330** · adj R² = 0.329 · all 9 coefficients p < 0.05.
- Signs: Private room −0.918 log units (≈ −60% vs. entire home),
  Shared room −1.622, Hotel room −0.431; `minimum_nights`,
  `number_of_reviews`, `calculated_host_listings_count` each slightly
  negative; `availability_365` slightly positive; Other Cities ≈ 0
  (p = 0.036), Unincorporated Areas −0.092.
- statsmodels prints a condition-number warning (3.4e3) — driven by
  predictor scale differences (`availability_365` 0–365 vs. 0/1 dummies),
  not real collinearity. Not addressed; standardising would break the
  req-47 percentage-effect reading.

## Pending decisions / open items

1. **R² = 0.330 < success-metric-3's 0.35 bar.** Not a blocker yet.
   Task 5.6 fits with vs. without 264 neighbourhood dummies and compares
   adj R²; the fixed-effects variant is expected to clear 0.35. If it
   does, that likely becomes the reported model. Decide at 5.6 and record.
2. **`regression_summary.txt` is not byte-identical across runs** — the
   statsmodels block prints `Date:` / `Time:`. Success metric 10 only
   requires the *CSV* to be byte-identical, so this is currently left as
   is. Open question: strip those two lines in `write_summary` for
   all-artefacts reproducibility? User was asked, not yet answered.
3. **4.6 still deferred** — the n = 50/100/200 cluster-stability table
   needs task 6.0. `write_exclusion_report` takes a `sensitivity` arg and
   currently writes a "pending" paragraph; wire the real table through
   once clustering exists.
4. **PRD §9 open question 1** (sensitivity-test the 0.5 reviews-per-stay
   constant) — still unaddressed; not assigned to a numbered task.

## Uncommitted right now

`src/aggregate.py` (4.5 + 4.7), `src/regression.py` (new, 5.1–5.3),
`tests/test_aggregate.py` (new), `tasks/airbnb-task.md` (4.7/4.8/5.1–5.3
ticks), `outputs/neighbourhood_indicators.csv` (new/regenerated),
`outputs/regression_summary.txt` (new), `outputs/excluded_neighbourhoods.md`
(untracked), `tasks/handoff-4.md` (this file).
Last commit: `0ce65ed adding excluded neighbourhoods`.

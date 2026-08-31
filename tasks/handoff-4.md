# Handoff — resume at task 4.7

Read `tasks/airbnb-prd.md` and `tasks/airbnb-task.md` first. This file only
covers what changed since the earlier `airbnb handoff.md` (which took things
to the end of task 3.0). Working style rules in that file still apply:
one sub-task at a time, surface decisions, wait for agreement, mark done.

## Environment

- `.venv/` at repo root, Python 3.14, all `requirements.txt` pins installed.
  **`tabulate==0.10.0` was added** to requirements — `indicators_text`
  calls `df.to_markdown()` and it was missing.
- Data present at `data/listings_California.csv` (33,078 rows). Not committed.
- Run: `.venv/Scripts/python.exe -m pytest -q` → **29 passed**
  (the previously-skipped geo test now runs — pandas is installed).
- `.venv/Scripts/python.exe run_analysis.py` still only runs ingestion;
  stages 2.0+ are not wired into it yet (that is task 8.1).

## Structure change

Everything was flat in the repo root with empty `src/config.py` /
`src/ingest.py` stubs. Now matches the intended layout:
`src/*.py` (package, `from . import config`), `tests/test_*.py`,
`outputs/`, `data/`. `src/__init__.py` added. `.gitignore` added.
`tasks/airbnb-prd.md` and `tasks/airbnb-task.md` created from the source
docs (they were not in the repo before).

Caveat: an IDE auto-save race once truncated `src/config.py` to 26 lines
right after an edit. Recovered with `git checkout HEAD -- src/config.py`.
Watch for it; re-check file length after editing `config.py`.

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
| 4.7 export CSV | next |
| 4.8 `tests/test_aggregate.py` | after 4.7 |

## 4.3 decision (agreed with user)

`INDICATOR_FAMILIES` in `config.py` is an explicit 8-family map,
**31 clustering features**:

```
tourism 9 · host_concentration 4 · regulatory 2 · tenure 1
revenue_occupancy 4 · price 4 · inactivity 2 · text 5
```

Three deviations from a pure column-prefix rule:
1. `rev_` + `occ_` are one family (PRD Goal 2 lists "revenue/occupancy" as one).
2. `rev_divergence_ratio` → `DESCRIPTIVE_ONLY_COLUMNS` (it is
   uncapped/capped, both already features — triple-counts revenue).
3. `price_median_<room_type>` → `DESCRIPTIVE_ONLY_COLUMNS` (req 26's four
   stats are the structural ones; req 27 breakouts are detail).

`DESCRIPTIVE_ONLY_COLUMNS` is now 13 entries. Together the two sets cover
all 44 table columns exactly — `build_table` calls `_validate_columns`
which raises if that ever drifts.

## `src/aggregate.py` — current API

- `build_table(df, loadings=None) -> 264 x 44` — numeric ⨝ topic loadings,
  inserts `low_confidence` at col 1, runs `_validate_columns`.
- `feature_columns() -> list[str]` — the 31, in family order.
- `exclude_low_confidence(tbl, threshold=None) -> DataFrame` — filtered
  view for ranked output / clustering / maps. Never mutates `tbl`.
  `threshold` param exists for 4.6.
- `feature_frame(tbl, threshold=None) -> retained x 31` — raises on any
  null feature.
- `write_exclusion_report(tbl, sensitivity=None, path=None)` — writes
  `outputs/excluded_neighbourhoods.md`. `sensitivity` is the 4.6 table;
  None → section says "pending task 4.6".

Numbers: 79 retained / 185 excluded at n≥100. Exclusion removes 5,658 of
33,067 listings (17.1%). Thresholds: 50→127, 100→79, 200→45 retained.
`feature_frame` is 79×31 with zero nulls.

## 4.7 (next)

Export the full 264-row `tbl` (all neighbourhoods, not just retained —
req 39/42) to `outputs/neighbourhood_indicators.csv`. Decide: index
(`neighbourhood`) as a column; column order; float formatting for
byte-identical reruns (success metric 10 — but global seeding is task 8.5,
so just don't do anything nondeterministic here).

## Uncommitted right now

`src/aggregate.py` (4.5 additions), `tasks/airbnb-task.md` (4.5 tick),
`outputs/excluded_neighbourhoods.md` (untracked). Last commit:
`0ce65ed adding excluded neighbourhoods`.

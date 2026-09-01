# Handoff — pipeline complete (tasks 7.0 + 8.0)

Read `tasks/airbnb-prd.md` and `tasks/airbnb-task.md` first. Trail:
- `handoff-4.md` — through task 5.3
- `handoff-5.md` — tasks 5.4–5.6, all of 6.0, 4.6
- this file — **all of 7.0 and 8.0. The task list is now fully checked.**

## Status

| Task | Status |
|---|---|
| 1.0–6.0 | done (unchanged) |
| 7.0 figures (7.1–7.8) | **done** |
| 8.0 assembly / repro / docs (8.1–8.8) | **done** |

`.venv/Scripts/python.exe run_analysis.py` runs the whole pipeline
end-to-end from the raw CSV and writes every artefact to `outputs/`.
`.venv/Scripts/python.exe -m pytest -q` → **45 passed** (no new tests this
round; the figure/report code is exercised by the full run).

## Environment

Unchanged from handoff-5. `.venv/`, Python 3.14, `requirements.txt` pins
all match the installed venv exactly (checked in 8.4). Data at
`data/listings_California.csv`, not committed.

## What was built

### `src/figures.py` — new functions (7.2–7.6)

- `centroid_bubble_map(retained, values, *, title, legend_label, name,
  categorical=False, category_labels=None)` — req 57. Marker **area**
  (not radius) tracks `listing_count`. Axis extent is computed from the
  points (`_extent`), so Avalon on Catalina (~35 km offshore, bottom of
  frame) is always visible. Continuous branch clips the colour scale to
  the **2nd/98th percentile** with `extend` arrows on the colour bar —
  without this, Avalon's host HHI (0.42 vs a mainland max ~0.08) flattened
  every mainland marker to one colour. Legends sit outside the tall/narrow
  geographic axes: indicator legend upper-left (categorical) or colour bar
  right (continuous), listing-count size key lower-right.
- `hexbin_density(df)` — req 58. gridsize 60, `bins="log"`, `mincnt=1`,
  extent from all listing coords (the 169 Catalina listings show as a
  separate southern cluster).
- `min_nights_histogram(df)` — req 16. Capped at 90, dashed line +
  annotation at 30 (7,974 listings / 24.1%), 266 listings above 90 noted
  in the title.
- `revenue_capped_vs_uncapped(retained)` — req 22. Capped x vs uncapped y
  per retained neighbourhood, 45° reference line; every point is above it.

All go through the existing `save()` (caption + 150 dpi + Agg). `numpy`
now imported at module top.

### `src/report.py` — new file (8.3, 8.8)

- `write_limitations(df)` → `outputs/limitations.md` (req 67). §10 field
  table with figures recomputed live from the frame, plus §7.3 estimator
  caveats, the two metric misses, out-of-scope note.
- `write_success_metrics(tbl, results, diag, pca_result, cluster_labels)`
  → `outputs/success_metrics.md` (task 8.8). Every PRD §8 metric evaluated
  against live objects / on-disk artefacts. Writes a scratch
  `_repro_check.csv` for the metric-10 byte check and unlinks it in the
  same call.

### `run_analysis.py` — full wiring (8.1)

All stages in dependency order (see the module docstring). `write_summary`
before `compare_neighbourhood_fixed_effects` (append order matters).
Imports `aggregate, clustering, config, figures, indicators_text, ingest,
regression, report`.

### `src/regression.py` — determinism fix (8.5)

`_deterministic_summary(results)` blanks the statsmodels `Date:` / `Time:`
fields (width-preserving regex) so `regression_summary.txt` is
byte-identical between runs. Used in `write_summary`.

### Encoding fix (8.5)

`src/indicators_text.py` and `src/ingest.py` `write_text` calls were
missing `encoding="utf-8"` — Windows wrote cp1252 for the em-dashes, which
broke `report.py` reading them back and made cross-platform output
non-identical. All file writes in `src/` now pin utf-8.

## Results / decisions this round

### 7.3 — "tourism intensity" map column
Used `tour_reviews_per_month_mean` (booking velocity). The other tourism
features are landmark distances, which a map would just re-draw as
geography.

### 7.7 — Voronoi check (req 59)
Grepped `voronoi|tessellat|delaunay|convexhull|alpha_shape|choropleth|
shapefile|geojson` and `geopandas|shapely|scipy.spatial` imports. **Zero
matches** except comments/docs stating the pipeline does not do this.

### 8.2 — output layout
All seven PRD §6 files + the 10 named figures. Added
`outputs/success_metrics.md` (task 8.8 needs it written somewhere; not in
the §6 list). `outputs/*.md`, `*.csv`, `*.txt` are git-tracked; only
`outputs/figures/*.png` is gitignored (`.gitkeep` keeps the dir).

### 8.7 — offline check
No networking imports/calls anywhere. Ran the full pipeline with
`socket.socket.connect` / `socket.create_connection` monkey-patched to
raise → completed, all artefacts written.

### 8.8 — success metrics: **9 of 11 met**
- **FAIL 3** — hedonic R² = 0.330 < 0.35. Fixed req-43 formula; FE variant
  inadmissible under HC3. Documented, accepted (task 5.6).
- **FAIL 4** — cluster mean silhouette = 0.194 < 0.25. Intrinsic to the
  data (unweighted peaks at 0.20). Documented, accepted (task 6.3).
- All 9 others PASS, including 10 (byte-identical CSV — and in fact every
  text artefact is byte-identical across runs now).

### PRD §9 open questions — both resolved
Q1 (0.5 constant): taken as given, linearity note in `limitations.md`.
Q2 (fixed effects): no. PRD §9 and `DECISIONS.md` updated.

## Known cosmetic issues (not blocking)

- On `map_host_hhi.png` / `map_min_nights_30.png` the lower-right size-key
  legend sits very close to the Avalon marker at the bottom of the frame.
  Avalon is still visible in every map. Left as is.
- `map_clusters.png` legend labels are long (`config.CLUSTER_LABELS`); they
  fit at the current figure size but there is little margin.

## Uncommitted right now

- new: `src/report.py`, `tasks/handoff-6.md`, `outputs/limitations.md`,
  `outputs/success_metrics.md`
- modified: `run_analysis.py`, `src/figures.py`, `src/regression.py`,
  `src/indicators_text.py`, `src/ingest.py`, `README.md`, `DECISIONS.md`,
  `tasks/airbnb-prd.md`, `tasks/airbnb-task.md`,
  `outputs/data_quality_report.md`, `outputs/topic_model.md`,
  `outputs/regression_summary.txt` (+ `cluster_summary.md`,
  `excluded_neighbourhoods.md`, `neighbourhood_indicators.csv` regenerated
  but byte-identical)
- figures: all 10 regenerated, gitignored by `outputs/figures/*.png`

Branch level with `origin/main`. `git add -A && git commit && git push`.
Last commit: `433a408 add handoff-5: decisions through tasks 5.6, 6.0, 4.6`.

## If more work is wanted

The task list is fully checked. Candidates for a follow-up pass, none
required by the PRD:
- A `tests/test_figures.py` (smoke test each figure function on a small
  synthetic frame — currently only the full run exercises them).
- A `tests/test_report.py` for the metric-check logic.
- Revisit the two accepted metric misses only if the PRD's fixed
  constraints (req 43 formula, family-weighting) are relaxed.

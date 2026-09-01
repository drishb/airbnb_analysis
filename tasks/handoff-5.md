# Handoff — resume at task 7.2

Read `tasks/airbnb-prd.md` and `tasks/airbnb-task.md` first. Then the two
earlier handoffs for the trail:
- `airbnb handoff.md` — through end of task 3.0
- `handoff-4.md` — through task 5.3
- this file — tasks 5.4, 5.5, 7.1, 5.6, **all of 6.0**, and 4.6

Working style unchanged: one sub-task at a time, surface decisions, wait
for agreement, mark done in `airbnb-task.md`.

## Environment

- `.venv/` at repo root, Python 3.14, `requirements.txt` pins installed.
- **`requirements.txt` gained `scipy==1.18.1`** (task 4.6 uses
  `scipy.optimize.linear_sum_assignment` directly; it was already present
  transitively via sklearn/statsmodels, now pinned explicitly).
- Data at `data/listings_California.csv` (33,078 rows). Not committed.
- Run tests: `.venv/Scripts/python.exe -m pytest -q` → **45 passed**
  (was 39; +6 from `tests/test_clustering.py`).
- `run_analysis.py` still only runs ingestion. Stages 2.0+ are not wired
  in — that is task 8.1, still open.
- Caveat carried over from handoff-4: an IDE auto-save race truncated
  `src/config.py` once, and truncated `src/ingest.py` in a later commit
  (recovered via `git checkout <prev> -- src/ingest.py`, now committed
  whole at 226 lines). **Re-check file length after editing any `src/`
  file**, especially `config.py`.

## Progress

| Task | Status |
|---|---|
| 1.0–3.0 | done |
| 4.0 aggregation + exclusion | **done** (4.6 was the last piece) |
| 4.6 threshold sensitivity | **done** (needed 6.0) |
| 5.0 hedonic regression | **done** |
| 5.4 % price effects | done |
| 5.5 residual diagnostic plots | done |
| 5.6 neighbourhood fixed-effects decision | done |
| 6.0 clustering (6.1–6.9) | **done** |
| 7.1 shared figure helper | done (built early, during 5.5) |
| 7.2–7.8 remaining figures | **next** |
| 8.0 assembly / reproducibility / docs | not started |

## Decisions since handoff-4 (all agreed with the user)

### 5.4 — percentage price effects (req 47)
Report **both** forms, exact emphasised: `approx_pct = 100·β` and
`exact_pct = 100·(exp(β)−1)`. Approx overstates badly for the room-type
dummies (Private room −92% approx vs −60% exact). `percentage_effects()`
also carries the HC3 CI bounds through the exact transform.

### 5.5 / 7.1 — figures
Built `src/figures.py` (task 7.1's shared helper) **before** 5.5 rather
than quick-and-dirty plotting in `regression.py`. One `save()` path for
all ten figures: wraps `config.FIGURE_CAPTION`, writes
`outputs/figures/<name>.png` at `config.FIGURE_DPI` (150),
`bbox_inches="tight"`, closes. Module forces the **Agg** backend
(offline/headless) and sets **viridis** as the rc default cmap;
`FIGURE_CMAP_CATEGORICAL = "tab10"` for clusters.

### 5.6 — neighbourhood fixed effects (PRD §9 Q2)  ← important
Ran both. Base (`neighbourhood_group`, HC3): R² 0.330 / adj 0.329. FE
(264-level `neighbourhood`, `FE_REFERENCE_NEIGHBOURHOOD = "Venice"`):
R² 0.481 / adj 0.477 — fits much better.

**Decision: base stays the PRIMARY reported model. FE is inadmissible
here.** 7 neighbourhoods have exactly 1 listing (Cudahy, Hawaiian Gardens,
Lake Hughes, Northwest Antelope Valley, Ridge Route, South Diamond Bar,
Whittier Narrows). Once each gets a dummy, that row has leverage 1, so
HC3's `1/(1−h)²` weight is undefined and **every HC3 standard error in the
FE fit is infinite**. Req 44 mandates HC3; req 48 mandates all listings;
req 43 pins the formula. FE is kept as a robustness note in
`regression_summary.txt` (NEIGHBOURHOOD FIXED EFFECTS section).

**Consequence: success metric 3 (R² ≥ 0.35) is NOT MET and the miss is
accepted** — the reported model is 0.330, the formula is fixed, FE can't
rescue it admissibly. Flagged near the top of `regression_summary.txt`
and to be recorded in task 8.8.

### 6.1 — standardise (req 49)
`StandardScaler` (population std, ddof = 0). Composable step 1.

### 6.2 — family weighting (req 50)
**Two composable steps**, not a fused `prepare_features()`:
`family_weight(standardize(frame))`. Divide each standardised feature by
√(family size). Post-condition asserted: each of the 8 families
contributes total feature variance exactly 1.0.

### 6.3 — k selection (req 51)  ← important
Silhouette is **flat and low across all k** (~0.19 peak, weighted or
unweighted — inherent to the data, 79 neighbourhoods on 31 correlated
indicators). Inertia has no sharp elbow. **k = 5 selected**
(`config.CLUSTER_K`): tied-best silhouette (0.194, = k=2), local peak,
inertia knee, 5 nameable market types, matches the NMF topic count.

**Consequence: success metric 4 (mean silhouette ≥ 0.25) is NOT MET and
the miss is accepted** — recorded in `cluster_summary.md`, to be recorded
in task 8.8. Segmentation is reported as a descriptive grouping, not a
claim of sharp natural boundaries.

### Avalon (Santa Catalina Island)
**Kept in the clustering.** It forms its own 1-member cluster (id 2) from
k ≥ 4 — genuine extreme outlier (host HHI z ≈ +8.4, top-5 share 79%,
35 km offshore, $450 median, already `is_island`-flagged). User chose
keep-in over exclude-as-outlier. Removing it does not rescue the
silhouette.

### 6.5 — PCA robustness check (req 53)
PCA runs on the **standardised, unweighted** matrix (the alternative to
family weighting, per §7.1 — not the weighted one, which would double-count
the family correction). 9 components = 86.8% variance. **ARI = 0.298**
vs the family-weighted solution — partial agreement: central/tourist
cluster + Avalon stable across both, the outer/upmarket/inner split is
method-sensitive. Reported whatever the value (success metric 5 satisfied).

### 6.7 — cluster labels (req 55)
**Hand-written constants** in `config.CLUSTER_LABELS` (keyed by the
cluster id the fixed seed produces), each with its centroid evidence in a
comment. `label_clusters(centroids)` **guards** them against fit drift —
argmax/argmin checks on identifying features (reg_min_nights→0,
price_gini→3, host_hhi & n_neighbourhoods→2, tenure→4, cheapest→1); raises
rather than mislabel silently. Labels:
- 0 — Long-stay / regulation-exempt core
- 1 — Outer suburban budget, owner-hosted
- 2 — Island resort, single operator (Avalon)
- 3 — Upmarket hillside & Westside
- 4 — Established high-turnover tourist

### 6.9 — clustering tests
Synthetic fixture (`_feature_frame`, no full pipeline run). 6 tests, key
one: `test_family_weight_equalises_distance_contribution` — pairwise
squared-distance contribution per family, unweighted spread > 3×,
weighted < 1.6×.

### 4.6 — threshold sensitivity (req 41)  ← important
**Count only** (not ARI), **k held fixed at 5** across all thresholds so
the comparison isolates the threshold. Per pair, Hungarian-align cluster
ids by max overlap on common neighbourhoods, count reassignments.

Result: 50→100 **18/79 (23%)**, 100→200 **18/45 (40%)**, 50→200
**19/45 (42%)**. **The threshold IS load-bearing** for the fine
partition. Wired into `aggregate.write_exclusion_report(sensitivity=…)`
with interpretation tying it to the ~0.19 silhouette / ~0.30 ARI: broad
segmentation stable, mid-cluster membership not. n ≥ 100 retained; readers
told to treat near-boundary membership as approximate.

## `src/clustering.py` — full API (new file, task 6.0 + 4.6)

Module forces nothing; imports `aggregate, config, figures` (no cycle).

- `standardize(frame) -> DataFrame` — 6.1. StandardScaler ddof=0, asserts
  zero-mean/unit-variance output.
- `family_weight(frame) -> DataFrame` — 6.2. `/√(family size)` per
  feature. `_feature_family_size()` maps feature → family size from
  `config.INDICATOR_FAMILIES`. Asserts per-family variance sum == 1.0.
- `_kmeans(k) -> KMeans` — one constructor, `random_state=RANDOM_SEED`,
  `n_init=config.KMEANS_N_INIT` (10). Every fit in the module uses it.
- `k_diagnostics(weighted) -> DataFrame` — 6.3. Sweeps
  `config.CLUSTER_K_RANGE` (2..10), columns `inertia`, `silhouette`,
  indexed by k.
- `fit_kmeans(weighted, k=None) -> (model, labels)` — 6.4. k defaults to
  `config.CLUSTER_K`. `labels` is an int Series indexed by neighbourhood.
  Sizes at k=5: 26 / 22 / 15 / 15 / 1. Silhouette 0.194.
- `pca_clustering(standardized, weighted_labels, k=None) -> dict` — 6.5.
  Keys: `n_components`, `variance_explained`, `ari`, `pca_labels`,
  `pca_silhouette`.
- `centroid_table(feature_frame, labels, tbl=None) -> DataFrame` — 6.6.
  5×31 group-mean of **raw** features + `n_neighbourhoods` / `n_listings`
  (when `tbl` passed). Indexed by cluster id.
- `label_clusters(centroids) -> dict[int, str]` — 6.7. Returns
  `config.CLUSTER_LABELS` after the guard checks pass.
- `write_summary(centroids, labels, assignments, diag, pca_result,
  path=None) -> str` — 6.8. Writes `outputs/cluster_summary.md`:
  k-justification + sweep table, silhouette-miss caveat, label table,
  31-row centroid table (original units), member lists, PCA/ARI section.
- `threshold_sensitivity(tbl, thresholds=None, k=None) -> DataFrame` —
  4.6. Rows: adjacent pairs + widest pair. Columns `threshold_low`,
  `threshold_high`, `n_common`, `n_changed`, `pct_changed`. Feeds
  `write_exclusion_report`.
- helpers: `_cluster_at_threshold`, `_count_reassigned` (Hungarian id
  match), `_n_meta`.
- `figures.plot_k_selection(diag, selected_k, name=...)` — twin-axis
  elbow+silhouette → `outputs/figures/elbow_silhouette.png`.

## `src/config.py` — additions

- `FIGURE_DPI = 150`, `FIGURE_CMAP = "viridis"`,
  `FIGURE_CMAP_CATEGORICAL = "tab10"`, `FIGURE_CAPTION` (fixed caption
  string — August 2020 snapshot + pandemic caveat).
- `CLUSTER_K_RANGE = list(range(2, 11))`, `CLUSTER_K = 5`,
  `PCA_VARIANCE_RETAINED = 0.85`, `KMEANS_N_INIT = 10`.
- `CLUSTER_LABELS` — dict {0..4: label}, with a long evidence comment
  block above it.

## `src/regression.py` — additions since handoff-4

- `percentage_effects(results) -> DataFrame` + `_format_percentage_effects`
  — 5.4. Appended to `regression_summary.txt` by `write_summary`.
- `CONTINUOUS_PREDICTORS` set (labels "per +1 unit" vs "vs. reference").
- `FORMULA_FE`, `FE_REFERENCE_NEIGHBOURHOOD = "Venice"`,
  `MODEL_COLUMNS_FE`, `build_model_frame(df, fixed_effects=False)`,
  `fit_model(frame, formula=FORMULA)` (now takes a formula arg).
- `compare_neighbourhood_fixed_effects(df, path=None) -> dict` — 5.6.
  Appends the NEIGHBOURHOOD FIXED EFFECTS section to
  `regression_summary.txt`. **Run it after `write_summary`**, which
  truncates the file.
- `write_summary` header now carries the "success metric 3 NOT MET" note.

## `src/figures.py` — current API

- `save(fig, name, caption=None, dpi=None) -> Path` — the shared exit.
- `residual_diagnostics(results, name="residual_diagnostics.png")` — 5.5.
- `plot_k_selection(diag, selected_k, name="elbow_silhouette.png")` — 6.3.
- rcParams set at import (dpi, viridis, font sizes); Agg backend forced.

## `src/aggregate.py` — change since handoff-4

`write_exclusion_report(tbl, sensitivity=None, path=None)` — the
`sensitivity is not None` branch now renders the 4.6 table with a lead-in
and an interpretation paragraph (load-bearing conclusion, cross-ref to
`cluster_summary.md`). `sensitivity` is the `threshold_sensitivity`
frame.

## Output files regenerated / new

- `outputs/regression_summary.txt` — 5.4 % effects + 5.6 FE section +
  metric-3 note.
- `outputs/figures/residual_diagnostics.png` — new (5.5).
- `outputs/figures/elbow_silhouette.png` — new (6.3).
- `outputs/cluster_summary.md` — new (6.8).
- `outputs/excluded_neighbourhoods.md` — 4.6 sensitivity section filled.
- `outputs/neighbourhood_indicators.csv` — unchanged (still byte-identical
  across reruns, success metric 10).

## Pending decisions / open items

1. **Success metrics 3 and 4 both MISS**, both accepted and documented in
   their output files. Task 8.8 must record pass/fail for every metric —
   3 (R² ≥ 0.35 → 0.330) and 4 (silhouette ≥ 0.25 → 0.19) are FAIL, with
   the reasons already written. Metric 5 (report ARI) PASS. Metric 7
   (threshold sensitivity reported) PASS.
2. **`regression_summary.txt` is still not byte-identical across runs** —
   statsmodels prints `Date:` / `Time:` lines. Carried over from
   handoff-4 item 2, still unanswered. Success metric 10 only requires the
   **CSV** to be byte-identical, so currently left as is. Decide in 8.5:
   strip those two lines in `write_summary` for full-artefact repro?
3. **PRD §9 open question 1** (sensitivity-test the 0.5 reviews-per-stay
   constant at 0.3 / 0.7) — still unaddressed, not assigned to a numbered
   task. Raise before 8.8.
4. **`run_analysis.py` wires in nothing past ingestion** — task 8.1.
   When wiring the regression stage: `write_summary(results)` first, then
   `compare_neighbourhood_fixed_effects(df)` (append order matters).
5. **7.7** requires a grep for Voronoi / synthesised boundary geometry —
   there is none, but the check must be run and recorded.

## Next: task 7.2

Centroid bubble-map function in `src/figures.py` — one marker per retained
neighbourhood at its mean lat/long (`centroid_lat` / `centroid_lon` are in
the table, `DESCRIPTIVE_ONLY_COLUMNS`), sized by `listing_count`, coloured
by an indicator, viridis, through `save()`. Then 7.3 renders it for median
price, host HHI, tourism intensity, 30-night-min share, and clusters;
7.4 hexbin; 7.5 min-nights histogram; 7.6 revenue scatter; 7.7 Voronoi
check; 7.8 confirm all 10 figures at 150 dpi.

## Uncommitted right now

User ran `git add .` earlier (stale partial snapshot). Everything to
stage and commit:
- new: `src/clustering.py`, `tests/test_clustering.py`,
  `outputs/cluster_summary.md`, `tasks/handoff-5.md`
- modified: `src/config.py`, `src/figures.py`, `src/regression.py`,
  `src/aggregate.py`, `requirements.txt`, `tasks/airbnb-task.md`,
  `outputs/regression_summary.txt`, `outputs/excluded_neighbourhoods.md`
- NOT committed (gitignored via `outputs/figures/*.png`):
  `elbow_silhouette.png`, `residual_diagnostics.png` — regenerated by the
  pipeline, so this is intended.

Branch is level with `origin/main` — **no rebase needed**. Just
`git add -A && git commit && git push`.
Last commit: `125b266 converting log prices to percentage pricing, resolve bad push task 5.4`.

# Decision Log

Every non-obvious choice made while scoping and building this pipeline, and why. Ordered by when it came up.

Status: tasks 1.0–3.0 complete, 29 tests passing. Tasks 4.0–8.0 not yet built.

---

## Phase 1 — Scoping

### 1. The research question was changed

**Asked:** which LA areas are more touristy, gentrified, or losing their charm.

**Built instead:** how short-term rental market structure differs across neighbourhoods.

**Why:** gentrification and "losing charm" are *change over time*. The dataset is one snapshot — `last_review` maxes at 2020-08-21 and there is no earlier observation. Change cannot be inferred from a single point. Every output is therefore phrased as cross-sectional ranking, never as a trajectory.

A second reason: 21.5% of listings have never been reviewed, and 44.7% of reviewed listings had no review after March 2020. Any neighbourhood that looks like it is declining is showing the pandemic, not local character.

### 2. The dataset is LA County, not California

Despite the filename. `neighbourhood_group` holds only City of Los Angeles (19,075), Other Cities (11,496), and Unincorporated Areas (2,507). Nothing in the analysis claims statewide scope.

### 3. No supervised model

There is no target variable and no ground truth. Inventing an `is_gentrified` label and training against it would make the model validate its own premise circularly. The pipeline is descriptive statistics, one hedonic regression, and unsupervised clustering.

### 4. Python rather than gretl

gretl is built for time-series and panel econometrics; this is cross-sectional. It has no geospatial support, so lat/long would be unusable, and no text mining, so 33k listing titles would be inaccessible. Cleaning and aggregation would have to happen in pandas regardless, making gretl a second toolchain for no gain. It would be adequate for the hedonic regression alone, but `statsmodels` produces equivalent output in the same codebase.

### 5. Non-Goals trimmed, not deleted

`create-prd.md` mandates the section. Three items were kept because they are real scope boundaries a developer needs — no dashboard, no interactive maps, no external data joins. The rest, including a proposed ban on the words "gentrifying" and "declining" in generated output, was cut as overreach.

---

## Phase 2 — Constraints

### 6. Choropleth maps abandoned

A choropleth shades polygons. The CSV has points and text labels, no boundary geometry. Inside Airbnb publishes `neighbourhoods.geojson` separately, but no external file is permitted.

Replaced with centroid bubble maps (one marker per neighbourhood, sized by listing count) plus a hexbin over raw lat/long that ignores labels entirely.

**Voronoi tessellation was explicitly rejected** as a substitute. It would synthesise polygons from centroids and produce a map that looks authoritative while depicting boundaries that do not exist — both wrong and convincing, the worst combination.

### 7. `geopandas` and `shapely` dropped

Both exist to manipulate boundary geometry, of which there is none. Nearest-point-on-polyline is roughly ten lines of NumPy. Dropping them also removes a GDAL dependency chain that breaks routinely on Windows.

### 8. `nltk` — banned, then un-banned

Initially prohibited on the grounds that `nltk.download('stopwords')` is an external data fetch. **That was an overreach on my part.** The constraint is about analysis data — no geojson, no census join. A stopword list is a package resource, not analysis data.

Now optional, with one practical note retained: run `nltk.download()` at environment setup rather than from analysis code, so the pipeline stays offline-runnable and does not fail on a grader's machine behind a proxy. scikit-learn's built-in list is used in practice, so the dependency is not needed.

---

## Phase 3 — Task 1.0, ingestion

### 9. Catalina Island: flagged, not dropped; coast distance set to zero

169 listings sit in Avalon (149) and Unincorporated Catalina Island (20), roughly 35 km offshore.

Catalina is deliberately absent from the coastline polyline. Measuring these listings to the mainland would report ~35 km for beachfront property.

Setting their `dist_coast_km` to **0.0** rather than null was chosen over three alternatives:

| Option | Rejected because |
|---|---|
| Exclude from clustering | Avalon has 149 listings, above the n≥100 threshold — it belongs in the analysis |
| Leave as null | K-means cannot accept NaN, forcing imputation later |
| Add Catalina to the polyline | Would let mainland listings compute distances to an island 35 km offshore |

Zero is not a workaround. These listings *are* coastal; the question the feature asks is "how far from the coast," and the answer is zero.

### 10. Winsorisation left at 1st/99th percentile

Bounds land at $22–$2,316, clipping only 331 of 33,067 listings, while 906 listings exceed $1,000/night. Tightening to 5/95 was considered and rejected — LA genuinely contains Malibu estates, and aggressive clipping would erase real high-end supply rather than data errors.

Raw `price` is retained for descriptive statistics; `price_winsorized` and `log_price` are used only for modelling.

### 11. Column validation is strict

The loader rejects both missing *and* unexpected columns. A CSV with an extra column appended fails rather than warning. Chosen deliberately: silent schema drift is worse than a loud failure, and the error message names the offending columns.

### 12. Review-field consistency showcased, not just noted

Three fields encode the same fact — `number_of_reviews == 0`, `last_review` null, `reviews_per_month` null — and they agree on exactly 7,118 rows.

Surfaced as a table in the quality report because of the practical consequence: **these are one signal, not three.** Any composite score treating them as independent would triple-count unreviewed listings. Downstream code uses `number_of_reviews == 0` alone.

### 13. Nulls asserted, not just preserved

`clean()` contains `assert df["last_review"].isna().sum() > 0`. A later refactor that imputes these would silently destroy the market-inactivity indicator. The assertion makes that failure loud.

---

## Phase 4 — Task 2.0, numeric indicators

### 14. Revenue medians computed over reviewed listings only

The Inside Airbnb formula multiplies by review count. Where more than half a neighbourhood is unreviewed, the median collapses to exactly zero regardless of prices or occupancy. Avalon is 59.1% unreviewed; its median revenue computed over all listings was **$0**, and `rev_divergence_ratio` was a 0/0 NaN.

Excluding unreviewed listings gives Avalon $7,380 on 61 supporting listings, and no retained neighbourhood has a structurally-zero median.

**The reasoning:** the estimator is undefined for a listing with no reviews. It is not estimating zero revenue — it is estimating nothing. Counting those rows as zeros asserts something the formula cannot support. `rev_supporting_listings` records the count, matching the pattern already used for tenure.

### 15. Both revenue variants kept, never combined

Uncapped uses `minimum_nights` as the formula specifies. Capped limits that multiplier to 5. With 32.1% of listings at 30+ nights, the uncapped figure inflates badly for exactly the segment most worth characterising. Capping at an arbitrary value is equally indefensible, so both are reported with a divergence ratio flagging where they disagree most.

### 16. Hotel- and shared-room price medians are descriptive only

Only 18 of 79 retained neighbourhoods contain any hotel rooms; 67 contain shared rooms. K-means cannot accept NaN, and imputing a hotel price for a neighbourhood with no hotels would fabricate data.

They remain in the exported table — the data is real where it exists — but sit in `config.DESCRIPTIVE_ONLY_COLUMNS` and never reach clustering.

**Payoff:** the clustering-eligible feature set is now 29 columns with **zero nulls** across all 79 retained neighbourhoods. No imputation is needed anywhere in task 6.0.

### 17. Count columns excluded from clustering

`listing_count`, `rev_supporting_listings`, and `tenure_supporting_listings` are counts, not rates. Clustering on them would re-encode neighbourhood size, which is not a market-structure property.

### 18. HHI's floor documented at the point of definition

`hhi()` ranges from 1/n to 1. A ten-listing neighbourhood cannot register as unconcentrated even with ten distinct hosts. This is one of the three reasons for the n≥100 threshold, and the docstring says so where a reader will encounter it.

### 19. Equirectangular projection for point-to-segment, haversine for landmarks

At LA County's scale the two differ by under 0.1%. Point-to-segment distance is far cleaner in planar coordinates, so the polyline work projects locally; landmark distances use full haversine since there is no reason not to.

The projection parameter is clamped with `np.clip(t, 0, 1)` so a point off the north end of Malibu does not project onto the segment's infinite extension. Tested explicitly.

---

## Phase 5 — Task 3.0, text mining

### 20. Keyword lists replaced with TF-IDF and NMF

Hardcoded tourism / upmarket / commercial word lists were the original plan. Replaced with a derived topic model so the categories are an output to be tested, not an input that guarantees itself.

### 21. Place names and room-type nouns suppressed from the vocabulary

**This is the most consequential choice in the text pipeline.**

Fitting NMF over the raw vocabulary produced 8 topics, of which 6 were place names or room types — "santa monica", "private room", "guest house". Those are not findings. They are `neighbourhood`, `room_type`, and the five distance columns from task 2.0, recovered from the titles. Using them as clustering features would weight geography twice, on top of four landmark distances and a coast distance already present.

Suppressing that vocabulary leaves marketing *register*: cozy/clean/quiet, modern/luxury/pool/ocean, beautiful/master/spacious, near-LAX/near-studios, heart-of/charming/sunny. That is information the structured columns do not contain, which is the only defensible reason to mine text at all.

**Both runs are reported in `topic_model.md`.** The suppression is a researcher choice, not something the data dictated. Omitting the baseline would present a decision as if it were a finding; including it makes the choice reviewable.

### 22. NMF over LDA

Listing titles average under 10 tokens. LDA's Dirichlet prior behaves poorly on documents that short.

### 23. Coherence reported with its margin

Suppression changed the selected k from 8 to 5. The four candidate k values span 0.17 of coherence and the metric trends with k — its known failure mode. The margin over the runner-up (0.136) is printed alongside the selection so a reader can see how thin it is rather than reading k=5 as a clean optimum.

### 24. The hypothesis mostly failed, and the output says so

Across five derived topics: **zero** tourism-term hits, **zero** commercial hits, and only `luxury` and `modern` landing in topics 1 and 4.

The tourism signal was real in the baseline run — but as place names, which is geography, not marketing language. The prior was roughly two-thirds wrong, and `topic_model.md` states this plainly rather than reporting only the third that worked.

### 25. `min_df` sensitivity is mediocre and recorded as such

Mean topic overlap against the reference fit is 0.68 at `min_df=10` and 0.73 at `min_df=50`; worst-case single-topic overlap is 0.43. The topics are recognisably similar across settings but not stable. Usable as clustering features, not a firm structure — and belongs in the limitations section, not buried.

---

## Deviations from the provided rule files

| Rule file | Deviation | Reason |
|---|---|---|
| `generate-tasks.md` | Tests in top-level `tests/`, not alongside source | Python convention; the rule assumes a JS/Jest layout |
| `generate-tasks.md` | `pytest`, not `npx jest` | Python project |
| `create-prd.md` | Non-Goals trimmed to three items | See decision 5 |

---

## Open decisions, not yet made

1. Should the 0.5 reviews-per-stay constant be sensitivity-tested at 0.3 and 0.7, or taken as the Inside Airbnb convention?
2. Should the hedonic regression include 264 neighbourhood dummies alongside `neighbourhood_group`? Some neighbourhoods hold under 10 listings, so those coefficients would be estimated off almost nothing. Current lean is no — `neighbourhood_group` plus the five distance features should absorb most spatial variation.

---

## Reversals

Recorded because a decision log that only contains decisions that held is not an honest one.

- **`nltk` ban** (decision 8) — reversed. Conflated package resources with analysis data.
- **Non-Goals word ban** — cut before implementation. Banning "gentrifying" from generated output and enforcing it by grep was overreach; the constraint belongs in how conclusions are phrased, not in a lint rule.
- **Test bound in `test_geo.py`** — Santa Monica Pier to LA City Hall was asserted at ~19.6 km. The correct figure is 24.0 km (4.98 km north, 23.49 km east). The test was wrong, not the code.

# Key Findings — LA County Airbnb Market Structure

Derived from the pipeline outputs in `outputs/` (bundled in `outputs.zip`).
Source data: one Inside Airbnb snapshot of LA County, ~August 2020,
33,067 cleaned listings. **Everything here is cross-sectional** — a
description of the market at one moment, not a trend. The scrape is
mid-pandemic; see the caveats at the end.

Analysis is on the **79 neighbourhoods with ≥ 100 listings** (27,409
listings, 82.9% of the market). The other 185 neighbourhoods are retained
in the CSV but excluded from rankings and clustering — see
`excluded_neighbourhoods.md`.

---

## 1. A large, deliberate 30-night regulatory workaround, concentrated in the dense central core

**Evidence** — `hist_minimum_nights.png`, `map_min_nights_30.png`,
`cluster_summary.md`:

- **7,974 listings (24.1% of all listings) sit at *exactly* 30 nights** —
  a sharp, non-organic spike; 32% are at 30 or more.
- LA's 2019 Home-Sharing Ordinance caps a short-term rental at 120
  nights/year and requires the host's primary residence. **A 30-night
  minimum exempts a listing from both rules.** The spike is a response to
  regulation, not a distribution of genuine demand.
- Clustering isolates a **"long-stay / regulation-exempt core"** — 15
  neighbourhoods, 6,777 listings: *Koreatown, Hollywood, East Hollywood,
  Mid-Wilshire, Westwood, West LA, Santa Monica, Sawtelle, Brentwood,
  Pico-Robertson, Beverly Grove, Exposition Park, Harvard Heights,
  Arlington Heights, Hermosa Beach.* In **12 of these 15**, the *median*
  listing requires a 30-night minimum stay. Cluster-wide: 55% of listings
  at 30+ nights, lowest tourist review velocity of any cluster.
- Extremes: **Manhattan Beach 94%** of listings at 30+, West LA 69%,
  Harvard Heights / Exposition Park 63%.

**So what** — This is housing stock operating as de-facto furnished
corporate/medium-term rental under an Airbnb listing, positioned to stay
outside the STR ordinance. It clusters in dense, central, transit-served
neighbourhoods — precisely where the displaced use is long-term housing.

---

## 2. LA is not one short-term-rental market — it is five, and they are geographically coherent

**Evidence** — `cluster_summary.md`, `map_clusters.png`. Family-weighted
K-means, k = 5, labels assigned after inspecting centroids:

| Cluster | n hoods | n listings | Defining profile |
|---|--:|--:|---|
| **Long-stay / regulation-exempt core** | 15 | 6,777 | median 30-night minimum, central, low tourist velocity, 29% of listings held by hosts with 10+ listings |
| **Outer suburban budget, owner-hosted** | 26 | 7,429 | cheapest (median $83), farthest out (~28 km from Hollywood), 2-night minimums, few multi-listing operators |
| **Island resort, single operator** | 1 | 149 | Avalon / Catalina — see finding 3 |
| **Upmarket hillside & Westside** | 15 | 5,218 | highest median price ($256), highest price inequality (Gini 0.59, IQR $454), 73% entire-home — *Beverly Hills, Malibu, Bel-Air, Pacific Palisades, the Hollywood Hills* |
| **Established high-turnover tourist** | 22 | 7,836 | most reviews per listing (42), highest estimated revenue, longest tenure (~35 months), highest booked-days proxy — *Venice, Silver Lake, West Hollywood, Echo Park, Studio City, Manhattan Beach* |

**Robustness** — the mean silhouette is modest (~0.19), so this is a
*descriptive grouping*, not a claim of hard boundaries. But the broad
shape is stable: an independent PCA-based clustering agrees on the core
and the Avalon singleton (adjusted Rand index 0.30), and the split is
recognisable by eye on the map. Membership of neighbourhoods near the
edges of the middle three clusters should be treated as approximate
(threshold sensitivity: up to 42% of mid-size neighbourhoods move cluster
if the ≥100 rule is changed — `excluded_neighbourhoods.md`).

**So what** — A researcher can reason about five market logics instead of
79 neighbourhoods, and each maps to a distinct policy concern: housing
conversion (core), affordable-supply exposure (suburban budget),
second-home lock-up (upmarket), and tourism dependence (tourist).

---

## 3. Within-neighbourhood host concentration is near zero everywhere — except one island

**Evidence** — `map_host_hhi.png`, `neighbourhood_indicators.csv`,
`cluster_summary.md`:

- The Herfindahl index of host shares has a **median of 0.011** and is
  **below 0.10 in all 78 mainland neighbourhoods** (below 0.05 in 74 of
  them) — no single host dominates any mainland neighbourhood.
- **Avalon (Santa Catalina Island) is the lone exception: HHI 0.42, the
  top 5 hosts hold 79% of listings, 75% of listings belong to hosts with
  10+ listings.** A 149-listing island economy run by a handful of
  operators. It is a genuine structural outlier on almost every axis
  (median price $450, 97% entire-home, 59% never reviewed, 84 km from
  Hollywood) and forms its own one-member cluster.

**But concentration ≠ absence of professional operators.** The right
measure is the *multi-listing-host* share: in the regulation-exempt core,
**29% of listings belong to hosts running 10+ listings** (West LA 55%,
Arlington Heights 45%, Westwood 39%), versus **8%** in the tourist
cluster. Professionalisation in LA shows up not as neighbourhood
monopoly but as mid-size operators running 30-night "corporate housing"
portfolios across the central core (ties to finding 1).

---

## 4. What you rent explains price; where you rent barely does

**Evidence** — `regression_summary.txt`, `residual_diagnostics.png`.
Hedonic OLS of log price on room type, minimum nights, availability, host
listing count, review count, and neighbourhood group (HC3 errors, n =
33,067, R² = 0.33):

| Attribute | Effect on nightly price |
|---|---|
| Private room vs. entire home/apt | **−60%** |
| Shared room vs. entire home/apt | **−80%** |
| Hotel room vs. entire home/apt | −35% |
| Neighbourhood group (Other Cities / Unincorporated vs. City of LA) | **−9% to +2%** |
| +1 minimum night / +1 review / +1 host listing | ≈ −0.15% each |
| +1 day of availability | +0.07% |

- **Room type dwarfs every other term.** The three coarse
  `neighbourhood_group` buckets move price by under 10%.
- Adding all 264 neighbourhood dummies raises R² from 0.33 to 0.48
  (+0.15). So micro-location *does* carry real price signal — it is just
  not captured by the 3-way grouping, and the full fixed-effects model is
  inadmissible here (7 single-listing neighbourhoods break the robust
  standard errors — `regression_summary.txt`).
- Residuals are heavy-tailed (skew 1.2, kurtosis 5.2): a hedonic model on
  these six attributes explains about a third of nightly-price variation,
  and unmodelled property-level quality is the rest.

**So what** — For "what would a property in area X command," the listing's
*type* and its *specific* neighbourhood matter; the broad
City/Other/Unincorporated split is close to useless as a price predictor.

---

## 5. The revenue estimate is least trustworthy exactly where it matters most

**Evidence** — `scatter_revenue_capped_vs_uncapped.png`,
`neighbourhood_indicators.csv`:

- The Inside Airbnb revenue formula multiplies by `minimum_nights`. Two
  variants are reported and never combined: **uncapped** (formula as-is)
  and **capped** (multiplier limited to 5 nights).
- Every retained neighbourhood sits *above* the 45° line — uncapped
  always exceeds capped — but the gap is wildly uneven. Largest
  divergences: **Manhattan Beach 5.3×**, Exposition Park 3.9×, West LA
  3.5×, Palms 3.5×, Pico-Robertson 3.3×.
- These are the **same neighbourhoods as finding 1** — the ones with the
  highest 30-night shares. Their listings' "minimum nights" is a legal
  device, not a booking pattern, so multiplying revenue by it inflates
  the estimate several-fold.

**So what** — Any revenue ranking of LA neighbourhoods is dominated by an
artefact of the regulatory workaround. The regulation-exempt core looks
like the highest-earning segment under the uncapped formula and a
middling one under the capped formula; the truth is unknowable from this
data, and the divergence itself is the honest headline.

---

## 6. The "inactive" listings are concentrated in the high-end second-home segment

**Evidence** — `neighbourhood_indicators.csv`, `data_quality_report.md`:

- 21.5% of all listings have **never** been reviewed; 44.7% of reviewed
  listings had **no review after March 2020**.
- Highest never-reviewed shares: **Avalon 59%, Beverly Crest 45%, Beverly
  Hills 41%, Brentwood 37%, Manhattan Beach 35%, Encino 34%** — the
  upmarket / island clusters.
- The tourist cluster (Venice, Silver Lake, etc.) has the *lowest*
  never-reviewed share (~18%) and the *highest* post-COVID staleness
  (~41%) — listings that were busy and then stopped.

**So what** — Two different mechanisms wear the same "inactivity" label:
expensive homes that were always listed-but-rarely-booked (a standing
feature of that segment), and genuinely active tourist listings frozen by
the pandemic. Neither is neighbourhood *decline*. This is why the pipeline
names every such field *inactivity*, never *decline*, and why these
numbers cannot be read as a market-health signal.

---

## Caveats that bound every finding above

From `limitations.md`:

1. **One snapshot, ~August 2020.** No change over time is measurable. No
   finding here is a trajectory.
2. **Mid-pandemic scrape.** Activity, revenue, and occupancy proxies
   reflect COVID conditions, not baseline demand.
3. **Revenue and occupancy are model estimates**, not measured figures
   (finding 5).
4. **LA County only**, despite the "California" filename.
5. **No boundary geometry** — maps are centroid bubbles and a hexbin, not
   choropleths; spatial claims are at neighbourhood-centroid resolution.
6. The segmentation is a **descriptive grouping** (silhouette ~0.19), not
   a set of hard clusters (finding 2).

---

*Not included here:* the TF-IDF / NMF topic model of listing titles
(`topic_model.md`). The tested tourism / upmarket / commercial keyword
hypothesis was not corroborated — the derived topics recovered only
generic marketing register (*cozy, modern, near-LAX*), with near-zero
overlap with the prior. Reported for completeness in that file; it yields
no substantive market-structure finding.

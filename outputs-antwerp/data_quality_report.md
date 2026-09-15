# Data Quality Report

- Rows in raw file: **2,422**
- Rows after cleaning: **2,421**
- Dropped for `price == 0`: **1**

## Per-column summary (raw file)

| Column | dtype | Nulls | Null % | Zeros | Min | Max |
|---|---|---:|---:|---:|---:|---:|
| `id` | int64 | 0 | 0.0% | 0 | 5.09e+04 | 4.388e+07 |
| `name` | str | 1 | 0.0% | — | — | — |
| `host_id` | int64 | 0 | 0.0% | 0 | 2.341e+05 | 3.511e+08 |
| `host_name` | str | 1 | 0.0% | — | — | — |
| `neighbourhood_group` | float64 | 2,422 | 100.0% | 0 | nan | nan |
| `neighbourhood` | str | 0 | 0.0% | — | — | — |
| `latitude` | float64 | 0 | 0.0% | 0 | 51.16 | 51.35 |
| `longitude` | float64 | 0 | 0.0% | 0 | 4.342 | 4.486 |
| `room_type` | str | 0 | 0.0% | — | — | — |
| `price` | int64 | 0 | 0.0% | 1 | 0 | 4,600 |
| `minimum_nights` | int64 | 0 | 0.0% | 0 | 1 | 1,125 |
| `number_of_reviews` | int64 | 0 | 0.0% | 441 | 0 | 567 |
| `last_review` | datetime64[us] | 441 | 18.2% | — | 2011-09-19 | 2020-06-22 |
| `reviews_per_month` | float64 | 441 | 18.2% | 0 | 0.01 | 12.15 |
| `calculated_host_listings_count` | int64 | 0 | 0.0% | 0 | 1 | 42 |
| `availability_365` | int64 | 0 | 0.0% | 897 | 0 | 365 |

## Price treatment

- Winsorisation bounds (1% / 99%): **$20** to **$1,500**
- Listings clipped at the low bound: **20**
- Listings clipped at the high bound: **22**
- `price` retains raw values for descriptive statistics; `price_winsorized` and `log_price` are used for modelling.

## Preserved nulls (not imputed)

- `last_review`: **441** nulls
- `reviews_per_month`: **441** nulls

These are retained deliberately. A listing with no reviews has never been booked through the platform, which is the market-inactivity signal computed in section 4.9. Imputing them would erase it.

## Review-field consistency check

Three fields encode the same underlying fact — that a listing has never been reviewed — and they agree exactly:

| Condition | Listings |
|---|---:|
| `number_of_reviews == 0` | 441 |
| `last_review` is null | 441 |
| `reviews_per_month` is null | 441 |
| All three simultaneously | 441 |

**Agreement: exact.** The three are one signal, not three. Treating them as independent indicators would triple-count zero-review listings in any composite score, so downstream code uses `number_of_reviews == 0` alone.

## Island listings

- Flagged as `is_island`: **0** listings in .
- Santa Catalina Island sits roughly 35 km offshore and is excluded from the coastline polyline. Distance-to-coast is set to null for these listings rather than measured to the mainland.
- All other indicators are computed for them normally.

## Structural caveats

- Single cross-sectional snapshot, scraped approximately mid-2020. No change over time is measurable.
- Scrape falls mid-pandemic. Inactivity figures reflect COVID conditions, not local market character.
- Geographic coverage is Antwerp only (source file: `listings-Belgium.csv`).
- `availability_365 == 0` on **37.0%** of listings, and is ambiguous: fully booked, or host-blocked calendar.
- `minimum_nights >= 30` on **2.2%** of listings, 25 of them at exactly 30. See `limitations.md` for whether a specific local ordinance is known to attach to that threshold in this market.

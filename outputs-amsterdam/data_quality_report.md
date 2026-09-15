# Data Quality Report

- Rows in raw file: **18,949**
- Rows after cleaning: **18,949**
- Dropped for `price == 0`: **0**

## Per-column summary (raw file)

| Column | dtype | Nulls | Null % | Zeros | Min | Max |
|---|---|---:|---:|---:|---:|---:|
| `id` | int64 | 0 | 0.0% | 0 | 2,818 | 4.496e+07 |
| `name` | str | 33 | 0.2% | — | — | — |
| `host_id` | int64 | 0 | 0.0% | 0 | 3,159 | 3.63e+08 |
| `host_name` | str | 55 | 0.3% | — | — | — |
| `neighbourhood_group` | float64 | 18,949 | 100.0% | 0 | nan | nan |
| `neighbourhood` | str | 0 | 0.0% | — | — | — |
| `latitude` | float64 | 0 | 0.0% | 0 | 52.29 | 52.43 |
| `longitude` | float64 | 0 | 0.0% | 0 | 4.752 | 5.028 |
| `room_type` | str | 0 | 0.0% | — | — | — |
| `price` | int64 | 0 | 0.0% | 0 | 5 | 8,000 |
| `minimum_nights` | int64 | 0 | 0.0% | 0 | 1 | 1,001 |
| `number_of_reviews` | int64 | 0 | 0.0% | 2330 | 0 | 850 |
| `last_review` | datetime64[us] | 2,330 | 12.3% | — | 2012-07-26 | 2020-08-18 |
| `reviews_per_month` | float64 | 2,330 | 12.3% | 0 | 0.01 | 44.61 |
| `calculated_host_listings_count` | int64 | 0 | 0.0% | 0 | 1 | 85 |
| `availability_365` | int64 | 0 | 0.0% | 11751 | 0 | 365 |

## Price treatment

- Winsorisation bounds (1% / 99%): **$37** to **$595**
- Listings clipped at the low bound: **179**
- Listings clipped at the high bound: **188**
- `price` retains raw values for descriptive statistics; `price_winsorized` and `log_price` are used for modelling.

## Preserved nulls (not imputed)

- `last_review`: **2,330** nulls
- `reviews_per_month`: **2,330** nulls

These are retained deliberately. A listing with no reviews has never been booked through the platform, which is the market-inactivity signal computed in section 4.9. Imputing them would erase it.

## Review-field consistency check

Three fields encode the same underlying fact — that a listing has never been reviewed — and they agree exactly:

| Condition | Listings |
|---|---:|
| `number_of_reviews == 0` | 2,330 |
| `last_review` is null | 2,330 |
| `reviews_per_month` is null | 2,330 |
| All three simultaneously | 2,330 |

**Agreement: exact.** The three are one signal, not three. Treating them as independent indicators would triple-count zero-review listings in any composite score, so downstream code uses `number_of_reviews == 0` alone.

## Island listings

- Flagged as `is_island`: **0** listings in .
- Santa Catalina Island sits roughly 35 km offshore and is excluded from the coastline polyline. Distance-to-coast is set to null for these listings rather than measured to the mainland.
- All other indicators are computed for them normally.

## Structural caveats

- Single cross-sectional snapshot, scraped approximately mid-2020. No change over time is measurable.
- Scrape falls mid-pandemic. Inactivity figures reflect COVID conditions, not local market character.
- Geographic coverage is Amsterdam only (source file: `listings-Netherlands.csv`).
- `availability_365 == 0` on **62.0%** of listings, and is ambiguous: fully booked, or host-blocked calendar.
- `minimum_nights >= 30` on **0.8%** of listings, 68 of them at exactly 30. See `limitations.md` for whether a specific local ordinance is known to attach to that threshold in this market.

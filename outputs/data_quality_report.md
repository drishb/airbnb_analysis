# Data Quality Report

- Rows in raw file: **33,078**
- Rows after cleaning: **33,067**
- Dropped for `price == 0`: **11**

## Per-column summary (raw file)

| Column | dtype | Nulls | Null % | Zeros | Min | Max |
|---|---|---:|---:|---:|---:|---:|
| `id` | int64 | 0 | 0.0% | 0 | 109 | 4.503e+07 |
| `name` | str | 2 | 0.0% | — | — | — |
| `host_id` | int64 | 0 | 0.0% | 0 | 521 | 3.633e+08 |
| `host_name` | str | 9 | 0.0% | — | — | — |
| `neighbourhood_group` | str | 0 | 0.0% | — | — | — |
| `neighbourhood` | str | 0 | 0.0% | — | — | — |
| `latitude` | float64 | 0 | 0.0% | 0 | 33.34 | 34.81 |
| `longitude` | float64 | 0 | 0.0% | 0 | -118.9 | -117.7 |
| `room_type` | str | 0 | 0.0% | — | — | — |
| `price` | int64 | 0 | 0.0% | 11 | 0 | 2.5e+04 |
| `minimum_nights` | int64 | 0 | 0.0% | 0 | 1 | 1,125 |
| `number_of_reviews` | int64 | 0 | 0.0% | 7118 | 0 | 821 |
| `last_review` | datetime64[us] | 7,118 | 21.5% | — | 2010-03-28 | 2020-08-21 |
| `reviews_per_month` | float64 | 7,118 | 21.5% | 0 | 0.01 | 34.26 |
| `calculated_host_listings_count` | int64 | 0 | 0.0% | 0 | 1 | 195 |
| `availability_365` | int64 | 0 | 0.0% | 7743 | 0 | 365 |

## Price treatment

- Winsorisation bounds (1% / 99%): **$22** to **$2,316**
- Listings clipped at the low bound: **289**
- Listings clipped at the high bound: **331**
- `price` retains raw values for descriptive statistics; `price_winsorized` and `log_price` are used for modelling.

## Preserved nulls (not imputed)

- `last_review`: **7,107** nulls
- `reviews_per_month`: **7,107** nulls

These are retained deliberately. A listing with no reviews has never been booked through the platform, which is the market-inactivity signal computed in section 4.9. Imputing them would erase it.

## Review-field consistency check

Three fields encode the same underlying fact — that a listing has never been reviewed — and they agree exactly:

| Condition | Listings |
|---|---:|
| `number_of_reviews == 0` | 7,118 |
| `last_review` is null | 7,118 |
| `reviews_per_month` is null | 7,118 |
| All three simultaneously | 7,118 |

**Agreement: exact.** The three are one signal, not three. Treating them as independent indicators would triple-count zero-review listings in any composite score, so downstream code uses `number_of_reviews == 0` alone.

## Island listings

- Flagged as `is_island`: **169** listings in Avalon, Unincorporated Catalina Island.
- Santa Catalina Island sits roughly 35 km offshore and is excluded from the coastline polyline. Distance-to-coast is set to null for these listings rather than measured to the mainland.
- All other indicators are computed for them normally.

## Structural caveats

- Single cross-sectional snapshot, scraped approximately mid-2020. No change over time is measurable.
- Scrape falls mid-pandemic. Inactivity figures reflect COVID conditions, not local market character.
- Geographic coverage is LA County only (source file: `listings_California.csv`).
- `availability_365 == 0` on **23.4%** of listings, and is ambiguous: fully booked, or host-blocked calendar.
- `minimum_nights >= 30` on **32.1%** of listings, 7,974 of them at exactly 30. See `limitations.md` for whether a specific local ordinance is known to attach to that threshold in this market.

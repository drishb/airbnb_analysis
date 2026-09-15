# Data Quality Report

- Rows in raw file: **35,731**
- Rows after cleaning: **35,724**
- Dropped for `price == 0`: **7**

## Per-column summary (raw file)

| Column | dtype | Nulls | Null % | Zeros | Min | Max |
|---|---|---:|---:|---:|---:|---:|
| `id` | int64 | 0 | 0.0% | 0 | 1.788e+04 | 4.385e+07 |
| `name` | str | 58 | 0.2% | — | — | — |
| `host_id` | int64 | 0 | 0.0% | 0 | 1.174e+04 | 3.505e+08 |
| `host_name` | str | 5 | 0.0% | — | — | — |
| `neighbourhood_group` | float64 | 35,731 | 100.0% | 0 | nan | nan |
| `neighbourhood` | str | 0 | 0.0% | — | — | — |
| `latitude` | float64 | 0 | 0.0% | 0 | -23.07 | -22.75 |
| `longitude` | float64 | 0 | 0.0% | 0 | -43.74 | -43.1 |
| `room_type` | str | 0 | 0.0% | — | — | — |
| `price` | int64 | 0 | 0.0% | 7 | 0 | 1.324e+05 |
| `minimum_nights` | int64 | 0 | 0.0% | 0 | 1 | 1,123 |
| `number_of_reviews` | int64 | 0 | 0.0% | 14991 | 0 | 406 |
| `last_review` | datetime64[us] | 14,991 | 42.0% | — | 2012-02-21 | 2020-06-19 |
| `reviews_per_month` | float64 | 14,991 | 42.0% | 0 | 0.01 | 8.55 |
| `calculated_host_listings_count` | int64 | 0 | 0.0% | 0 | 1 | 319 |
| `availability_365` | int64 | 0 | 0.0% | 11203 | 0 | 365 |

## Price treatment

- Winsorisation bounds (1% / 99%): **$48** to **$8,852**
- Listings clipped at the low bound: **226**
- Listings clipped at the high bound: **348**
- `price` retains raw values for descriptive statistics; `price_winsorized` and `log_price` are used for modelling.

## Preserved nulls (not imputed)

- `last_review`: **14,988** nulls
- `reviews_per_month`: **14,988** nulls

These are retained deliberately. A listing with no reviews has never been booked through the platform, which is the market-inactivity signal computed in section 4.9. Imputing them would erase it.

## Review-field consistency check

Three fields encode the same underlying fact — that a listing has never been reviewed — and they agree exactly:

| Condition | Listings |
|---|---:|
| `number_of_reviews == 0` | 14,991 |
| `last_review` is null | 14,991 |
| `reviews_per_month` is null | 14,991 |
| All three simultaneously | 14,991 |

**Agreement: exact.** The three are one signal, not three. Treating them as independent indicators would triple-count zero-review listings in any composite score, so downstream code uses `number_of_reviews == 0` alone.

## Island listings

- Flagged as `is_island`: **0** listings in .
- Santa Catalina Island sits roughly 35 km offshore and is excluded from the coastline polyline. Distance-to-coast is set to null for these listings rather than measured to the mainland.
- All other indicators are computed for them normally.

## Structural caveats

- Single cross-sectional snapshot, scraped approximately mid-2020. No change over time is measurable.
- Scrape falls mid-pandemic. Inactivity figures reflect COVID conditions, not local market character.
- Geographic coverage is Rio de Janeiro only (source file: `listings-RIo_de_Janeiro.csv`).
- `availability_365 == 0` on **31.4%** of listings, and is ambiguous: fully booked, or host-blocked calendar.
- `minimum_nights >= 30` on **1.8%** of listings, 413 of them at exactly 30. See `limitations.md` for whether a specific local ordinance is known to attach to that threshold in this market.

# Neighbourhood Clusters

Family-weighted K-means over the **79** retained neighbourhoods (>= 100 listings) and **31** engineered features, grouped into eight indicator families each contributing equally to the distance metric (PRD §7.1). Excluded neighbourhoods are in `excluded_neighbourhoods.md` and are not clustered.

## Choosing k

k was swept from 2 to 10 (`figures/elbow_silhouette.png`); the range may fall short of the usual 2-10 when there are few retained neighbourhoods (k-means requires k <= n_samples). Swept over **79** retained neighbourhoods and **31** engineered features (peak silhouette 0.19 at k=5).

**k = 5** was selected: it sits at a local silhouette maximum (0.19, tied with k=2 for the best in the range), is where the inertia gain per extra cluster starts to shrink, yields five centroid profiles that each describe a recognisable market type, and coincides with the independently chosen NMF topic count. Larger k fragments the map into two- and three-neighbourhood clusters without raising the silhouette. The shortfall against success metric 4's 0.25 bar is a property of the data, not the family weighting - unweighted standardised features peak at 0.20.

| k | inertia | mean silhouette |
|--:|--:|--:|
| 2 | 514.1 | 0.194 |
| 3 | 446.8 | 0.180 |
| 4 | 387.3 | 0.167 |
| 5 | 336.3 | 0.194  <- selected |
| 6 | 304.8 | 0.165 |
| 7 | 274.1 | 0.162 |
| 8 | 250.2 | 0.176 |
| 9 | 238.1 | 0.162 |
| 10 | 225.4 | 0.150 |

> Success metric 4 sets a mean-silhouette bar of 0.25. The chosen solution scores **0.19** (below that bar).

## Cluster labels

Labels were assigned **after** fitting, by reading the centroid table below in original units. They are descriptive summaries of each centroid profile, not inputs to the clustering.

| Cluster | Label | n neighbourhoods | n listings |
|--:|---|--:|--:|
| 0 | Long-stay / regulation-exempt core | 15 | 6777 |
| 1 | Outer suburban budget, owner-hosted | 26 | 7429 |
| 2 | Island resort, single operator | 1 | 149 |
| 3 | Upmarket hillside & Westside | 15 | 5218 |
| 4 | Established high-turnover tourist | 22 | 7836 |

## Centroid profiles (original units)

Mean of each feature over the cluster's member neighbourhoods (req 54). Columns are cluster ids; see the label table above.

|                                    |        0 |        1 |        2 |        3 |        4 |
|:-----------------------------------|---------:|---------:|---------:|---------:|---------:|
| tour_reviews_per_month_mean        |    1.204 |    1.562 |    1.564 |    1.537 |    1.381 |
| tour_reviews_per_month_median      |    0.633 |    1.038 |    1.22  |    0.939 |    0.761 |
| tour_reviews_total_mean            |   27.672 |   31.382 |   17.866 |   34.001 |   42.375 |
| tour_entire_home_share             |    0.58  |    0.455 |    0.966 |    0.733 |    0.703 |
| tour_dist_hollywood_km_median      |    9.286 |   27.916 |   84.328 |   16.993 |   13.261 |
| tour_dist_downtown_km_median       |   13.457 |   23.62  |   79.38  |   25.192 |   15.975 |
| tour_dist_universal_km_median      |   12.346 |   29.777 |   88.412 |   16.416 |   14.795 |
| tour_dist_disneyland_km_median     |   49.9   |   41.574 |   64.389 |   63.511 |   49.134 |
| tour_dist_coast_km_median          |   11.302 |   27.826 |    0     |   13.01  |   14.276 |
| host_hhi                           |    0.026 |    0.017 |    0.419 |    0.01  |    0.008 |
| host_share_10plus                  |    0.291 |    0.116 |    0.752 |    0.135 |    0.078 |
| host_top5_share                    |    0.248 |    0.19  |    0.785 |    0.138 |    0.109 |
| host_multilisting_share            |    0.617 |    0.604 |    0.859 |    0.517 |    0.421 |
| reg_min30_share                    |    0.548 |    0.118 |    0     |    0.268 |    0.399 |
| reg_min_nights_median              |   27.467 |    2.115 |    2     |    3.4   |   10.773 |
| tenure_months_median               |   27.206 |   21.015 |   13.592 |   27.701 |   34.893 |
| rev_uncapped_median                | 5433.85  | 1866.8   | 7380     | 7605.17  | 8545.5   |
| rev_capped_median                  | 2119.88  | 1355.49  | 7380     | 5226.9   | 3863.06  |
| occ_booked_days_median             |  180.4   |  230.25  |   35     |  193.567 |  247.568 |
| occ_zero_availability_share        |    0.22  |    0.228 |    0.007 |    0.193 |    0.284 |
| price_median                       |  105.8   |   82.962 |  450     |  255.533 |  117.5   |
| price_iqr                          |  100.417 |   77.394 |  219     |  453.85  |  113.114 |
| price_cv                           |    1.735 |    1.214 |    0.458 |    2.011 |    1.29  |
| price_gini                         |    0.474 |    0.409 |    0.24  |    0.59  |    0.432 |
| inactivity_never_reviewed_share    |    0.261 |    0.191 |    0.591 |    0.262 |    0.179 |
| inactivity_stale_since_covid_share |    0.389 |    0.333 |    0.04  |    0.291 |    0.412 |
| topic_0_loading                    |    0.109 |    0.135 |    0.08  |    0.094 |    0.123 |
| topic_1_loading                    |    0.2   |    0.155 |    0.27  |    0.25  |    0.204 |
| topic_2_loading                    |    0.147 |    0.135 |    0.2   |    0.16  |    0.149 |
| topic_3_loading                    |    0.285 |    0.288 |    0.26  |    0.249 |    0.286 |
| topic_4_loading                    |    0.167 |    0.1   |    0.135 |    0.143 |    0.147 |

## Member neighbourhoods

### Cluster 0 - Long-stay / regulation-exempt core (15)

Arlington Heights, Beverly Grove, Brentwood, East Hollywood, Exposition Park, Harvard Heights, Hermosa Beach, Hollywood, Koreatown, Mid-Wilshire, Pico-Robertson, Santa Monica, Sawtelle, West Los Angeles, Westwood

### Cluster 1 - Outer suburban budget, owner-hosted (26)

Alhambra, Arcadia, Diamond Bar, East Los Angeles, El Monte, El Segundo, Gardena, Glendale, Hacienda Heights, Hawthorne, Inglewood, Lancaster, Long Beach, Marina del Rey, Monterey Park, Pasadena, Pomona, Rowland Heights, San Gabriel, Santa Clarita, Temple City, Torrance, Van Nuys, West Covina, Westchester, Westlake

### Cluster 2 - Island resort, single operator (1)

Avalon

### Cluster 3 - Upmarket hillside & Westside (15)

Beverly Crest, Beverly Hills, Downtown, Encino, Hollywood Hills, Hollywood Hills West, Malibu, Pacific Palisades, Reseda, Sherman Oaks, Tarzana, Topanga, Unincorporated Santa Monica Mountains, Valley Glen, Woodland Hills

### Cluster 4 - Established high-turnover tourist (22)

Altadena, Burbank, Culver City, Del Rey, Eagle Rock, Echo Park, Fairfax, Highland Park, Los Feliz, Manhattan Beach, Mar Vista, Mid-City, North Hollywood, Palms, Playa del Rey, Redondo Beach, San Pedro, Silver Lake, Studio City, Valley Village, Venice, West Hollywood

## PCA robustness check (req 53)

K-means was re-run at k=5 on principal components retaining 86.8% of the variance (9 components) from the standardised, unweighted features - the alternative to family weighting (PRD §7.1). Adjusted Rand index between that solution and the family-weighted one: **0.298**.

That is partial agreement. The central long-stay cluster and the Avalon singleton are stable across both methods; the split among the outer-suburban, upmarket, and inner-tourist groups is method-sensitive, consistent with the weak silhouette. The broad shape of the segmentation holds; the exact partition of the middle of the distribution should not be over-read.

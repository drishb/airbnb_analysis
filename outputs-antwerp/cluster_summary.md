# Neighbourhood Clusters

Family-weighted K-means over the **7** retained neighbourhoods (>= 100 listings) and **31** engineered features, grouped into eight indicator families each contributing equally to the distance metric (PRD §7.1). Excluded neighbourhoods are in `excluded_neighbourhoods.md` and are not clustered.

## Choosing k

k was swept from 2 to 6 (`figures/elbow_silhouette.png`); the range may fall short of the usual 2-10 when there are few retained neighbourhoods (k-means requires k <= n_samples). Swept over **7** retained neighbourhoods and **31** engineered features (peak silhouette 0.23 at k=2).

**k = 3** was selected: the silhouette peaks at k=2 (0.23) in this 7-neighbourhood sample, but that split is too coarse to say anything beyond 'cheap vs. not' - k=3 (0.17) separates a small, central tourist-facing core (Centraal Station, Historisch Centrum, Theaterbuurt-Meir) from a lower-concentration residential group and a single high-concentration, high-price-inequality outlier (Stadspark), a more informative typology despite the lower score. With only 7 retained neighbourhoods this segmentation is thin and low-confidence by construction (§4.10's rationale for the n>=100 rule) - read the member lists, not the silhouette, as the primary evidence.

| k | inertia | mean silhouette |
|--:|--:|--:|
| 2 | 33.9 | 0.231 |
| 3 | 24.4 | 0.172  <- selected |
| 4 | 15.0 | 0.122 |
| 5 | 7.5 | 0.113 |
| 6 | 2.6 | 0.074 |

> Success metric 4 sets a mean-silhouette bar of 0.25. The chosen solution scores **0.17** (below that bar).

## Cluster labels

Labels were assigned **after** fitting, by reading the centroid table below in original units. They are descriptive summaries of each centroid profile, not inputs to the clustering.

| Cluster | Label | n neighbourhoods | n listings |
|--:|---|--:|--:|
| 0 | Outer residential, dispersed hosts | 3 | 441 |
| 1 | Historic core, tourist-facing | 3 | 617 |
| 2 | High-concentration outlier (Stadspark) | 1 | 184 |

## Centroid profiles (original units)

Mean of each feature over the cluster's member neighbourhoods (req 54). Columns are cluster ids; see the label table above.

|                                      |        0 |       1 |       2 |
|:-------------------------------------|---------:|--------:|--------:|
| tour_reviews_per_month_mean          |    1.446 |   1.624 |   1.086 |
| tour_reviews_per_month_median        |    0.815 |   0.985 |   0.64  |
| tour_reviews_total_mean              |   37.111 |  32.761 |  20.538 |
| tour_entire_home_share               |    0.785 |   0.838 |   0.853 |
| tour_dist_grote_markt_km_median      |    1.204 |   0.94  |   1.813 |
| tour_dist_centraal_station_km_median |    1.269 |   0.941 |   1.171 |
| tour_dist_mas_km_median              |    1.496 |   1.43  |   2.469 |
| tour_dist_zoo_km_median              |    1.266 |   0.935 |   1.093 |
| tour_dist_coast_km_median            |    0.916 |   0.968 |   1.313 |
| host_hhi                             |    0.014 |   0.021 |   0.049 |
| host_share_10plus                    |    0.121 |   0.213 |   0.375 |
| host_top5_share                      |    0.168 |   0.243 |   0.38  |
| host_multilisting_share              |    0.426 |   0.599 |   0.652 |
| reg_min30_share                      |    0.026 |   0.006 |   0.038 |
| reg_min_nights_median                |    2     |   1     |   2     |
| tenure_months_median                 |   23.518 |  16.128 |  15.385 |
| rev_uncapped_median                  | 1263.75  | 941.667 | 999     |
| rev_capped_median                    | 1111.08  | 918.083 | 910     |
| occ_booked_days_median               |  296.5   | 222.667 | 283.5   |
| occ_zero_availability_share          |    0.42  |   0.299 |   0.37  |
| price_median                         |   68.333 |  83.667 |  79     |
| price_iqr                            |   43.333 |  55     |  86.25  |
| price_cv                             |    1.127 |   1.869 |   1.769 |
| price_gini                           |    0.394 |   0.519 |   0.649 |
| inactivity_never_reviewed_share      |    0.181 |   0.18  |   0.223 |
| inactivity_stale_since_covid_share   |    0.473 |   0.38  |   0.446 |
| topic_0_loading                      |    0.125 |   0.135 |   0.261 |
| topic_1_loading                      |    0.119 |   0.06  |   0.053 |
| topic_2_loading                      |    0.074 |   0.161 |   0.144 |
| topic_3_loading                      |    0.304 |   0.293 |   0.258 |
| topic_4_loading                      |    0.124 |   0.117 |   0.138 |

## Member neighbourhoods

### Cluster 0 - Outer residential, dispersed hosts (3)

Amandus - Atheneum, Universiteitsbuurt, Zuid

### Cluster 1 - Historic core, tourist-facing (3)

Centraal Station, Historisch Centrum, Theaterbuurt-Meir

### Cluster 2 - High-concentration outlier (Stadspark) (1)

Stadspark

## PCA robustness check (req 53)

K-means was re-run at k=3 on principal components retaining 94.9% of the variance (4 components) from the standardised, unweighted features - the alternative to family weighting (PRD §7.1). Adjusted Rand index between that solution and the family-weighted one: **0.067**.

Very low agreement (ARI 0.07). With only 7 retained neighbourhoods split 3/3/1, both the family-weighted and PCA solutions are highly sensitive to the exact placement of a handful of points - the specific 3-way partition should not be over-read; treat this run as illustrating the method, not a confident segmentation of Antwerp.

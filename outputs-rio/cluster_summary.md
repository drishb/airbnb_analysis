# Neighbourhood Clusters

Family-weighted K-means over the **32** retained neighbourhoods (>= 100 listings) and **31** engineered features, grouped into eight indicator families each contributing equally to the distance metric (PRD §7.1). Excluded neighbourhoods are in `excluded_neighbourhoods.md` and are not clustered.

## Choosing k

k was swept from 2 to 10 (`figures/elbow_silhouette.png`); the range may fall short of the usual 2-10 when there are few retained neighbourhoods (k-means requires k <= n_samples). Swept over **32** retained neighbourhoods and **31** engineered features (peak silhouette 0.25 at k=2).

**k = 5** was selected: the silhouette peaks at k=2 (0.25) but that only separates the beachfront core from everywhere else - k=5 (0.17) resolves that core (Copacabana, Ipanema, Leblon, Leme) from four further, geographically coherent groups (South Zone upscale, far periphery, inland North Zone, downtown/inner harbour) and matches the independently chosen NMF topic count, at some cost in the silhouette score - the same interpretability-over-statistic trade-off the LA run made.

| k | inertia | mean silhouette |
|--:|--:|--:|
| 2 | 178.8 | 0.252 |
| 3 | 151.3 | 0.187 |
| 4 | 129.6 | 0.189 |
| 5 | 116.5 | 0.165  <- selected |
| 6 | 104.6 | 0.157 |
| 7 | 96.2 | 0.158 |
| 8 | 87.8 | 0.147 |
| 9 | 75.4 | 0.179 |
| 10 | 68.9 | 0.165 |

> Success metric 4 sets a mean-silhouette bar of 0.25. The chosen solution scores **0.17** (below that bar).

## Cluster labels

Labels were assigned **after** fitting, by reading the centroid table below in original units. They are descriptive summaries of each centroid profile, not inputs to the clustering.

| Cluster | Label | n neighbourhoods | n listings |
|--:|---|--:|--:|
| 0 | South Zone periphery, upscale residential | 7 | 6447 |
| 1 | Far periphery, low turnover | 9 | 3234 |
| 2 | Iconic beachfront tourist core | 4 | 14549 |
| 3 | Inland North Zone, stadium-adjacent | 4 | 3317 |
| 4 | Downtown & inner harbour, budget-mixed | 8 | 5638 |

## Centroid profiles (original units)

Mean of each feature over the cluster's member neighbourhoods (req 54). Columns are cluster ids; see the label table above.

|                                    |        0 |       1 |        2 |       3 |       4 |
|:-----------------------------------|---------:|--------:|---------:|--------:|--------:|
| tour_reviews_per_month_mean        |    0.375 |   0.336 |    0.622 |   0.349 |   0.474 |
| tour_reviews_per_month_median      |    0.204 |   0.194 |    0.292 |   0.179 |   0.237 |
| tour_reviews_total_mean            |    6.382 |   2.404 |   14.474 |   3.009 |   8.343 |
| tour_entire_home_share             |    0.689 |   0.602 |    0.806 |   0.543 |   0.636 |
| tour_dist_corcovado_km_median      |    4.663 |  17.286 |    3.816 |   8.14  |   3.914 |
| tour_dist_sugarloaf_km_median      |    7.477 |  22.584 |    5.124 |  12.852 |   4.446 |
| tour_dist_maracana_km_median       |    7.376 |  16.847 |    8.219 |   5.382 |   6.15  |
| tour_dist_centro_km_median         |    7.937 |  21.812 |    8.15  |  10.774 |   4.619 |
| tour_dist_coast_km_median          |    1.405 |   4.164 |    0.371 |   5.716 |   1.134 |
| host_hhi                           |    0.004 |   0.009 |    0.002 |   0.003 |   0.006 |
| host_share_10plus                  |    0.046 |   0.059 |    0.158 |   0.018 |   0.049 |
| host_top5_share                    |    0.063 |   0.112 |    0.049 |   0.048 |   0.086 |
| host_multilisting_share            |    0.352 |   0.35  |    0.502 |   0.293 |   0.385 |
| reg_min30_share                    |    0.032 |   0.019 |    0.018 |   0.018 |   0.012 |
| reg_min_nights_median              |    2.286 |   1.889 |    3     |   1.75  |   2.125 |
| tenure_months_median               |   31.086 |  19.053 |   30.046 |  29.33  |  25.983 |
| rev_uncapped_median                | 1343.89  | 545.722 | 2884     | 539.438 | 952.562 |
| rev_capped_median                  | 1276.43  | 542.056 | 2769.5   | 521.438 | 916.406 |
| occ_booked_days_median             |  257.571 | 163.667 |  212.75  | 253.25  | 235.875 |
| occ_zero_availability_share        |    0.382 |   0.332 |    0.27  |   0.408 |   0.355 |
| price_median                       |  338.571 | 313.111 |  351     | 300     | 220.75  |
| price_iqr                          |  550     | 791.389 |  478     | 662.688 | 328.594 |
| price_cv                           |    2.575 |   2.06  |    2.581 |   2.16  |   2.932 |
| price_gini                         |    0.634 |   0.639 |    0.604 |   0.607 |   0.676 |
| inactivity_never_reviewed_share    |    0.428 |   0.639 |    0.33  |   0.621 |   0.414 |
| inactivity_stale_since_covid_share |    0.462 |   0.304 |    0.466 |   0.318 |   0.45  |
| topic_0_loading                    |    0.267 |   0.142 |    0.328 |   0.117 |   0.245 |
| topic_1_loading                    |    0.106 |   0.086 |    0.07  |   0.06  |   0.119 |
| topic_2_loading                    |    0.072 |   0.183 |    0.044 |   0.16  |   0.062 |
| topic_3_loading                    |    0.295 |   0.238 |    0.318 |   0.201 |   0.281 |
| topic_4_loading                    |    0.162 |   0.23  |    0.109 |   0.376 |   0.158 |

## Member neighbourhoods

### Cluster 0 - South Zone periphery, upscale residential (7)

Barra da Tijuca, Cosme Velho, Flamengo, Glória, Gávea, Jardim Botânico, Lagoa

### Cluster 1 - Far periphery, low turnover (9)

Camorim, Freguesia (Jacarepaguá), Itanhangá, Recreio dos Bandeirantes, Rio Comprido, São Conrado, Taquara, Vargem Grande, Vargem Pequena

### Cluster 2 - Iconic beachfront tourist core (4)

Copacabana, Ipanema, Leblon, Leme

### Cluster 3 - Inland North Zone, stadium-adjacent (4)

Jacarepaguá, Maracanã, Tijuca, Vila Isabel

### Cluster 4 - Downtown & inner harbour, budget-mixed (8)

Botafogo, Catete, Centro, Humaitá, Laranjeiras, Santa Teresa, Urca, Vidigal

## PCA robustness check (req 53)

K-means was re-run at k=5 on principal components retaining 87.7% of the variance (7 components) from the standardised, unweighted features - the alternative to family weighting (PRD §7.1). Adjusted Rand index between that solution and the family-weighted one: **0.382**.

Partial agreement, similar in magnitude to the LA run's 0.30. The iconic beachfront cluster (Copacabana, Ipanema, Leblon, Leme) is a strong, geographically obvious grouping likely to be stable across methods; the split among the inland, periphery, and South Zone groups is more method-sensitive, consistent with the modest silhouette.

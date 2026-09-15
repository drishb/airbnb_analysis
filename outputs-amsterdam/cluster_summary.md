# Neighbourhood Clusters

Family-weighted K-means over the **22** retained neighbourhoods (>= 100 listings) and **31** engineered features, grouped into eight indicator families each contributing equally to the distance metric (PRD §7.1). Excluded neighbourhoods are in `excluded_neighbourhoods.md` and are not clustered.

## Choosing k

k was swept from 2 to 10 (`figures/elbow_silhouette.png`); the range may fall short of the usual 2-10 when there are few retained neighbourhoods (k-means requires k <= n_samples). Swept over **22** retained neighbourhoods and **31** engineered features (peak silhouette 0.33 at k=5).

**k = 5** was selected: it is the outright silhouette maximum over the swept range (0.33, clearing success metric 4's 0.25 bar) and yields five centroid profiles that separate cleanly on distance-to-centre and price: a small premium-centre pair, a large entire-home-dominant inner ring, an outer-suburban group, and two small outlying/high-variance clusters.

| k | inertia | mean silhouette |
|--:|--:|--:|
| 2 | 124.3 | 0.253 |
| 3 | 91.7 | 0.312 |
| 4 | 70.7 | 0.300 |
| 5 | 53.0 | 0.329  <- selected |
| 6 | 39.4 | 0.298 |
| 7 | 33.4 | 0.267 |
| 8 | 28.5 | 0.256 |
| 9 | 24.1 | 0.247 |
| 10 | 20.8 | 0.240 |

> Success metric 4 sets a mean-silhouette bar of 0.25. The chosen solution scores **0.33** (meets that bar).

## Cluster labels

Labels were assigned **after** fitting, by reading the centroid table below in original units. They are descriptive summaries of each centroid profile, not inputs to the clustering.

| Cluster | Label | n neighbourhoods | n listings |
|--:|---|--:|--:|
| 0 | City centre, premium tourist core | 2 | 3703 |
| 1 | Established inner ring, entire-home dominant | 9 | 12674 |
| 2 | Outer suburban, mixed room types | 8 | 1605 |
| 3 | Outer periphery, room-share dominant (Gaasperdam-Driemond) | 1 | 126 |
| 4 | Newer/outlying development, volatile pricing | 2 | 841 |

## Centroid profiles (original units)

Mean of each feature over the cluster's member neighbourhoods (req 54). Columns are cluster ids; see the label table above.

|                                    |        0 |        1 |        2 |        3 |        4 |
|:-----------------------------------|---------:|---------:|---------:|---------:|---------:|
| tour_reviews_per_month_mean        |    1.107 |    0.616 |    0.865 |    0.959 |    0.718 |
| tour_reviews_per_month_median      |    0.545 |    0.319 |    0.382 |    0.43  |    0.35  |
| tour_reviews_total_mean            |   37.967 |   21.08  |   24.407 |   30.778 |   20.391 |
| tour_entire_home_share             |    0.696 |    0.82  |    0.592 |    0.389 |    0.72  |
| tour_dist_dam_square_km_median     |    1.055 |    2.815 |    6.016 |   10.278 |    5.796 |
| tour_dist_rijksmuseum_km_median    |    1.668 |    2.745 |    5.478 |    9.441 |    6.663 |
| tour_dist_anne_frank_km_median     |    1.219 |    2.866 |    5.963 |   10.816 |    6.024 |
| tour_dist_vondelpark_km_median     |    2.538 |    3.061 |    5.21  |   10.054 |    7.454 |
| tour_dist_coast_km_median          |    1.054 |    1.931 |    4.267 |   10.016 |    3.646 |
| host_hhi                           |    0.001 |    0.001 |    0.009 |    0.013 |    0.003 |
| host_share_10plus                  |    0.071 |    0.027 |    0.014 |    0     |    0.023 |
| host_top5_share                    |    0.035 |    0.029 |    0.098 |    0.151 |    0.051 |
| host_multilisting_share            |    0.335 |    0.168 |    0.248 |    0.333 |    0.211 |
| reg_min30_share                    |    0.006 |    0.008 |    0.013 |    0.048 |    0.005 |
| reg_min_nights_median              |    2     |    2     |    2     |    2     |    3     |
| tenure_months_median               |   39.045 |   38.923 |   31.145 |   33.333 |   29.791 |
| rev_uncapped_median                | 3256.88  | 1649.03  | 1123.25  | 1400     | 1430     |
| rev_capped_median                  | 3168.88  | 1608.36  | 1069.06  | 1160     | 1414.88  |
| occ_booked_days_median             |  359     |  365     |  365     |  340.5   |  365     |
| occ_zero_availability_share        |    0.483 |    0.66  |    0.585 |    0.405 |    0.579 |
| price_median                       |  150     |  126.5   |   98.438 |   80     |  134.5   |
| price_iqr                          |  115     |   82.194 |   76.781 |   50     |   97.25  |
| price_cv                           |    0.965 |    0.77  |    0.792 |    0.561 |    1.075 |
| price_gini                         |    0.333 |    0.293 |    0.321 |    0.288 |    0.317 |
| inactivity_never_reviewed_share    |    0.136 |    0.116 |    0.165 |    0.071 |    0.155 |
| inactivity_stale_since_covid_share |    0.566 |    0.72  |    0.602 |    0.659 |    0.601 |
| topic_0_loading                    |    0.285 |    0.155 |    0.176 |    0.183 |    0.149 |
| topic_1_loading                    |    0.214 |    0.414 |    0.416 |    0.306 |    0.487 |
| topic_2_loading                    |    0.095 |    0.122 |    0.116 |    0.132 |    0.062 |
| topic_3_loading                    |    0.084 |    0.132 |    0.092 |    0.105 |    0.078 |
| topic_4_loading                    |    0.246 |    0.123 |    0.095 |    0.091 |    0.132 |

## Member neighbourhoods

### Cluster 0 - City centre, premium tourist core (2)

Centrum-Oost, Centrum-West

### Cluster 1 - Established inner ring, entire-home dominant (9)

Bos en Lommer, De Baarsjes - Oud-West, De Pijp - Rivierenbuurt, Oostelijk Havengebied - Indische Buurt, Oud-Noord, Oud-Oost, Watergraafsmeer, Westerpark, Zuid

### Cluster 2 - Outer suburban, mixed room types (8)

Bijlmer-Centrum, Bijlmer-Oost, Buitenveldert - Zuidas, De Aker - Nieuw Sloten, Geuzenveld - Slotermeer, Noord-Oost, Osdorp, Slotervaart

### Cluster 3 - Outer periphery, room-share dominant (Gaasperdam-Driemond) (1)

Gaasperdam - Driemond

### Cluster 4 - Newer/outlying development, volatile pricing (2)

IJburg - Zeeburgereiland, Noord-West

## PCA robustness check (req 53)

K-means was re-run at k=5 on principal components retaining 88.7% of the variance (5 components) from the standardised, unweighted features - the alternative to family weighting (PRD §7.1). Adjusted Rand index between that solution and the family-weighted one: **0.493**.

Moderate agreement - the strongest ARI of the three new datasets, consistent with this being the one clustering run that already clears the silhouette bar. The segmentation is comparatively robust to the weighting/PCA choice; the mid-distribution boundaries (the outer-suburban and periphery clusters) are more method-sensitive than the city-centre vs. rest split.

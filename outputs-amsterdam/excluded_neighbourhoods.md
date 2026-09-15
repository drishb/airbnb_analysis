# Excluded Neighbourhoods

The neighbourhood table retains all **22** neighbourhoods. Ranked tables, clustering, and maps use only the **22** with at least **100** listings. This report covers the **0** that are excluded from those outputs.

## What the exclusion removes

- Neighbourhoods excluded: **0** of 22 (0%)
- Listings in excluded neighbourhoods: **0** of 18,949 (**0.0%**)
- Nothing is excluded: every neighbourhood in this dataset clears n >= 100.

The exclusion trades 0.0% of listing volume for indicator stability. The retained neighbourhoods still cover 100.0% of the market by listing count.

## Why n >= 100

Three problems affect small neighbourhoods, and all three get worse as n falls.

### (a) Rate instability

Every share indicator - entire-home share, 30-night-minimum share, no-review share - can only take values that are multiples of 1/n. A neighbourhood with 12 listings produces entire-home shares in steps of 8.3%, and moving one listing shifts the value by that much. The ranking would then order neighbourhoods partly on which side of a rounding step they happen to land.

### (b) Mechanical HHI inflation

The Herfindahl-Hirschman index has a floor of 1/n. A 10-listing neighbourhood cannot score below 0.10 even if all 10 hosts are distinct - it would read as moderately concentrated purely from being small. Host concentration is one of the eight indicator families, so this pushes small neighbourhoods toward the "commercialised" end of the segmentation as an artifact of size.

### (c) Clustering distortion

K-means minimises within-cluster variance. A small neighbourhood with an extreme indicator value - easy to produce when n is small - pulls a centroid toward itself and can end up alone in its own cluster, spending a segment on noise instead of a real market type.

## Threshold sensitivity (req 41)

The ranking and family-weighted K-means (k = 5, held fixed) were re-run at each threshold. For every pair, cluster ids were matched by maximum overlap on the neighbourhoods common to both fits; the table counts how many of those common neighbourhoods still land in a different cluster.

|   threshold_low |   threshold_high |   n_common |   n_changed |   pct_changed |
|----------------:|-----------------:|-----------:|------------:|--------------:|
|              50 |              100 |         22 |           0 |           0   |
|             100 |              200 |         17 |           2 |          11.8 |
|              50 |              200 |         17 |           2 |          11.8 |

Between **12%** (widest pair) and 0% of common neighbourhoods change cluster as the threshold moves. The threshold choice is therefore **load-bearing** for the fine cluster partition - it shifts which small-to-mid neighbourhoods anchor which centroid. This matches the modest silhouette (~0.19) and the family-weighted vs. PCA adjusted Rand index (~0.30) reported in `cluster_summary.md`: the broad segmentation is stable, the exact membership of the middle clusters is not. The n >= 100 rule is retained for the reasons above; readers should treat individual cluster membership near the boundary as approximate.

## Full list of excluded neighbourhoods (0)

| Neighbourhood | Listings | Group |
|---|---:|---|

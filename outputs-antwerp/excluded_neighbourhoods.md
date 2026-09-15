# Excluded Neighbourhoods

The neighbourhood table retains all **57** neighbourhoods. Ranked tables, clustering, and maps use only the **7** with at least **100** listings. This report covers the **50** that are excluded from those outputs.

## What the exclusion removes

- Neighbourhoods excluded: **50** of 57 (88%)
- Listings in excluded neighbourhoods: **1,179** of 2,421 (**48.7%**)
- Excluded neighbourhoods hold **1** to **93** listings each; 3 sit within 10 of the threshold (Sint-Andries (93), Borgerhout Intra Muros Zuid (92), Borgerhout Intra Muros Noord (90)).

The exclusion trades 48.7% of listing volume for indicator stability. The retained neighbourhoods still cover 51.3% of the market by listing count.

## Why n >= 100

Three problems affect small neighbourhoods, and all three get worse as n falls.

### (a) Rate instability

Every share indicator - entire-home share, 30-night-minimum share, no-review share - can only take values that are multiples of 1/n. A neighbourhood with 12 listings produces entire-home shares in steps of 8.3%, and moving one listing shifts the value by that much. The ranking would then order neighbourhoods partly on which side of a rounding step they happen to land.

### (b) Mechanical HHI inflation

The Herfindahl-Hirschman index has a floor of 1/n. A 10-listing neighbourhood cannot score below 0.10 even if all 10 hosts are distinct - it would read as moderately concentrated purely from being small. Host concentration is one of the eight indicator families, so this pushes small neighbourhoods toward the "commercialised" end of the segmentation as an artifact of size.

### (c) Clustering distortion

K-means minimises within-cluster variance. A small neighbourhood with an extreme indicator value - easy to produce when n is small - pulls a centroid toward itself and can end up alone in its own cluster, spending a segment on noise instead of a real market type.

## Threshold sensitivity (req 41)

The ranking and family-weighted K-means (k = 3, held fixed) were re-run at each threshold. For every pair, cluster ids were matched by maximum overlap on the neighbourhoods common to both fits; the table counts how many of those common neighbourhoods still land in a different cluster.

|   threshold_low |   threshold_high |   n_common |   n_changed |   pct_changed |
|----------------:|-----------------:|-----------:|------------:|--------------:|
|              50 |              100 |          7 |           2 |          28.6 |

Between **29%** (widest pair) and 29% of common neighbourhoods change cluster as the threshold moves. The threshold choice is therefore **load-bearing** for the fine cluster partition - it shifts which small-to-mid neighbourhoods anchor which centroid. This matches the modest silhouette (~0.19) and the family-weighted vs. PCA adjusted Rand index (~0.30) reported in `cluster_summary.md`: the broad segmentation is stable, the exact membership of the middle clusters is not. The n >= 100 rule is retained for the reasons above; readers should treat individual cluster membership near the boundary as approximate.

## Full list of excluded neighbourhoods (50)

| Neighbourhood | Listings | Group |
|---|---:|---|
| Sint-Andries | 93 | nan |
| Borgerhout Intra Muros Zuid | 92 | nan |
| Borgerhout Intra Muros Noord | 90 | nan |
| Eilandje | 87 | nan |
| Stuivenberg | 81 | nan |
| Brederode | 80 | nan |
| Harmonie | 68 | nan |
| Oud - Berchem | 66 | nan |
| Markgrave | 51 | nan |
| Haringrode | 49 | nan |
| Zurenborg | 45 | nan |
| Borgerhout Extra Muros | 39 | nan |
| Dam | 30 | nan |
| Deurne Zuid West | 29 | nan |
| Groenenhoek | 24 | nan |
| Kiel | 20 | nan |
| Hoogte | 19 | nan |
| Linkeroever | 17 | nan |
| Nieuw - Kwartier Oost | 17 | nan |
| Deurne Noord | 16 | nan |
| Deurne Zuid Oost | 15 | nan |
| Middelheim | 15 | nan |
| Oud - Merksem | 14 | nan |
| Hoboken - Centrum | 13 | nan |
| Oosterveld - Elsdonk | 12 | nan |
| Nieuw - Zuid | 11 | nan |
| Deurne Dorp - Gallifort | 10 | nan |
| Deurne Oost | 9 | nan |
| Ekeren Centrum | 7 | nan |
| Nieuw - Kwartier West | 7 | nan |
| Wilrijk Centrum | 7 | nan |
| Hoboken - Noord | 6 | nan |
| Merksem - Heide | 6 | nan |
| Tentoonstellingswijk | 5 | nan |
| Valaar | 5 | nan |
| Rivierenhof | 4 | nan |
| Donk | 3 | nan |
| Petroleum - Zuid | 3 | nan |
| Neerland | 2 | nan |
| Tuinwijk | 2 | nan |
| Deurne Vlieghaven | 1 | nan |
| Hoboken - West | 1 | nan |
| Hoboken - Zuidoost | 1 | nan |
| Koornbloem | 1 | nan |
| Lambrechtshoeken | 1 | nan |
| Leugenberg | 1 | nan |
| Luchtbal | 1 | nan |
| Nieuwdreef | 1 | nan |
| Polder | 1 | nan |
| Schoonbroek-Rozemaai | 1 | nan |

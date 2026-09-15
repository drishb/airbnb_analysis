# Excluded Neighbourhoods

The neighbourhood table retains all **156** neighbourhoods. Ranked tables, clustering, and maps use only the **32** with at least **100** listings. This report covers the **124** that are excluded from those outputs.

## What the exclusion removes

- Neighbourhoods excluded: **124** of 156 (79%)
- Listings in excluded neighbourhoods: **2,539** of 35,724 (**7.1%**)
- Excluded neighbourhoods hold **1** to **99** listings each; 5 sit within 10 of the threshold (Grajaú (99), Joá (98), São Cristóvão (97), Estácio (95), Campo Grande (91)).

The exclusion trades 7.1% of listing volume for indicator stability. The retained neighbourhoods still cover 92.9% of the market by listing count.

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
|              50 |              100 |         32 |          15 |          46.9 |
|             100 |              200 |         24 |           1 |           4.2 |
|              50 |              200 |         24 |          14 |          58.3 |

Between **58%** (widest pair) and 4% of common neighbourhoods change cluster as the threshold moves. The threshold choice is therefore **load-bearing** for the fine cluster partition - it shifts which small-to-mid neighbourhoods anchor which centroid. This matches the modest silhouette (~0.19) and the family-weighted vs. PCA adjusted Rand index (~0.30) reported in `cluster_summary.md`: the broad segmentation is stable, the exact membership of the middle clusters is not. The n >= 100 rule is retained for the reasons above; readers should treat individual cluster membership near the boundary as approximate.

## Full list of excluded neighbourhoods (124)

| Neighbourhood | Listings | Group |
|---|---:|---|
| Grajaú | 99 | nan |
| Joá | 98 | nan |
| São Cristóvão | 97 | nan |
| Estácio | 95 | nan |
| Campo Grande | 91 | nan |
| Curicica | 86 | nan |
| Andaraí | 83 | nan |
| Praça da Bandeira | 78 | nan |
| Barra de Guaratiba | 75 | nan |
| Guaratiba | 75 | nan |
| Pechincha | 73 | nan |
| Engenho de Dentro | 72 | nan |
| Anil | 60 | nan |
| Alto da Boa Vista | 59 | nan |
| Jardim Guanabara | 59 | nan |
| Méier | 56 | nan |
| Engenho Novo | 51 | nan |
| Todos os Santos | 42 | nan |
| Cachambi | 40 | nan |
| Irajá | 37 | nan |
| Praça Seca | 34 | nan |
| Saúde | 33 | nan |
| Paquetá | 32 | nan |
| São Francisco Xavier | 31 | nan |
| Tanque | 30 | nan |
| Cidade Nova | 28 | nan |
| Gamboa | 27 | nan |
| Brás de Pina | 26 | nan |
| Portuguesa | 26 | nan |
| Riachuelo | 26 | nan |
| Rocha | 26 | nan |
| Gardênia Azul | 25 | nan |
| Encantado | 24 | nan |
| Rocinha | 24 | nan |
| Del Castilho | 23 | nan |
| Bangu | 22 | nan |
| Bonsucesso | 22 | nan |
| Penha | 21 | nan |
| Santa Cruz | 21 | nan |
| Mangueira | 19 | nan |
| Lins de Vasconcelos | 17 | nan |
| Santo Cristo | 17 | nan |
| Vila Valqueire | 16 | nan |
| Pedra de Guaratiba | 15 | nan |
| Piedade | 15 | nan |
| Maria da Graça | 14 | nan |
| Tauá | 14 | nan |
| Vila da Penha | 14 | nan |
| Bento Ribeiro | 13 | nan |
| Campinho | 13 | nan |
| Cidade de Deus | 13 | nan |
| Cosmos | 13 | nan |
| Jardim Sulacap | 13 | nan |
| Marechal Hermes | 13 | nan |
| Realengo | 13 | nan |
| Sampaio | 13 | nan |
| Vasco da Gama | 12 | nan |
| Guadalupe | 11 | nan |
| Jardim Carioca | 11 | nan |
| Olaria | 11 | nan |
| Padre Miguel | 11 | nan |
| Parque Anchieta | 11 | nan |
| Quintino Bocaiúva | 11 | nan |
| Ramos | 11 | nan |
| Higienópolis | 10 | nan |
| Paciência | 10 | nan |
| Benfica | 9 | nan |
| Madureira | 9 | nan |
| Osvaldo Cruz | 9 | nan |
| Cacuia | 8 | nan |
| Cascadura | 8 | nan |
| Moneró | 8 | nan |
| Pilares | 8 | nan |
| Sepetiba | 8 | nan |
| Vicente de Carvalho | 8 | nan |
| Abolição | 7 | nan |
| Anchieta | 7 | nan |
| Catumbi | 7 | nan |
| Engenho da Rainha | 7 | nan |
| Inhaúma | 7 | nan |
| Magalhães Bastos | 7 | nan |
| Santíssimo | 7 | nan |
| Senador Vasconcelos | 7 | nan |
| Tomás Coelho | 7 | nan |
| Freguesia (Ilha) | 6 | nan |
| Jacaré | 6 | nan |
| Pavuna | 6 | nan |
| Ricardo de Albuquerque | 6 | nan |
| Cocotá | 5 | nan |
| Parada de Lucas | 5 | nan |
| Senador Camará | 5 | nan |
| Cordovil | 4 | nan |
| Galeão | 4 | nan |
| Penha Circular | 4 | nan |
| Pitangueiras | 4 | nan |
| Vila Kosmos | 4 | nan |
| Água Santa | 4 | nan |
| Bancários | 3 | nan |
| Barros Filho | 3 | nan |
| Coelho Neto | 3 | nan |
| Complexo do Alemão | 3 | nan |
| Grumari | 3 | nan |
| Inhoaíba | 3 | nan |
| Ribeira | 3 | nan |
| Rocha Miranda | 3 | nan |
| Vaz Lobo | 3 | nan |
| Vigário Geral | 3 | nan |
| Vila Militar | 3 | nan |
| Caju | 2 | nan |
| Cidade Universitária | 2 | nan |
| Colégio | 2 | nan |
| Deodoro | 2 | nan |
| Engenheiro Leal | 2 | nan |
| Honório Gurgel | 2 | nan |
| Manguinhos | 2 | nan |
| Praia da Bandeira | 2 | nan |
| Campo dos Afonsos | 1 | nan |
| Cavalcanti | 1 | nan |
| Gericinó | 1 | nan |
| Jacarezinho | 1 | nan |
| Jardim América | 1 | nan |
| Maré | 1 | nan |
| Parque Colúmbia | 1 | nan |
| Vista Alegre | 1 | nan |

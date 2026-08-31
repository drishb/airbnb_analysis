# Excluded Neighbourhoods

The neighbourhood table retains all **264** neighbourhoods. Ranked tables, clustering, and maps use only the **79** with at least **100** listings. This report covers the **185** that are excluded from those outputs.

## What the exclusion removes

- Neighbourhoods excluded: **185** of 264 (70%)
- Listings in excluded neighbourhoods: **5,658** of 33,067 (**17.1%**)
- Excluded neighbourhoods hold **1** to **99** listings each; 6 sit within 10 of the threshold (Hancock Park (99), Northridge (99), Mount Washington (97), Pico-Union (97), Boyle Heights (96), Palmdale (96)).

The exclusion trades 17.1% of listing volume for indicator stability. The retained neighbourhoods still cover 82.9% of the market by listing count.

## Why n >= 100

Three problems affect small neighbourhoods, and all three get worse as n falls.

### (a) Rate instability

Every share indicator - entire-home share, 30-night-minimum share, no-review share - can only take values that are multiples of 1/n. A neighbourhood with 12 listings produces entire-home shares in steps of 8.3%, and moving one listing shifts the value by that much. The ranking would then order neighbourhoods partly on which side of a rounding step they happen to land.

### (b) Mechanical HHI inflation

The Herfindahl-Hirschman index has a floor of 1/n. A 10-listing neighbourhood cannot score below 0.10 even if all 10 hosts are distinct - it would read as moderately concentrated purely from being small. Host concentration is one of the eight indicator families, so this pushes small neighbourhoods toward the "commercialised" end of the segmentation as an artifact of size.

### (c) Clustering distortion

K-means minimises within-cluster variance. A small neighbourhood with an extreme indicator value - easy to produce when n is small - pulls a centroid toward itself and can end up alone in its own cluster, spending a segment on noise instead of a real market type.

## Threshold sensitivity (req 41)

_Pending: the n = 50 / 100 / 200 cluster-stability comparison is produced by task 4.6 once the clustering stage (task 6.0) exists. It will report how many neighbourhoods change cluster assignment between thresholds; if that number is small, the choice of 100 is not load-bearing._

## Full list of excluded neighbourhoods (185)

| Neighbourhood | Listings | Group |
|---|---:|---|
| Hancock Park | 99 | City of Los Angeles |
| Northridge | 99 | City of Los Angeles |
| Mount Washington | 97 | City of Los Angeles |
| Pico-Union | 97 | City of Los Angeles |
| Boyle Heights | 96 | City of Los Angeles |
| Palmdale | 96 | Other Cities |
| Atwater Village | 89 | City of Los Angeles |
| Monrovia | 87 | Other Cities |
| Rosemead | 85 | Other Cities |
| Larchmont | 84 | City of Los Angeles |
| South Pasadena | 84 | Other Cities |
| Lawndale | 81 | Other Cities |
| West Adams | 81 | City of Los Angeles |
| Carson | 79 | Other Cities |
| Hyde Park | 79 | City of Los Angeles |
| Walnut | 79 | Other Cities |
| Glassell Park | 78 | City of Los Angeles |
| East San Gabriel | 77 | Unincorporated Areas |
| Playa Vista | 77 | City of Los Angeles |
| Sun Valley | 77 | City of Los Angeles |
| West Hills | 76 | City of Los Angeles |
| View Park-Windsor Hills | 75 | Unincorporated Areas |
| Baldwin Hills/Crenshaw | 74 | City of Los Angeles |
| Vermont Square | 74 | City of Los Angeles |
| Winnetka | 74 | City of Los Angeles |
| Rancho Palos Verdes | 73 | Other Cities |
| Lake Balboa | 70 | City of Los Angeles |
| Carthay | 69 | City of Los Angeles |
| El Sereno | 69 | City of Los Angeles |
| Azusa | 66 | Other Cities |
| Historic South-Central | 66 | City of Los Angeles |
| Lincoln Heights | 66 | City of Los Angeles |
| Montecito Heights | 66 | City of Los Angeles |
| Toluca Lake | 66 | City of Los Angeles |
| University Park | 65 | City of Los Angeles |
| Whittier | 63 | Other Cities |
| Canoga Park | 61 | City of Los Angeles |
| Glendora | 61 | Other Cities |
| Jefferson Park | 61 | City of Los Angeles |
| Chinatown | 59 | City of Los Angeles |
| Downey | 57 | Other Cities |
| Bel-Air | 56 | City of Los Angeles |
| Calabasas | 55 | Other Cities |
| Leimert Park | 54 | City of Los Angeles |
| Chatsworth | 53 | City of Los Angeles |
| Claremont | 53 | Other Cities |
| Lakewood | 51 | Other Cities |
| Del Aire | 50 | Unincorporated Areas |
| Covina | 48 | Other Cities |
| Industry | 47 | Other Cities |
| Ladera Heights | 47 | Unincorporated Areas |
| North Hills | 45 | City of Los Angeles |
| East Pasadena | 43 | Unincorporated Areas |
| Granada Hills | 43 | City of Los Angeles |
| Adams-Normandie | 41 | City of Los Angeles |
| Green Meadows | 41 | City of Los Angeles |
| La Canada Flintridge | 41 | Other Cities |
| San Dimas | 40 | Other Cities |
| Agoura Hills | 37 | Other Cities |
| Harbor Gateway | 37 | City of Los Angeles |
| Signal Hill | 37 | Other Cities |
| Windsor Square | 37 | City of Los Angeles |
| Pico Rivera | 36 | Other Cities |
| Cheviot Hills | 35 | City of Los Angeles |
| Norwalk | 33 | Other Cities |
| Montebello | 32 | Other Cities |
| West Carson | 32 | Unincorporated Areas |
| Westmont | 31 | Unincorporated Areas |
| Wilmington | 31 | City of Los Angeles |
| Baldwin Park | 30 | Other Cities |
| Rancho Park | 30 | City of Los Angeles |
| Bellflower | 29 | Other Cities |
| Lennox | 28 | Unincorporated Areas |
| Sylmar | 27 | City of Los Angeles |
| Watts | 27 | City of Los Angeles |
| Century City | 26 | City of Los Angeles |
| Lomita | 26 | Other Cities |
| Shadow Hills | 26 | City of Los Angeles |
| Beverlywood | 25 | City of Los Angeles |
| Sierra Madre | 25 | Other Cities |
| Chesterfield Square | 23 | City of Los Angeles |
| Elysian Valley | 23 | City of Los Angeles |
| Mayflower Village | 23 | Unincorporated Areas |
| Cerritos | 22 | Other Cities |
| Panorama City | 22 | City of Los Angeles |
| San Pasqual | 22 | Unincorporated Areas |
| South San Gabriel | 22 | Unincorporated Areas |
| Tujunga | 22 | City of Los Angeles |
| Valinda | 21 | Unincorporated Areas |
| Duarte | 20 | Other Cities |
| Unincorporated Catalina Island | 20 | Unincorporated Areas |
| Vermont Knolls | 20 | City of Los Angeles |
| Harbor City | 19 | City of Los Angeles |
| La Crescenta-Montrose | 19 | Unincorporated Areas |
| Florence-Firestone | 18 | Unincorporated Areas |
| Manchester Square | 18 | City of Los Angeles |
| North El Monte | 18 | Unincorporated Areas |
| Castaic Canyons | 17 | Unincorporated Areas |
| Elysian Park | 17 | City of Los Angeles |
| Lynwood | 17 | Other Cities |
| South Whittier | 17 | Unincorporated Areas |
| Compton | 16 | Other Cities |
| Griffith Park | 16 | City of Los Angeles |
| La Habra Heights | 16 | Other Cities |
| La Verne | 16 | Other Cities |
| South Gate | 16 | Other Cities |
| Porter Ranch | 15 | City of Los Angeles |
| San Marino | 15 | Other Cities |
| Cypress Park | 14 | City of Los Angeles |
| Harvard Park | 14 | City of Los Angeles |
| Agua Dulce | 13 | Unincorporated Areas |
| Alondra Park | 13 | Unincorporated Areas |
| Gramercy Park | 13 | City of Los Angeles |
| Pacoima | 13 | City of Los Angeles |
| Palos Verdes Estates | 13 | Other Cities |
| Vermont-Slauson | 13 | City of Los Angeles |
| Veterans Administration | 13 | Unincorporated Areas |
| La Puente | 12 | Other Cities |
| Southeast Antelope Valley | 12 | Unincorporated Areas |
| Willowbrook | 12 | Unincorporated Areas |
| Castaic | 11 | Unincorporated Areas |
| Central-Alameda | 11 | City of Los Angeles |
| Charter Oak | 11 | Unincorporated Areas |
| Paramount | 11 | Other Cities |
| Westlake Village | 11 | Other Cities |
| Artesia | 10 | Other Cities |
| Avocado Heights | 10 | Unincorporated Areas |
| Maywood | 10 | Other Cities |
| Northwest Palmdale | 10 | Unincorporated Areas |
| Unincorporated Santa Susana Mountains | 10 | Unincorporated Areas |
| Green Valley | 9 | Unincorporated Areas |
| Mission Hills | 9 | City of Los Angeles |
| Northeast Antelope Valley | 9 | Unincorporated Areas |
| Quartz Hill | 9 | Unincorporated Areas |
| San Fernando | 9 | Other Cities |
| Stevenson Ranch | 9 | Unincorporated Areas |
| West Puente Valley | 9 | Unincorporated Areas |
| Broadway-Manchester | 8 | City of Los Angeles |
| La Mirada | 8 | Other Cities |
| Lake Los Angeles | 7 | Unincorporated Areas |
| Rolling Hills Estates | 7 | Other Cities |
| South Park | 7 | City of Los Angeles |
| South San Jose Hills | 7 | Unincorporated Areas |
| Sunland | 7 | City of Los Angeles |
| Tujunga Canyons | 7 | Unincorporated Areas |
| Huntington Park | 6 | Other Cities |
| South El Monte | 6 | Other Cities |
| Sun Village | 6 | Unincorporated Areas |
| West Compton | 6 | Unincorporated Areas |
| West Whittier-Los Nietos | 6 | Unincorporated Areas |
| Arleta | 5 | City of Los Angeles |
| Rolling Hills | 5 | Other Cities |
| Sepulveda Basin | 5 | City of Los Angeles |
| Vermont Vista | 5 | City of Los Angeles |
| Athens | 4 | Unincorporated Areas |
| Bell | 4 | Other Cities |
| Bell Gardens | 4 | Other Cities |
| Citrus | 4 | Unincorporated Areas |
| Commerce | 4 | Other Cities |
| Irwindale | 4 | Other Cities |
| Rancho Dominguez | 4 | Unincorporated Areas |
| Val Verde | 4 | Unincorporated Areas |
| Vincent | 4 | Unincorporated Areas |
| Acton | 3 | Unincorporated Areas |
| Angeles Crest | 3 | Unincorporated Areas |
| Desert View Highlands | 3 | Unincorporated Areas |
| East Whittier | 3 | Unincorporated Areas |
| Florence | 3 | City of Los Angeles |
| North Whittier | 3 | Unincorporated Areas |
| Universal City | 3 | Unincorporated Areas |
| Bradbury | 2 | Other Cities |
| East Compton | 2 | Unincorporated Areas |
| Hasley Canyon | 2 | Unincorporated Areas |
| Lake View Terrace | 2 | City of Los Angeles |
| Leona Valley | 2 | Unincorporated Areas |
| Lopez/Kagel Canyons | 2 | Unincorporated Areas |
| Santa Fe Springs | 2 | Other Cities |
| Vernon | 2 | Other Cities |
| Cudahy | 1 | Other Cities |
| Hawaiian Gardens | 1 | Other Cities |
| Lake Hughes | 1 | Unincorporated Areas |
| Northwest Antelope Valley | 1 | Unincorporated Areas |
| Ridge Route | 1 | Unincorporated Areas |
| South Diamond Bar | 1 | Unincorporated Areas |
| Whittier Narrows | 1 | Unincorporated Areas |

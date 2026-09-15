"""
Central configuration. PRD requirement 62: every landmark coordinate and
coastline vertex is a literal constant, with a source comment.
Nothing in this project reads geometry from an external file.

Multi-dataset note: this pipeline runs against four Inside Airbnb single-city
snapshots (data/). Everything that is genuinely city-specific - landmarks,
coastline/riverfront/harbourfront polyline, cluster labels and their fit
guards, the text-suppression vocabulary, the tourism/upmarket/commercial
hypothesis, and whether `neighbourhood_group` exists at all - lives in the
DATASETS registry below and is switched in with `select_dataset(key)`. Every
module still reads plain `config.X` module-level attributes; `select_dataset`
just repoints them, so no other file needs to know a registry exists.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# --- Reproducibility (PRD req 69) ----------------------------------------

RANDOM_SEED = 42

# --- Figures (PRD req 60, 61, PRD §6) -----------------------------------

FIGURE_DPI = 150
FIGURE_CMAP = "viridis"          # continuous indicators
FIGURE_CMAP_CATEGORICAL = "tab10"  # cluster assignment

# --- Schema (PRD req 1) --------------------------------------------------
# Identical across all four datasets.

EXPECTED_COLUMNS = [
    "id", "name", "host_id", "host_name",
    "neighbourhood_group", "neighbourhood",
    "latitude", "longitude", "room_type", "price",
    "minimum_nights", "number_of_reviews", "last_review",
    "reviews_per_month", "calculated_host_listings_count",
    "availability_365",
]

# --- Cleaning parameters (PRD req 3, 4) ----------------------------------

WINSORIZE_LOWER_PCT = 0.01
WINSORIZE_UPPER_PCT = 0.99

# --- Analysis thresholds -------------------------------------------------

MIN_LISTINGS_PER_NEIGHBOURHOOD = 100        # PRD req 38
SENSITIVITY_THRESHOLDS = [50, 100, 200]     # PRD req 41
COVID_CUTOFF = "2020-03-01"                 # PRD req 35
REVIEWS_PER_STAY = 0.5                      # PRD req 20, Inside Airbnb convention
REVENUE_NIGHTS_CAP = 5                      # PRD req 20, capped variant
LONG_STAY_THRESHOLD = 30    # nights; regulatory meaning is per-dataset (REGULATION_NOTE)

# --- Descriptive-only columns --------------------------------------------
# In the exported table and used for description, never clustering features.
# Room types (and therefore the price_median_<room_type> columns) are the
# same four values in every dataset, so this list is dataset-agnostic.

DESCRIPTIVE_ONLY_COLUMNS = [
    "listing_count",
    "low_confidence",
    "neighbourhood_group",
    "centroid_lat",
    "centroid_lon",
    "price_median_entire_home_apt",
    "price_median_hotel_room",
    "price_median_private_room",
    "price_median_shared_room",
    "rev_divergence_ratio",
    "rev_supporting_listings",
    "tenure_supporting_listings",
    "occ_proxy_unreliable",
]

# --- Text pipeline (PRD req 29, 31) --------------------------------------

TFIDF_MIN_DF = 20
TFIDF_MIN_DF_SENSITIVITY = [10, 20, 50]
NMF_K_RANGE = [5, 6, 7, 8]

# English room-type nouns to suppress from the title vocabulary (task 3.0) -
# reused as-is for the two other English-titled corpora (Antwerp, Amsterdam);
# Rio's entry unions this with a Portuguese equivalent set.
_SUPPRESS_ROOM_TYPE_EN = {
    "room", "rooms", "bedroom", "bedrooms", "bed", "beds", "bath", "baths",
    "bathroom", "bathrooms", "apartment", "apt", "studio", "house", "home",
    "condo", "suite", "guest", "unit", "private", "shared", "entire",
    "loft", "bungalow", "cottage", "duplex", "villa", "guesthouse",
}
_SUPPRESS_ROOM_TYPE_PT = {
    "quarto", "quartos", "casa", "apartamento", "apto", "ap", "suite",
    "suíte", "privado", "compartilhado", "cobertura", "kitnet", "flat",
    "vila", "chalé", "pousada", "hospedagem", "temporada",
}
# Dutch room-type nouns (Antwerp and Amsterdam listing titles mix English
# and Dutch - Phase 1 exploration found raw Dutch leaking into NMF topics,
# e.g. "appartement, kamer, hartje" for Antwerp).
_SUPPRESS_ROOM_TYPE_NL = {
    "kamer", "kamers", "appartement", "huis", "woning", "studio", "suite",
    "logement", "gastenkamer",
}
# General Dutch function words - same rationale/pattern as the Portuguese
# list below, for the same reason (task 3.0's suppression logic).
_DUTCH_STOPWORDS = {
    "de", "het", "een", "en", "van", "in", "op", "met", "voor", "aan", "te",
    "is", "zijn", "dat", "die", "dit", "deze", "niet", "ook", "maar", "of",
    "bij", "uit", "naar", "door", "over", "om", "tot", "als", "dan", "wel",
    "geen", "wordt", "worden", "heeft", "hebben", "kan", "kunnen", "wil",
    "willen", "u", "je", "jij", "wij", "we", "ze", "zij", "er", "nog", "al",
}

# A short literal Portuguese stopword list for the Rio corpus (titles are a
# Portuguese/English mix). No NLTK - literal constant, consistent with the
# project's existing "no NLTK" choice (README, task 8.6) and req 61's
# allowance for standard package resources; this is smaller than even that,
# a hand-picked function-word list for short listing titles.
_PORTUGUESE_STOPWORDS = {
    "a", "à", "às", "ao", "aos", "o", "os", "as", "um", "uma", "uns", "umas",
    "de", "do", "da", "dos", "das", "em", "no", "na", "nos", "nas", "por",
    "para", "pra", "com", "sem", "sobre", "entre", "até", "desde", "e", "ou",
    "mas", "que", "se", "não", "sim", "é", "são", "foi", "ser", "estar",
    "está", "estão", "ter", "tem", "têm", "há", "muito", "muita", "muitos",
    "muitas", "mais", "menos", "bem", "bom", "boa", "este", "esta", "estes",
    "estas", "esse", "essa", "esses", "essas", "isso", "isto", "aquele",
    "aquela", "seu", "sua", "seus", "suas", "meu", "minha", "meus", "minhas",
    "nosso", "nossa", "eu", "você", "voce", "nós", "vc", "ele", "ela",
    "eles", "elas", "como", "quando", "onde", "também", "tambem", "já", "ja",
    "ainda", "aqui", "ali", "lá", "la",
}

# --- Clustering (PRD req 51-53) ------------------------------------------
# CLUSTER_K_RANGE is the usual sweep ceiling (k_diagnostics clamps it down
# for thin datasets); CLUSTER_K - the chosen k - is per-dataset, since a
# 7-neighbourhood dataset (Antwerp) cannot support the same k as LA's 79.

CLUSTER_K_RANGE = list(range(2, 11))
PCA_VARIANCE_RETAINED = 0.85
KMEANS_N_INIT = 10

# Upmarket/commercial marketing-register hypothesis words (req 34) - kept
# identical across datasets; only the "tourism" sub-list is landmark-specific
# and lives per-dataset below.
_HYPOTHESIS_UPMARKET = ["luxury", "modern", "renovated", "designer", "loft",
                        "historic", "stylish"]
_HYPOTHESIS_COMMERCIAL = ["unit", "apt", "suite", "studio apt", "no"]

# The 7 indicator families whose feature names do not depend on landmark
# choice (only "tourism" does - its distance columns are named after
# LANDMARKS' keys, so it is built per-dataset alongside them).
_COMMON_FAMILIES: dict[str, list[str]] = {
    "host_concentration": [
        "host_hhi", "host_share_10plus", "host_top5_share",
        "host_multilisting_share",
    ],
    "regulatory": ["reg_min30_share", "reg_min_nights_median"],
    "tenure": ["tenure_months_median"],
    "revenue_occupancy": [
        "rev_uncapped_median", "rev_capped_median",
        "occ_booked_days_median", "occ_zero_availability_share",
    ],
    "price": ["price_median", "price_iqr", "price_cv", "price_gini"],
    "inactivity": [
        "inactivity_never_reviewed_share", "inactivity_stale_since_covid_share",
    ],
    "text": [f"topic_{i}_loading" for i in range(5)],
}


def _tourism_family(landmark_keys: list[str]) -> list[str]:
    """Tourism family member names - depend on LANDMARKS' keys, plus the
    fixed `dist_coast_km` column every dataset computes (geo.py names it
    that regardless of whether it's an ocean, river, or harbour distance -
    see COASTLINE_LABEL for the human-readable distinction)."""
    return [
        "tour_reviews_per_month_mean", "tour_reviews_per_month_median",
        "tour_reviews_total_mean", "tour_entire_home_share",
        *[f"tour_dist_{k}_km_median" for k in landmark_keys],
        "tour_dist_coast_km_median",
    ]


# ===========================================================================
# LA (default) - the fully-built, fully-labelled reference dataset.
# ===========================================================================

def _la() -> dict:
    landmarks = {
        "hollywood":  (34.1016, -118.3400),   # Hollywood Blvd & Highland Ave
        "downtown":   (34.0537, -118.2428),   # LA City Hall
        "universal":  (34.1381, -118.3534),   # Universal Studios Hollywood
        "disneyland": (33.8121, -117.9190),   # Disneyland Park, Anaheim
    }
    return dict(
        DATA_FILE=PROJECT_ROOT / "data" / "listings_California.csv",
        OUTPUT_DIR=PROJECT_ROOT / "outputs",
        FIGURE_DIR=PROJECT_ROOT / "outputs" / "figures",
        CITY_LABEL="LA County",
        HAS_NEIGHBOURHOOD_GROUP=True,
        FIGURE_CAPTION=(
            "Inside Airbnb snapshot of LA County, scraped ~August 2020. "
            "Single cross-section: shows market structure at one point in time, not change. "
            "Scraped mid-pandemic — 44.7% of reviewed listings had no review since March 2020, "
            "so activity and inactivity measures reflect COVID conditions, not baseline demand."
        ),
        LANDMARKS=landmarks,
        # Simplified LA County shoreline, north-west to south-east. 11
        # vertices; straight-line segments stay within ~1 km of the true
        # shore, far finer than the neighbourhood scale this operates at.
        COASTLINE=[
            (34.0000, -118.8060),   # Point Dume, Malibu
            (34.0369, -118.6770),   # Malibu Pier
            (34.0400, -118.5700),   # Topanga Beach
            (34.0089, -118.4973),   # Santa Monica Pier
            (33.9850, -118.4695),   # Venice Beach
            (33.9200, -118.4310),   # Dockweiler / LAX
            (33.8847, -118.4109),   # Manhattan Beach
            (33.8000, -118.4000),   # Redondo / Palos Verdes west
            (33.7400, -118.3900),   # Palos Verdes south
            (33.7100, -118.2900),   # San Pedro
            (33.7550, -118.1900),   # Long Beach
        ],
        COASTLINE_LABEL="Pacific coastline",
        # Task 1.8 decision: Santa Catalina Island sits ~35 km offshore.
        # Excluded from the polyline; distance-to-coast set to 0 instead of
        # measured to the mainland (geo.add_distance_columns).
        ISLAND_NEIGHBOURHOODS=["Avalon", "Unincorporated Catalina Island"],
        CLUSTER_K=5,
        INDICATOR_FAMILIES={
            "tourism": _tourism_family(list(landmarks)),
            **_COMMON_FAMILIES,
        },
        # LA place names appearing often enough in titles to pollute NMF
        # topics with geography rather than marketing register (task 3.0).
        SUPPRESS_PLACE_EXTRA={
            "la", "los", "angeles", "ca", "california", "hollywood", "venice",
            "malibu", "pasadena", "burbank", "monica", "santa", "beverly",
            "hills", "beach", "marina", "rey", "del", "culver", "glendale",
            "anaheim", "disney", "disneyland", "universal", "ucla", "usc",
            "dtla", "downtown", "westside", "valley", "oc", "socal", "weho",
            "nomo", "koreatown",
        },
        SUPPRESS_ROOM_TYPE=set(_SUPPRESS_ROOM_TYPE_EN),
        EXTRA_STOPWORDS=set(),
        HYPOTHESIS={
            "tourism": ["beach", "hollywood", "steps", "disney", "universal", "walk"],
            "upmarket": list(_HYPOTHESIS_UPMARKET),
            "commercial": list(_HYPOTHESIS_COMMERCIAL),
        },
        # Assigned POST-HOC (task 6.7) after fitting K-means at k=5 and
        # reading the centroid table in original units:
        #   0  Long-stay/regulation-exempt core - median min_nights 27, 55%
        #      at 30+ nights, lowest tourist activity. Koreatown, Hollywood,
        #      Westwood, Mid-Wilshire.
        #   1  Outer suburban budget - cheapest ($83), farthest out, lowest
        #      concentration. Pasadena, Long Beach, Glendale, Torrance.
        #   2  Island resort, single operator - Avalon alone: HHI 0.42,
        #      top-5 share 0.79, 97% entire-home.
        #   3  Upmarket hillside & Westside - highest price ($256) and
        #      price Gini (0.59). Beverly Hills, Malibu, Bel-Air, Pacific
        #      Palisades, Hollywood Hills.
        #   4  Established high-turnover tourist - most reviews/listing (42),
        #      highest revenue, longest tenure. Venice, Silver Lake, WeHo,
        #      Echo Park, Studio City.
        CLUSTER_LABELS={
            0: "Long-stay / regulation-exempt core",
            1: "Outer suburban budget, owner-hosted",
            2: "Island resort, single operator",
            3: "Upmarket hillside & Westside",
            4: "Established high-turnover tourist",
        },
        CLUSTER_LABEL_GUARDS=[
            ("reg_min_nights_median", "idxmax", 0),   # long-stay core
            ("price_gini", "idxmax", 3),              # upmarket = most unequal
            ("host_hhi", "idxmax", 2),                # Avalon, single operator
            ("n_neighbourhoods", "idxmin", 2),        # Avalon, alone
            ("tenure_months_median", "idxmax", 4),    # high-turnover, long-tenured
            ("price_median", "idxmin", 1),            # cheapest, by elimination
        ],
        CLUSTER_K_JUSTIFICATION=(
            "it sits at a local silhouette maximum (0.19, tied with k=2 for "
            "the best in the range), is where the inertia gain per extra "
            "cluster starts to shrink, yields five centroid profiles that "
            "each describe a recognisable market type, and coincides with "
            "the independently chosen NMF topic count. Larger k fragments "
            "the map into two- and three-neighbourhood clusters without "
            "raising the silhouette. The shortfall against success metric "
            "4's 0.25 bar is a property of the data, not the family "
            "weighting - unweighted standardised features peak at 0.20."
        ),
        PCA_ARI_NOTE=(
            "That is partial agreement. The central long-stay cluster and "
            "the Avalon singleton are stable across both methods; the split "
            "among the outer-suburban, upmarket, and inner-tourist groups is "
            "method-sensitive, consistent with the weak silhouette. The "
            "broad shape of the segmentation holds; the exact partition of "
            "the middle of the distribution should not be over-read."
        ),
        REGULATION_NOTE=(
            "LA's 2019 Home-Sharing Ordinance caps short-term rentals at "
            "120 nights/year and requires primary residence; a 30-night "
            "minimum stay exempts a listing from those rules."
        ),
    )


# ===========================================================================
# Antwerp (data/listings-Belgium.csv - filename says Belgium, coverage is
# the city of Antwerp: lat 51.16-51.35N, lon 4.34-4.49E). 2,422 listings,
# 57 neighbourhoods, only 7 clear the n>=100 threshold - thin.
# ===========================================================================

def _antwerp() -> dict:
    landmarks = {
        "grote_markt":       (51.2211, 4.3997),   # Grote Markt, historic centre
        "centraal_station":  (51.2172, 4.4214),   # Antwerpen-Centraal
        "mas":               (51.2296, 4.4084),   # MAS museum, Eilandje
        "zoo":               (51.2166, 4.4208),   # Antwerp Zoo, by Centraal
    }
    return dict(
        DATA_FILE=PROJECT_ROOT / "data" / "listings-Belgium.csv",
        OUTPUT_DIR=PROJECT_ROOT / "outputs-antwerp",
        FIGURE_DIR=PROJECT_ROOT / "outputs-antwerp" / "figures",
        CITY_LABEL="Antwerp",
        HAS_NEIGHBOURHOOD_GROUP=False,
        FIGURE_CAPTION=(
            "Inside Airbnb snapshot of Antwerp, scraped ~mid-2020 (filename "
            "says \"Belgium\"; coverage is the city of Antwerp only). "
            "Single cross-section: shows market structure at one point in "
            "time, not change. Scraped mid-pandemic, so activity and "
            "inactivity measures may reflect COVID-19 conditions rather "
            "than baseline demand."
        ),
        LANDMARKS=landmarks,
        # Antwerp has no ocean coastline - it sits on the river Scheldt.
        # This polyline follows the Scheldt's east bank through the city
        # (roughly south to north) as the nearest analogue to LA's coast
        # distance; COASTLINE_LABEL keeps the distinction explicit
        # everywhere the number is reported.
        COASTLINE=[
            (51.1900, 4.3900),
            (51.2050, 4.3950),
            (51.2211, 4.3960),
            (51.2350, 4.3980),
            (51.2550, 4.4050),
        ],
        COASTLINE_LABEL="Scheldt riverfront (river, not ocean coast)",
        ISLAND_NEIGHBOURHOODS=[],
        # Only 7 neighbourhoods clear n>=100 - k=5 is valid (k<=n_samples)
        # but thin. Phase 1 placeholder; revisit from the real k-sweep.
        CLUSTER_K=3,
        INDICATOR_FAMILIES={
            "tourism": _tourism_family(list(landmarks)),
            **_COMMON_FAMILIES,
        },
        # `_stopwords()` also auto-adds every token from the real
        # `neighbourhood` labels, so district names do not need to be
        # hand-listed here. "hartje" (Dutch for "in the heart of") added
        # after Phase 1 inspection of topic_model.md showed it leaking as a
        # place-marketing term across multiple topics.
        SUPPRESS_PLACE_EXTRA={
            "antwerp", "antwerpen", "belgium", "belgie", "belgië", "belgique",
            "hartje",
        },
        SUPPRESS_ROOM_TYPE=set(_SUPPRESS_ROOM_TYPE_EN) | set(_SUPPRESS_ROOM_TYPE_NL),
        # Phase 1 found raw Dutch function words (met, op, en, het, van,
        # kamer) leaking into topics - Antwerp titles are a real
        # English/Dutch mix, not English-only as first assumed from a
        # small sample.
        EXTRA_STOPWORDS=set(_DUTCH_STOPWORDS),
        HYPOTHESIS={
            "tourism": ["cathedral", "station", "old town", "diamond", "zoo", "walk"],
            "upmarket": list(_HYPOTHESIS_UPMARKET),
            "commercial": list(_HYPOTHESIS_COMMERCIAL),
        },
        # Assigned POST-HOC (Phase 2) after fitting K-means at k=3 and
        # reading the real centroid table (outputs-antwerp/cluster_summary.md):
        #   0  Outer residential, dispersed hosts - lowest price (EUR68),
        #      lowest host HHI (0.014), longest tenure (23.5mo). Amandus -
        #      Atheneum, Universiteitsbuurt, Zuid.
        #   1  Historic core, tourist-facing - closest to every landmark
        #      (0.9-1.4km median), highest tourism intensity (1.62
        #      reviews/mo mean). Centraal Station, Historisch Centrum,
        #      Theaterbuurt-Meir.
        #   2  High-concentration outlier (Stadspark) - highest host HHI
        #      (0.049) and price Gini (0.65), single neighbourhood.
        CLUSTER_LABELS={
            0: "Outer residential, dispersed hosts",
            1: "Historic core, tourist-facing",
            2: "High-concentration outlier (Stadspark)",
        },
        CLUSTER_LABEL_GUARDS=[
            ("host_hhi", "idxmax", 2),
            ("price_gini", "idxmax", 2),
            ("n_neighbourhoods", "idxmin", 2),
            ("tenure_months_median", "idxmax", 0),
            ("price_median", "idxmin", 0),
            ("tour_reviews_per_month_mean", "idxmax", 1),
        ],
        CLUSTER_K_JUSTIFICATION=(
            "the silhouette peaks at k=2 (0.23) in this 7-neighbourhood "
            "sample, but that split is too coarse to say anything beyond "
            "'cheap vs. not' - k=3 (0.17) separates a small, central "
            "tourist-facing core (Centraal Station, Historisch Centrum, "
            "Theaterbuurt-Meir) from a lower-concentration residential "
            "group and a single high-concentration, high-price-inequality "
            "outlier (Stadspark), a more informative typology despite the "
            "lower score. With only 7 retained neighbourhoods this "
            "segmentation is thin and low-confidence by construction "
            "(§4.10's rationale for the n>=100 rule) - read the member "
            "lists, not the silhouette, as the primary evidence."
        ),
        PCA_ARI_NOTE=(
            "Very low agreement (ARI 0.07). With only 7 retained "
            "neighbourhoods split 3/3/1, both the family-weighted and PCA "
            "solutions are highly sensitive to the exact placement of a "
            "handful of points - the specific 3-way partition should not "
            "be over-read; treat this run as illustrating the method, not "
            "a confident segmentation of Antwerp."
        ),
        REGULATION_NOTE=(
            "No verified local short-term-rental ordinance tying a 30-night "
            "minimum stay to a specific regulatory exemption was available "
            "for this reproduction; reg_min30_share is reported as a "
            "structural long-minimum-stay indicator only, not evidence of "
            "evasion of a specific rule."
        ),
    )


# ===========================================================================
# Amsterdam (data/listings-Netherlands.csv - filename says Netherlands,
# coverage is the city of Amsterdam: lat 52.29-52.43N, lon 4.75-5.03E).
# 18,949 listings, 22 neighbourhoods, all clear n>=100.
# ===========================================================================

def _amsterdam() -> dict:
    landmarks = {
        "dam_square":   (52.3730, 4.8926),   # Dam Square / Royal Palace
        "rijksmuseum":  (52.3600, 4.8852),   # Rijksmuseum, Museumplein
        "anne_frank":   (52.3752, 4.8840),   # Anne Frank House
        "vondelpark":   (52.3579, 4.8686),   # Vondelpark
    }
    return dict(
        DATA_FILE=PROJECT_ROOT / "data" / "listings-Netherlands.csv",
        OUTPUT_DIR=PROJECT_ROOT / "outputs-amsterdam",
        FIGURE_DIR=PROJECT_ROOT / "outputs-amsterdam" / "figures",
        CITY_LABEL="Amsterdam",
        HAS_NEIGHBOURHOOD_GROUP=False,
        FIGURE_CAPTION=(
            "Inside Airbnb snapshot of Amsterdam, scraped ~mid-2020 "
            "(filename says \"Netherlands\"; coverage is the city of "
            "Amsterdam only). Single cross-section: shows market structure "
            "at one point in time, not change. Scraped mid-pandemic, so "
            "activity and inactivity measures may reflect COVID-19 "
            "conditions rather than baseline demand."
        ),
        LANDMARKS=landmarks,
        # Amsterdam's real North Sea coast is ~20 km away (Zandvoort) and
        # is not central to intra-city market structure. The IJ
        # waterfront/harbour north of Centraal Station is the nearer,
        # locally meaningful waterfront analogue; COASTLINE_LABEL keeps the
        # distinction explicit everywhere the number is reported.
        COASTLINE=[
            (52.3730, 4.8500),
            (52.3780, 4.8850),
            (52.3830, 4.9100),
            (52.3850, 4.9400),
            (52.3900, 4.9700),
        ],
        COASTLINE_LABEL="IJ waterfront/harbour (not the North Sea coast)",
        ISLAND_NEIGHBOURHOODS=[],
        CLUSTER_K=5,   # Phase 1 placeholder; revisit from the real k-sweep.
        INDICATOR_FAMILIES={
            "tourism": _tourism_family(list(landmarks)),
            **_COMMON_FAMILIES,
        },
        # "jordaan", "vondelpark", "pijp", "east"/"west" added after Phase 1
        # inspection of topic_model.md: hosts write district/landmark names
        # in English ("Amsterdam East/West", "De Pijp", "Jordaan",
        # "Vondelpark") often enough to dominate topics on their own.
        SUPPRESS_PLACE_EXTRA={
            "amsterdam", "adam", "netherlands", "holland", "dutch", "nl",
            "jordaan", "vondelpark", "pijp", "east", "west", "noord", "zuid",
        },
        SUPPRESS_ROOM_TYPE=set(_SUPPRESS_ROOM_TYPE_EN) | set(_SUPPRESS_ROOM_TYPE_NL),
        EXTRA_STOPWORDS=set(_DUTCH_STOPWORDS),
        HYPOTHESIS={
            "tourism": ["canal", "museum", "central", "dam", "park", "walk"],
            "upmarket": list(_HYPOTHESIS_UPMARKET),
            "commercial": list(_HYPOTHESIS_COMMERCIAL),
        },
        # Assigned POST-HOC (Phase 2) after fitting K-means at k=5 and
        # reading the real centroid table (outputs-amsterdam/cluster_summary.md):
        #   0  City centre, premium tourist core - highest price (EUR150),
        #      closest to every landmark (1.0-2.5km), highest revenue
        #      (EUR3257 uncapped). Centrum-Oost, Centrum-West.
        #   1  Established inner ring, entire-home dominant - largest
        #      cluster (12,674 listings), highest entire-home share (0.82),
        #      long tenure (38.9mo). 9 neighbourhoods incl. De Pijp, Zuid,
        #      Oud-Oost.
        #   2  Outer suburban, mixed room types - 5-6km out, lower
        #      entire-home share (0.59), lowest revenue (EUR1123
        #      uncapped). 8 neighbourhoods incl. Bijlmer-Centrum, Osdorp.
        #   3  Outer periphery, room-share dominant (Gaasperdam-Driemond) -
        #      farthest out (9-11km), lowest entire-home share (0.39),
        #      highest 30-night-minimum share (0.048). Single neighbourhood.
        #   4  Newer/outlying development, volatile pricing - highest
        #      price CV (1.08), shortest tenure (29.8mo), only cluster
        #      with median min-nights 3. IJburg - Zeeburgereiland,
        #      Noord-West.
        CLUSTER_LABELS={
            0: "City centre, premium tourist core",
            1: "Established inner ring, entire-home dominant",
            2: "Outer suburban, mixed room types",
            3: "Outer periphery, room-share dominant (Gaasperdam-Driemond)",
            4: "Newer/outlying development, volatile pricing",
        },
        CLUSTER_LABEL_GUARDS=[
            ("price_median", "idxmax", 0),
            ("tour_entire_home_share", "idxmax", 1),
            ("n_neighbourhoods", "idxmax", 1),
            ("rev_uncapped_median", "idxmin", 2),
            ("tour_entire_home_share", "idxmin", 3),
            ("reg_min_nights_median", "idxmax", 4),
        ],
        CLUSTER_K_JUSTIFICATION=(
            "it is the outright silhouette maximum over the swept range "
            "(0.33, clearing success metric 4's 0.25 bar) and yields five "
            "centroid profiles that separate cleanly on distance-to-centre "
            "and price: a small premium-centre pair, a large "
            "entire-home-dominant inner ring, an outer-suburban group, and "
            "two small outlying/high-variance clusters."
        ),
        PCA_ARI_NOTE=(
            "Moderate agreement - the strongest ARI of the three new "
            "datasets, consistent with this being the one clustering run "
            "that already clears the silhouette bar. The segmentation is "
            "comparatively robust to the weighting/PCA choice; the "
            "mid-distribution boundaries (the outer-suburban and periphery "
            "clusters) are more method-sensitive than the city-centre "
            "vs. rest split."
        ),
        REGULATION_NOTE=(
            "Amsterdam's well-known short-term-rental rule caps total "
            "nights let per calendar year (60, later reduced to 30, "
            "nights/year) — a different mechanism from a per-booking "
            "minimum-stay requirement. `reg_min30_share` (share of listings "
            "with minimum_nights >= 30) does not measure exposure to that "
            "annual cap; no equivalent minimum-stay ordinance was verified "
            "for this reproduction, so the indicator is reported as a "
            "structural signal only, not evidence of evasion of the "
            "annual-cap rule."
        ),
    )


# ===========================================================================
# Rio de Janeiro (data/listings-RIo_de_Janeiro.csv). 35,731 listings, 156
# neighbourhoods, 32 clear n>=100. Titles mix Portuguese and English.
# ===========================================================================

def _rio() -> dict:
    landmarks = {
        "corcovado": (-22.9519, -43.2105),   # Christ the Redeemer
        "sugarloaf":  (-22.9492, -43.1545),   # Pao de Acucar
        "maracana":   (-22.9122, -43.2302),   # Maracana stadium
        "centro":     (-22.9068, -43.1729),   # Centro (downtown)
    }
    return dict(
        DATA_FILE=PROJECT_ROOT / "data" / "listings-RIo_de_Janeiro.csv",
        OUTPUT_DIR=PROJECT_ROOT / "outputs-rio",
        FIGURE_DIR=PROJECT_ROOT / "outputs-rio" / "figures",
        CITY_LABEL="Rio de Janeiro",
        HAS_NEIGHBOURHOOD_GROUP=False,
        FIGURE_CAPTION=(
            "Inside Airbnb snapshot of Rio de Janeiro, scraped ~mid-2020. "
            "Single cross-section: shows market structure at one point in "
            "time, not change. Scraped mid-pandemic, so activity and "
            "inactivity measures may reflect COVID-19 conditions rather "
            "than baseline demand."
        ),
        LANDMARKS=landmarks,
        # Real Atlantic Ocean / Guanabara Bay coastline - the closest LA
        # analogue of the three new cities. West (Recreio) to north-east
        # (Guanabara Bay near Ilha do Governador), 10 vertices covering the
        # highest-volume beach neighbourhoods (Copacabana, Barra da
        # Tijuca, Ipanema, Leblon are the top 4 by listing count).
        COASTLINE=[
            (-23.0170, -43.4650),   # Recreio dos Bandeirantes
            (-23.0050, -43.3650),   # Barra da Tijuca beachfront
            (-23.0250, -43.3100),   # Barra / Sao Conrado transition
            (-22.9930, -43.2500),   # Leblon beach
            (-22.9868, -43.2090),   # Ipanema beach
            (-22.9711, -43.1822),   # Copacabana beach
            (-22.9490, -43.1630),   # Leme, near Sugarloaf
            (-22.9350, -43.1730),   # Botafogo/Flamengo bay shore
            (-22.9068, -43.1729),   # Centro, Guanabara Bay edge
            (-22.8300, -43.2100),   # Guanabara Bay, near Ilha do Governador
        ],
        COASTLINE_LABEL="Atlantic coastline & Guanabara Bay",
        ISLAND_NEIGHBOURHOODS=[],  # revisit in Phase 2 if Ilha do Governador /
                                   # Paquetá show coast-distance anomalies
        CLUSTER_K=5,   # Phase 1 placeholder; revisit from the real k-sweep.
        INDICATOR_FAMILIES={
            "tourism": _tourism_family(list(landmarks)),
            **_COMMON_FAMILIES,
        },
        # "lapa" added after Phase 1 inspection of topic_model.md - a
        # well-known Rio nightlife district leaking as a place-marketing
        # term (`_stopwords()` only auto-suppresses exact `neighbourhood`
        # column values, and titles use the informal "Lapa" rather than
        # the formal neighbourhood label).
        SUPPRESS_PLACE_EXTRA={
            "rio", "janeiro", "rj", "brasil", "brazil", "lapa",
        },
        SUPPRESS_ROOM_TYPE=set(_SUPPRESS_ROOM_TYPE_EN) | set(_SUPPRESS_ROOM_TYPE_PT),
        EXTRA_STOPWORDS=set(_PORTUGUESE_STOPWORDS),
        HYPOTHESIS={
            "tourism": ["beach", "copacabana", "ipanema", "sugarloaf", "steps", "walk"],
            "upmarket": list(_HYPOTHESIS_UPMARKET),
            "commercial": list(_HYPOTHESIS_COMMERCIAL),
        },
        # Assigned POST-HOC (Phase 2) after fitting K-means at k=5 and
        # reading the real centroid table (outputs-rio/cluster_summary.md):
        #   0  South Zone periphery, upscale residential - long tenure
        #      (31.1mo, highest), high price (R$339). Barra da Tijuca,
        #      Cosme Velho, Flamengo, Gloria, Gavea, Jardim Botanico, Lagoa.
        #   1  Far periphery, low turnover - farthest from every landmark
        #      (17-23km), shortest tenure (19.1mo, lowest), lowest revenue
        #      (R$546). 9 neighbourhoods incl. Recreio, Vargem Grande,
        #      Camorim.
        #   2  Iconic beachfront tourist core - closest to the coast
        #      (0.37km) and to Corcovado/Sugarloaf, highest revenue by far
        #      (R$2884 uncapped) and highest host concentration.
        #      Copacabana, Ipanema, Leblon, Leme.
        #   3  Inland North Zone, stadium-adjacent - farthest from the
        #      coast (5.7km, highest), closest to Maracana. Jacarepagua,
        #      Maracana, Tijuca, Vila Isabel.
        #   4  Downtown & inner harbour, budget-mixed - lowest price
        #      (R$221) and highest price inequality (Gini 0.68). Botafogo,
        #      Catete, Centro, Humaita, Laranjeiras, Santa Teresa, Urca,
        #      Vidigal.
        CLUSTER_LABELS={
            0: "South Zone periphery, upscale residential",
            1: "Far periphery, low turnover",
            2: "Iconic beachfront tourist core",
            3: "Inland North Zone, stadium-adjacent",
            4: "Downtown & inner harbour, budget-mixed",
        },
        CLUSTER_LABEL_GUARDS=[
            ("rev_uncapped_median", "idxmax", 2),
            ("tour_dist_coast_km_median", "idxmin", 2),
            ("tour_dist_corcovado_km_median", "idxmax", 1),
            ("tenure_months_median", "idxmin", 1),
            ("tour_dist_coast_km_median", "idxmax", 3),
            ("price_median", "idxmin", 4),
            ("price_gini", "idxmax", 4),
            ("tenure_months_median", "idxmax", 0),
        ],
        CLUSTER_K_JUSTIFICATION=(
            "the silhouette peaks at k=2 (0.25) but that only separates the "
            "beachfront core from everywhere else - k=5 (0.17) resolves "
            "that core (Copacabana, Ipanema, Leblon, Leme) from four "
            "further, geographically coherent groups (South Zone upscale, "
            "far periphery, inland North Zone, downtown/inner harbour) and "
            "matches the independently chosen NMF topic count, at some "
            "cost in the silhouette score - the same interpretability-"
            "over-statistic trade-off the LA run made."
        ),
        PCA_ARI_NOTE=(
            "Partial agreement, similar in magnitude to the LA run's 0.30. "
            "The iconic beachfront cluster (Copacabana, Ipanema, Leblon, "
            "Leme) is a strong, geographically obvious grouping likely to "
            "be stable across methods; the split among the inland, "
            "periphery, and South Zone groups is more method-sensitive, "
            "consistent with the modest silhouette."
        ),
        REGULATION_NOTE=(
            "No verified local short-term-rental ordinance tying a 30-night "
            "minimum stay to a specific regulatory exemption was available "
            "for this reproduction; reg_min30_share is reported as a "
            "structural long-minimum-stay indicator only, not evidence of "
            "evasion of a specific rule."
        ),
    )


DATASETS: dict[str, dict] = {
    "la": _la(),
    "antwerp": _antwerp(),
    "amsterdam": _amsterdam(),
    "rio": _rio(),
}


def select_dataset(key: str) -> None:
    """
    Repoint every dataset-specific module-level constant (DATA_FILE,
    OUTPUT_DIR, LANDMARKS, COASTLINE, CLUSTER_LABELS, ...) at the named
    dataset's registry entry. Every other module reads these as plain
    `config.X` attributes, so this is the only place that needs to know a
    registry exists - call it once, before any other module runs.
    """
    if key not in DATASETS:
        raise ValueError(f"unknown dataset {key!r}; choose from {sorted(DATASETS)}")
    globals().update(DATASETS[key])
    global ACTIVE_DATASET
    ACTIVE_DATASET = key


ACTIVE_DATASET: str
select_dataset("la")   # default - preserves pre-multi-dataset behaviour

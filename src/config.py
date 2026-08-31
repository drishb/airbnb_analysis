"""
Central configuration. PRD requirement 62: every landmark coordinate and
coastline vertex is a literal constant defined here, with a source comment.
Nothing in this project reads geometry from an external file.
"""

from pathlib import Path

# --- Paths ---------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "listings_California.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
FIGURE_DIR = OUTPUT_DIR / "figures"

# --- Reproducibility (PRD req 69) ----------------------------------------

RANDOM_SEED = 42

# --- Schema (PRD req 1) --------------------------------------------------

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

# --- Regulatory context (PRD req 17) -------------------------------------

LONG_STAY_THRESHOLD = 30    # nights; >= this exempts a listing from LA's
                            # 2019 Home-Sharing Ordinance (120-night cap +
                            # primary-residence requirement)

# --- Landmarks (PRD req 8, 62) -------------------------------------------
# Coordinates are approximate centroids of each destination, taken from
# public map references. Precision to ~100 m is ample: these feed a
# neighbourhood-median distance measured in kilometres.

LANDMARKS = {
    "hollywood":  (34.1016, -118.3400),   # Hollywood Blvd & Highland Ave
    "downtown":   (34.0537, -118.2428),   # LA City Hall
    "universal":  (34.1381, -118.3534),   # Universal Studios Hollywood
    "disneyland": (33.8121, -117.9190),   # Disneyland Park, Anaheim
}

# --- Island neighbourhoods (task 1.8 decision) ---------------------------
# Santa Catalina Island sits ~35 km offshore. Its listings are excluded from
# the coastline polyline below and flagged instead: a mainland-referenced
# coast distance would report ~30 km for listings that are literally
# beachfront, which is worse than reporting nothing.

ISLAND_NEIGHBOURHOODS = ["Avalon", "Unincorporated Catalina Island"]

# --- Coastline polyline (PRD req 9, 62) ----------------------------------
# Simplified LA County shoreline, north-west to south-east. 11 vertices;
# the PRD requires at least 8. Straight-line segments between these points
# stay within roughly 1 km of the true shore, which is far finer than the
# neighbourhood scale this analysis operates at.

COASTLINE = [
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
]
# Catalina is deliberately absent. See ISLAND_NEIGHBOURHOODS above.

# --- Indicator families (PRD req 50, family weighting) -------------------
# Populated in task 4.0 once all indicator columns exist. Declared here so
# the weighting scheme has a single source of truth.

INDICATOR_FAMILIES: dict[str, list[str]] = {}


# --- Descriptive-only columns (task 2.0 decision) ------------------------
# Real where present, but too sparse to carry a distance metric. Hotel-room
# medians exist for only 18 of the 79 retained neighbourhoods and shared-room
# for 67. K-means cannot accept NaN, and imputing a hotel price for a
# neighbourhood with no hotels would fabricate data. These are reported and
# excluded from clustering features (task 6.0).

DESCRIPTIVE_ONLY_COLUMNS = [
    "price_median_hotel_room",
    "price_median_shared_room",
    "neighbourhood_group",
    "occ_proxy_unreliable",
    "rev_supporting_listings",
    "tenure_supporting_listings",
    "centroid_lat",
    "centroid_lon",
    "listing_count",
]


# --- Text vocabulary suppression (task 3.0 decision) ---------------------
# Fitting NMF over the raw title vocabulary produces topics dominated by
# place names and room types: of 8 topics, 6 were variations on "Santa
# Monica", "private room", "guest house". Those are not findings — they are
# `neighbourhood`, `room_type`, and the five distance columns from task 2.0,
# recovered from the titles. Using them as clustering features would weight
# geography twice.
#
# Suppressing that vocabulary leaves marketing *register*: cozy/clean/quiet,
# modern/new/chic, luxury/spacious/ocean, charming/garden/craftsman. That is
# information the structured columns do not contain, which is the only
# reason to mine the text at all.
#
# This is a researcher choice, not something the data dictated. Both runs
# are reported in topic_model.md so the choice is visible and reviewable.

SUPPRESS_PLACE_EXTRA = {
    "la", "los", "angeles", "ca", "california", "hollywood", "venice",
    "malibu", "pasadena", "burbank", "monica", "santa", "beverly", "hills",
    "beach", "marina", "rey", "del", "culver", "glendale", "anaheim",
    "disney", "disneyland", "universal", "ucla", "usc", "dtla", "downtown",
    "westside", "valley", "oc", "socal", "weho", "nomo", "koreatown",
}

SUPPRESS_ROOM_TYPE = {
    "room", "rooms", "bedroom", "bedrooms", "bed", "beds", "bath", "baths",
    "bathroom", "bathrooms", "apartment", "apt", "studio", "house", "home",
    "condo", "suite", "guest", "unit", "private", "shared", "entire",
    "loft", "bungalow", "cottage", "duplex", "villa", "guesthouse",
}

TFIDF_MIN_DF = 20
TFIDF_MIN_DF_SENSITIVITY = [10, 20, 50]
NMF_K_RANGE = [5, 6, 7, 8]

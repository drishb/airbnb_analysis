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

# --- Figures (PRD req 60, 61, PRD §6) -----------------------------------
# Every figure: >=150 dpi PNG, a perceptually uniform sequential colourmap
# (viridis) for continuous indicators, and a caption stating the snapshot
# date and the pandemic caveat. The caption text is fixed here so it reads
# identically on all ten figures.

FIGURE_DPI = 150
FIGURE_CMAP = "viridis"          # continuous indicators
FIGURE_CMAP_CATEGORICAL = "tab10"  # cluster assignment
FIGURE_CAPTION = (
    "Inside Airbnb snapshot of LA County, scraped ~August 2020. "
    "Single cross-section: shows market structure at one point in time, not change. "
    "Scraped mid-pandemic — 44.7% of reviewed listings had no review since March 2020, "
    "so activity and inactivity measures reflect COVID conditions, not baseline demand."
)

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
# The eight families named in PRD Goal 2. The union of these lists is exactly
# the feature set task 6.0 standardises and weights (31 features). This is an
# explicit map, not derived from column prefixes at runtime, because three
# column groups break a pure prefix rule (task 4.3 decision, agreed with the
# researcher):
#
#   1. `rev_` and `occ_` are one family here. PRD Goal 2 lists
#      "revenue/occupancy" as a single family, so the four columns share one
#      1/sqrt(size) divisor rather than counting as two families.
#   2. `rev_divergence_ratio` is not a feature. It is rev_uncapped_median /
#      rev_capped_median - both already features - so including it
#      triple-counts revenue. It is a trust flag on the estimate, not a
#      market-structure dimension. -> DESCRIPTIVE_ONLY_COLUMNS.
#   3. `price_median_<room_type>` columns are not features. PRD req 26's four
#      statistics are the structural price indicators; the per-room-type
#      medians in req 27 are descriptive detail. -> DESCRIPTIVE_ONLY_COLUMNS.

INDICATOR_FAMILIES: dict[str, list[str]] = {
    "tourism": [
        "tour_reviews_per_month_mean",
        "tour_reviews_per_month_median",
        "tour_reviews_total_mean",
        "tour_entire_home_share",
        "tour_dist_hollywood_km_median",
        "tour_dist_downtown_km_median",
        "tour_dist_universal_km_median",
        "tour_dist_disneyland_km_median",
        "tour_dist_coast_km_median",
    ],
    "host_concentration": [
        "host_hhi",
        "host_share_10plus",
        "host_top5_share",
        "host_multilisting_share",
    ],
    "regulatory": [
        "reg_min30_share",
        "reg_min_nights_median",
    ],
    "tenure": [
        "tenure_months_median",
    ],
    "revenue_occupancy": [
        "rev_uncapped_median",
        "rev_capped_median",
        "occ_booked_days_median",
        "occ_zero_availability_share",
    ],
    "price": [
        "price_median",
        "price_iqr",
        "price_cv",
        "price_gini",
    ],
    "inactivity": [
        "inactivity_never_reviewed_share",
        "inactivity_stale_since_covid_share",
    ],
    "text": [
        "topic_0_loading",
        "topic_1_loading",
        "topic_2_loading",
        "topic_3_loading",
        "topic_4_loading",
    ],
}


# --- Descriptive-only columns ------------------------------------------
# In the exported table and used for description, never clustering features.
# Reasons vary:
#   - hotel/shared room medians: too sparse (task 2.0) - hotel-room medians
#     exist for only 18 of the 79 retained neighbourhoods; imputing a hotel
#     price where there are no hotels would fabricate data.
#   - entire-home/private-room medians, rev_divergence_ratio: redundant with
#     existing features (task 4.3, see INDICATOR_FAMILIES above).
#   - listing_count, *_supporting_listings: counts that re-encode
#     neighbourhood size (handoff decision 8).
#   - the rest: identifiers, flags, coordinates.

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

import numpy as np
import pandas as pd
import pytest

from src import config, ingest


def _fixture(n=50):
    """Minimal valid frame with all 16 columns."""
    rng = np.random.default_rng(0)
    df = pd.DataFrame({
        "id": range(n),
        "name": ["listing"] * n,
        "host_id": rng.integers(1, 10, n),
        "host_name": ["host"] * n,
        "neighbourhood_group": ["City of Los Angeles"] * n,
        "neighbourhood": ["Hollywood"] * n,
        "latitude": rng.uniform(33.9, 34.2, n),
        "longitude": rng.uniform(-118.5, -118.2, n),
        "room_type": ["Entire home/apt"] * n,
        "price": rng.integers(50, 500, n),
        "minimum_nights": rng.integers(1, 40, n),
        "number_of_reviews": rng.integers(1, 50, n),
        "last_review": pd.to_datetime(["2020-01-01"] * n),
        "reviews_per_month": rng.uniform(0.1, 3.0, n),
        "calculated_host_listings_count": rng.integers(1, 5, n),
        "availability_365": rng.integers(0, 365, n),
    })
    # guarantee the nulls clean() asserts on
    df.loc[:4, ["last_review", "reviews_per_month"]] = pd.NaT, np.nan
    df.loc[:4, "number_of_reviews"] = 0
    return df


def test_missing_column_raises():
    df = _fixture().drop(columns=["price"])
    df.to_csv("/tmp/missing.csv", index=False)
    with pytest.raises(ingest.SchemaError, match="missing"):
        ingest.load_raw(__import__("pathlib").Path("/tmp/missing.csv"))


def test_unexpected_column_raises():
    """Task 1.8 decision: strict. Extra columns fail, they do not warn."""
    df = _fixture()
    df["extra"] = 1
    df.to_csv("/tmp/extra.csv", index=False)
    with pytest.raises(ingest.SchemaError, match="unexpected"):
        ingest.load_raw(__import__("pathlib").Path("/tmp/extra.csv"))


def test_zero_price_dropped():
    df = _fixture()
    df.loc[10:12, "price"] = 0
    cleaned, stats = ingest.clean(df)
    assert stats["zero_price_dropped"] == 3
    assert (cleaned["price"] > 0).all()


def test_nulls_preserved():
    cleaned, stats = ingest.clean(_fixture())
    assert stats["last_review_nulls"] == 5
    assert cleaned["reviews_per_month"].isna().sum() == 5


def test_winsorize_creates_separate_column():
    cleaned, stats = ingest.clean(_fixture())
    assert "price_winsorized" in cleaned
    assert "log_price" in cleaned
    assert cleaned["price"].max() >= cleaned["price_winsorized"].max()
    assert np.allclose(np.exp(cleaned["log_price"]), cleaned["price_winsorized"])


def test_island_flag():
    df = _fixture()
    df.loc[0:9, "neighbourhood"] = "Avalon"
    cleaned, stats = ingest.clean(df)
    assert stats["island_listings"] == 10
    assert cleaned.loc[cleaned["neighbourhood"] == "Avalon", "is_island"].all()


def test_review_field_consistency_on_real_data():
    """Skips when the CSV is absent so the suite runs on a fresh clone."""
    if not config.DATA_FILE.exists():
        pytest.skip(f"{config.DATA_FILE} not present")
    assert ingest._consistency_ok(ingest.load_raw())

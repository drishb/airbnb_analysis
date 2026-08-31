import numpy as np
import pandas as pd
from src import indicators_text as txt, config


def test_tokenize_handles_nulls():
    assert txt.tokenize(None) == ""
    assert txt.tokenize(np.nan) == ""
    assert txt.tokenize(3.5) == ""


def test_tokenize_strips_punctuation_and_case():
    assert txt.tokenize("*Beautiful* MASTER Suite/Jacuzzi!") == "beautiful master suite jacuzzi"


def test_suppression_removes_place_words():
    sw = set(txt._stopwords(True, ["Santa Monica", "Culver City"]))
    for w in ("santa", "monica", "culver", "city", "hollywood", "room", "apartment"):
        assert w in sw, w


def test_baseline_keeps_place_words():
    sw = set(txt._stopwords(False, ["Santa Monica"]))
    assert "monica" not in sw
    assert "room" not in sw


def test_loadings_rows_sum_to_one():
    df = pd.DataFrame({"neighbourhood": ["A", "A", "B", "B"]})
    W = np.array([[1.0, 3.0], [2.0, 2.0], [0.0, 4.0], [4.0, 0.0]])
    out = txt.neighbourhood_loadings(df, W)
    assert np.allclose(out.sum(axis=1), 1.0)


def test_hypothesis_check_reports_misses():
    terms = [[("cozy", 1.0), ("clean", 0.9)], [("luxury", 1.0), ("modern", 0.8)]]
    out = txt.compare_to_hypothesis(terms)
    assert out.loc[0, "upmarket_hits"] == 0
    assert out.loc[1, "upmarket_hits"] == 2
    assert (out["commercial_hits"] == 0).all()

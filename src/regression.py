"""
Hedonic log-price regression. PRD requirements 43-48.

An OLS model of log nightly price on listing attributes, fit at the
*listing* level over every cleaned row (req 48) — this stage does not
aggregate, so the n>=100 neighbourhood exclusion does not apply here.

This file grows through task 5.0: 5.1 builds the model frame (here),
5.2 fits with HC3 errors, 5.3-5.4 write the summary, 5.5 plots
diagnostics, 5.6 resolves the neighbourhood-fixed-effects question.
"""

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from . import config

# PRD req 43: the model form is fixed. Categoricals carry an explicit
# reference level so every coefficient reads as "versus this baseline"
# and the mapping does not shift if the data's category counts change:
#   - room_type      -> vs. "Entire home/apt" (the modal type)
#   - neighbourhood_group -> vs. "City of Los Angeles" (the largest group)
# The response is `log_price`, which ingest already defined as
# log(price_winsorized) — winsorised per req 4 / PRD §7.3, so the 1%
# tails do not lever the fit.
FORMULA = (
    'log_price ~ '
    'C(room_type, Treatment(reference="Entire home/apt")) '
    '+ minimum_nights '
    '+ availability_365 '
    '+ calculated_host_listings_count '
    '+ number_of_reviews '
    '+ C(neighbourhood_group, Treatment(reference="City of Los Angeles"))'
)

MODEL_COLUMNS = [
    "log_price",
    "room_type",
    "minimum_nights",
    "availability_365",
    "calculated_host_listings_count",
    "number_of_reviews",
    "neighbourhood_group",
]


def build_model_frame(df: pd.DataFrame) -> pd.DataFrame:
    """
    PRD req 43 + 48: the listing-level frame the hedonic model is fit on —
    every cleaned listing, the seven columns the formula references, no
    aggregation and no neighbourhood exclusion.

    Raises if `log_price` is missing (ingest.clean must run first) or if
    any model column contains a null. None of the seven has nulls in the
    cleaned data: `number_of_reviews` is 0 rather than null for unreviewed
    listings, and `reviews_per_month` — the only review field with nulls —
    is deliberately not in the model.
    """
    missing = [c for c in MODEL_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"model frame is missing column(s) {missing}; "
            "run ingest.clean to add log_price before building the frame"
        )

    frame = df[MODEL_COLUMNS].copy()

    nulls = frame.isna().sum()
    if nulls.any():
        raise ValueError(
            f"model columns contain nulls: {nulls[nulls > 0].to_dict()}. "
            "The hedonic model expects a complete case for every listing."
        )

    print(f"[regression] model frame {frame.shape[0]} listings x "
          f"{frame.shape[1]} columns (all cleaned listings, no exclusion)")
    return frame


def fit_model(frame: pd.DataFrame):
    """
    PRD req 44: OLS fit with heteroskedasticity-robust (HC3) standard
    errors. Price data is strongly heteroskedastic even after the log
    transform — variance rises with room type and location — so the
    classical SEs would understate uncertainty on several coefficients.

    HC3 is applied at fit time, so `.bse`, `.tvalues`, `.pvalues`, and
    `.conf_int()` on the returned results are already the robust versions;
    the point estimates and R^2 are identical to a classical fit.

    Returns the fitted `RegressionResultsWrapper` (used by 5.3-5.5).
    """
    results = smf.ols(FORMULA, data=frame).fit(cov_type="HC3")
    print(f"[regression] OLS fit: n={int(results.nobs)}, "
          f"R^2={results.rsquared:.3f}, "
          f"adj R^2={results.rsquared_adj:.3f}, cov_type={results.cov_type}")
    return results


CONTINUOUS_PREDICTORS = {
    "minimum_nights",
    "availability_365",
    "calculated_host_listings_count",
    "number_of_reviews",
}


def percentage_effects(results) -> pd.DataFrame:
    """
    PRD req 47: the log-price coefficients re-expressed as percentage
    effects on price itself. A reader wants "how much does this move the
    nightly rate", not a shift in log units.

    Both conventional forms are reported (req 5.4 asks for both):
      - approx_pct_effect = 100 * beta
        the small-coefficient rule of thumb.
      - exact_pct_effect  = 100 * (exp(beta) - 1)
        the correct multiplicative effect for any beta.

    They agree to a fraction of a point for |beta| < ~0.1 and diverge
    sharply above it: the room-type dummies run to beta = -1.62, where the
    approximation is off by 30+ points. `exact_pct_effect` is the column
    to read there. The confidence bounds (HC3) are carried through the
    exact transform.

    `kind` says how to read each row: "per +1 unit" for the continuous
    predictors, "vs. reference" for the treatment-coded dummies. The
    intercept is a price level, not an effect, so its percentage columns
    are left blank.
    """
    params = results.params
    conf = results.conf_int()
    conf.columns = ["ci_low", "ci_high"]

    def _kind(name: str) -> str:
        if name == "Intercept":
            return "(baseline level)"
        if name in CONTINUOUS_PREDICTORS:
            return "per +1 unit"
        return "vs. reference"

    out = pd.DataFrame(
        {
            "kind": [_kind(n) for n in params.index],
            "coef_log": params,
            "approx_pct_effect": 100.0 * params,
            "exact_pct_effect": 100.0 * (np.exp(params) - 1.0),
            "exact_pct_ci_low": 100.0 * (np.exp(conf["ci_low"]) - 1.0),
            "exact_pct_ci_high": 100.0 * (np.exp(conf["ci_high"]) - 1.0),
        }
    )

    pct_cols = [
        "approx_pct_effect",
        "exact_pct_effect",
        "exact_pct_ci_low",
        "exact_pct_ci_high",
    ]
    if "Intercept" in out.index:
        out.loc["Intercept", pct_cols] = np.nan

    return out


def _format_percentage_effects(pe: pd.DataFrame) -> str:
    """Render `percentage_effects` as a fixed-width block for the summary."""
    disp = pe.rename(
        columns={
            "coef_log": "coef(log)",
            "approx_pct_effect": "approx %",
            "exact_pct_effect": "exact %",
            "exact_pct_ci_low": "exact % lo",
            "exact_pct_ci_high": "exact % hi",
        }
    )
    pct = lambda v: f"{v:8.2f}"
    body = disp.to_string(
        formatters={
            "coef(log)": lambda v: f"{v:9.4f}",
            "approx %": pct,
            "exact %": pct,
            "exact % lo": pct,
            "exact % hi": pct,
        },
        na_rep="  -  ",
    )
    lines = [
        "",
        "",
        "=" * 78,
        "PERCENTAGE PRICE EFFECTS (PRD req 47)",
        "=" * 78,
        "",
        "The coefficients above are shifts in log(price). Re-expressed as",
        "effects on price:",
        "    approx % = 100 * beta          exact % = 100 * (exp(beta) - 1)",
        "",
        "The two agree while |beta| is small. Past |beta| ~ 0.2 the",
        "approximation overstates the effect: read the exact column for the",
        "room-type dummies (e.g. Private room is -60%, not -92%). CI bounds",
        "are the HC3 interval carried through the exact transform.",
        "'per +1 unit' rows are the effect of one more night / day / listing /",
        "review; 'vs. reference' rows are relative to the categorical baseline.",
        "",
        body,
        "",
    ]
    return "\n".join(lines)


def write_summary(results, path=None) -> str:
    """
    PRD req 45: the full coefficient table — coefficient, standard error,
    test statistic, p-value — plus R^2 and n, written to
    `outputs/regression_summary.txt`.

    The body is `statsmodels`' own summary. Because the fit uses a robust
    covariance, the per-coefficient statistic is the asymptotic **z**, not
    a t — statsmodels labels it accordingly. Task 5.4 appends the
    percentage-effect reading of the log coefficients (`percentage_effects`)
    to this same file.
    """
    path = path or (config.OUTPUT_DIR / "regression_summary.txt")

    header = [
        "HEDONIC LOG-PRICE REGRESSION",
        "=" * 78,
        "",
        "PRD req 43-48. Listing-level OLS over every cleaned listing — no",
        "neighbourhood exclusion (req 48). Response: log(price_winsorized),",
        "winsorised at the 1st/99th percentile per req 4.",
        "Standard errors: heteroskedasticity-robust (HC3), so the reported",
        "per-coefficient statistic is the asymptotic z.",
        "",
        "Formula:",
        f"  {FORMULA}",
        "",
        "Categorical reference levels (coefficients are relative to these):",
        "  room_type            = Entire home/apt",
        "  neighbourhood_group  = City of Los Angeles",
        "",
        "=" * 78,
        "",
    ]

    text = (
        "\n".join(header)
        + str(results.summary())
        + "\n"
        + _format_percentage_effects(percentage_effects(results))
    )
    path.write_text(text, encoding="utf-8")
    print(f"[regression] summary -> {path} "
          f"(R^2={results.rsquared:.3f}, n={int(results.nobs)})")
    return text

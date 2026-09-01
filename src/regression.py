"""
Hedonic log-price regression. PRD requirements 43-48.

An OLS model of log nightly price on listing attributes, fit at the
*listing* level over every cleaned row (req 48) — this stage does not
aggregate, so the n>=100 neighbourhood exclusion does not apply here.

This file grows through task 5.0: 5.1 builds the model frame (here),
5.2 fits with HC3 errors, 5.3-5.4 write the summary, 5.5 plots
diagnostics, 5.6 resolves the neighbourhood-fixed-effects question.
"""

import re
import textwrap

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from . import config


def _deterministic_summary(results) -> str:
    """
    `statsmodels`' summary text with the wall-clock `Date:` / `Time:` fields
    blanked, so `regression_summary.txt` is byte-identical between runs
    (success metric 10 in spirit - it only mandates the CSV, but there is no
    reason for this file to churn). Field widths are preserved so the
    column alignment of the summary block is untouched.
    """
    text = str(results.summary())
    text = re.sub(r"(Date:\s+)\w{3}, \d{2} \w{3} \d{4}",
                  lambda m: m.group(1) + "(run date omitted)", text)
    text = re.sub(r"(Time:\s+)\d{2}:\d{2}:\d{2}",
                  lambda m: m.group(1) + "(omitted)", text)
    return text

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

# Task 5.6 / PRD §9 Q2: the neighbourhood-fixed-effects variant. Identical
# to FORMULA except `neighbourhood_group` (3 levels) is replaced by
# `neighbourhood` (264 levels) — the two are nested, so they are never in
# the model together. Reference level = Venice, the largest neighbourhood
# (1,700 listings), so each dummy reads as "vs. Venice" against a
# well-estimated baseline. Patsy's alphabetical default would instead
# anchor on a tiny neighbourhood, inflating every dummy's standard error.
FE_REFERENCE_NEIGHBOURHOOD = "Venice"
FORMULA_FE = (
    'log_price ~ '
    'C(room_type, Treatment(reference="Entire home/apt")) '
    '+ minimum_nights '
    '+ availability_365 '
    '+ calculated_host_listings_count '
    '+ number_of_reviews '
    f'+ C(neighbourhood, Treatment(reference="{FE_REFERENCE_NEIGHBOURHOOD}"))'
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

# The FE frame swaps the group column for the 264-level neighbourhood.
MODEL_COLUMNS_FE = MODEL_COLUMNS[:-1] + ["neighbourhood"]


def build_model_frame(df: pd.DataFrame, fixed_effects: bool = False) -> pd.DataFrame:
    """
    PRD req 43 + 48: the listing-level frame the hedonic model is fit on —
    every cleaned listing, the columns the formula references, no
    aggregation and no neighbourhood exclusion.

    `fixed_effects=False` builds the req-43 frame (7 cols, uses
    `neighbourhood_group`). `fixed_effects=True` builds the task-5.6
    comparison frame, swapping in the 264-level `neighbourhood` column.

    Raises if `log_price` is missing (ingest.clean must run first) or if
    any model column contains a null. None of the columns has nulls in the
    cleaned data: `number_of_reviews` is 0 rather than null for unreviewed
    listings, and `reviews_per_month` — the only review field with nulls —
    is deliberately not in the model.
    """
    columns = MODEL_COLUMNS_FE if fixed_effects else MODEL_COLUMNS
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(
            f"model frame is missing column(s) {missing}; "
            "run ingest.clean to add log_price before building the frame"
        )

    frame = df[columns].copy()

    nulls = frame.isna().sum()
    if nulls.any():
        raise ValueError(
            f"model columns contain nulls: {nulls[nulls > 0].to_dict()}. "
            "The hedonic model expects a complete case for every listing."
        )

    kind = "neighbourhood fixed effects" if fixed_effects else "no exclusion"
    print(f"[regression] model frame {frame.shape[0]} listings x "
          f"{frame.shape[1]} columns ({kind})")
    return frame


def fit_model(frame: pd.DataFrame, formula: str = FORMULA):
    """
    PRD req 44: OLS fit with heteroskedasticity-robust (HC3) standard
    errors. Price data is strongly heteroskedastic even after the log
    transform — variance rises with room type and location — so the
    classical SEs would understate uncertainty on several coefficients.

    HC3 is applied at fit time, so `.bse`, `.tvalues`, `.pvalues`, and
    `.conf_int()` on the returned results are already the robust versions;
    the point estimates and R^2 are identical to a classical fit.

    `formula` defaults to the req-43 form; pass `FORMULA_FE` for the
    task-5.6 fixed-effects variant.

    Returns the fitted `RegressionResultsWrapper` (used by 5.3-5.6).
    """
    results = smf.ols(formula, data=frame).fit(cov_type="HC3")
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
        "Success metric 3 (R^2 >= 0.35): NOT MET. R^2 = 0.330 on the req-43",
        "feature set. The 264-dummy fixed-effects variant clears the bar",
        "(R^2 = 0.481) but is inadmissible under HC3 - see NEIGHBOURHOOD",
        "FIXED EFFECTS below. The req-43 formula is fixed, so the miss is",
        "accepted and recorded (task 5.6 decision).",
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
        + _deterministic_summary(results)
        + "\n"
        + _format_percentage_effects(percentage_effects(results))
    )
    path.write_text(text, encoding="utf-8")
    print(f"[regression] summary -> {path} "
          f"(R^2={results.rsquared:.3f}, n={int(results.nobs)})")
    return text


_FE_PREFIX = (
    f'C(neighbourhood, Treatment(reference="{FE_REFERENCE_NEIGHBOURHOOD}"))[T.'
)


def _fe_neighbourhood(param_name: str) -> str:
    """Strip the patsy wrapper: '...[T.Adams-Normandie]' -> 'Adams-Normandie'."""
    return param_name[len(_FE_PREFIX):-1]


def compare_neighbourhood_fixed_effects(df: pd.DataFrame, path=None) -> dict:
    """
    Task 5.6 / PRD §9 open question 2: does the hedonic model want 264
    neighbourhood dummies on top of the 3-level `neighbourhood_group`?

    Fits both — the req-43 model (`FORMULA`, HC3) and the fixed-effects
    variant (`FORMULA_FE`, `neighbourhood_group` swapped for the 264-level
    `neighbourhood`) — and compares R^2, adjusted R^2 (which charges for
    the 261 extra parameters), AIC and BIC.

    It also checks whether the FE model can even carry the req-44 error
    type: HC3 divides by (1 - leverage)^2, and a neighbourhood with a
    single listing gives that row leverage 1 once its dummy is in the
    design. Those rows make every HC3 standard error in the FE fit
    infinite — the model is not estimable under the mandated covariance.
    That is PRD open question 2's over-parameterisation concern made
    concrete rather than hypothetical.

    Appends a NEIGHBOURHOOD FIXED EFFECTS section to
    `outputs/regression_summary.txt` (run it after `write_summary`, which
    truncates the file) and returns the comparison as a dict.
    """
    path = path or (config.OUTPUT_DIR / "regression_summary.txt")

    base = fit_model(build_model_frame(df, fixed_effects=False), formula=FORMULA)

    # FE point estimates / R^2 / AIC come from a plain OLS fit; they do not
    # depend on the covariance choice. A second fit then tries HC3.
    fe_frame = build_model_frame(df, fixed_effects=True)
    fe = smf.ols(FORMULA_FE, data=fe_frame).fit()
    fe_hc3 = smf.ols(FORMULA_FE, data=fe_frame).fit(cov_type="HC3")
    hc3_ok = bool(np.isfinite(fe_hc3.bse).all())

    counts = df["neighbourhood"].value_counts()
    singletons = sorted(counts[counts == 1].index)
    n_below_10 = int((counts < 10).sum())

    dummies = [n for n in fe.params.index if n.startswith(_FE_PREFIX)]
    delta_adj = float(fe.rsquared_adj - base.rsquared_adj)

    # base is the req-43 model and stays primary: the FE spec cannot carry
    # HC3 errors (req 44), so it cannot be the reported model even though
    # it fits better. It is kept as a robustness note.
    fe_is_primary = hc3_ok and fe.rsquared >= 0.35 and delta_adj > 0

    result = {
        "base_r2": float(base.rsquared),
        "base_adj_r2": float(base.rsquared_adj),
        "base_params": int(base.df_model) + 1,
        "fe_r2": float(fe.rsquared),
        "fe_adj_r2": float(fe.rsquared_adj),
        "fe_params": int(fe.df_model) + 1,
        "delta_adj_r2": delta_adj,
        "n_dummies": len(dummies),
        "n_singleton_neighbourhoods": len(singletons),
        "n_neighbourhoods_below_10": n_below_10,
        "fe_hc3_estimable": hc3_ok,
        "fe_is_primary": bool(fe_is_primary),
    }

    if fe_is_primary:
        decision = (
            "Neighbourhood fixed effects are the PRIMARY reported model."
        )
    else:
        decision = "\n".join(textwrap.wrap(
            "The req-43 model (neighbourhood_group, HC3) stays the PRIMARY "
            "reported model. The 264-dummy fixed-effects variant fits better "
            f"(R^2 {base.rsquared:.3f} -> {fe.rsquared:.3f}, adjusted "
            f"{base.rsquared_adj:.3f} -> {fe.rsquared_adj:.3f}), which says "
            "neighbourhood location carries real price signal beyond the "
            "three groups. But it cannot be the reported model: "
            f"{len(singletons)} neighbourhoods have a single listing, giving "
            "those rows leverage 1 once their dummy enters the design, which "
            "makes every HC3 standard error in the fit infinite. Requirement "
            "44 mandates HC3, so the FE spec is inadmissible here. This is "
            "PRD open question 2's over-parameterisation concern, concrete: "
            "the small neighbourhoods that the n>=100 rule already excludes "
            "from aggregation also break the listing-level model. The FE "
            "result is retained below as a robustness note only.",
            width=78,
        ))

    lines = [
        "",
        "",
        "=" * 78,
        "NEIGHBOURHOOD FIXED EFFECTS  (task 5.6 / PRD open question 2)",
        "=" * 78,
        "",
        "Same listing-level model, two neighbourhood controls:",
        "  base : + C(neighbourhood_group)   (3 levels,  HC3)",
        "  FE   : + C(neighbourhood)          (264 levels, 263 dummies)",
        "",
        "                         base            FE",
        f"  n                {int(base.nobs):>10d}    {int(fe.nobs):>10d}",
        f"  parameters       {result['base_params']:>10d}    {result['fe_params']:>10d}",
        f"  R^2              {base.rsquared:>10.3f}    {fe.rsquared:>10.3f}",
        f"  adjusted R^2     {base.rsquared_adj:>10.3f}    {fe.rsquared_adj:>10.3f}",
        f"  AIC              {base.aic:>10.0f}    {fe.aic:>10.0f}",
        f"  BIC              {base.bic:>10.0f}    {fe.bic:>10.0f}",
        "",
        f"  adjusted R^2 change with FE: {delta_adj:+.3f}",
        f"  R^2 >= 0.35 (success metric 3): "
        f"base {'meets' if base.rsquared >= 0.35 else 'misses'}, "
        f"FE {'meets' if fe.rsquared >= 0.35 else 'misses'}",
        "",
        "FE feasibility under HC3 (requirement 44):",
        f"  neighbourhoods with 1 listing : {len(singletons)}  "
        f"({', '.join(singletons)})",
        f"  neighbourhoods with < 10      : {n_below_10}",
        f"  all HC3 standard errors finite: {hc3_ok}",
        "  A single-listing neighbourhood's dummy fits that row exactly,",
        "  so leverage = 1 and HC3's 1/(1-h)^2 weight is undefined. Every",
        "  HC3 SE in the FE fit is therefore infinite.",
        "",
        "DECISION",
        "-" * 78,
        decision,
        "",
    ]
    with path.open("a", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print(f"[regression] fixed-effects comparison appended -> {path} "
          f"(FE R^2 {fe.rsquared:.3f}, HC3 estimable={hc3_ok}, "
          f"primary={'FE' if fe_is_primary else 'base'})")
    return result

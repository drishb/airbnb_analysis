"""
All matplotlib output. PRD requirements 16, 22, 46, 57-60.

Every figure this project emits goes through `save()` here, so all ten
share one look: viridis for continuous indicators, a categorical map for
clusters, 150 dpi PNG, and the fixed caption from `config.FIGURE_CAPTION`
noting the ~August 2020 snapshot and the pandemic caveat (req 61, PRD §6).

The module forces the non-interactive "Agg" backend on import so the
pipeline renders with no display and no network (req 64).

This file grows through the project:
  5.5  residual_diagnostics  - hedonic-model diagnostic plots (req 46)
  7.x  bubble maps, hexbin, histograms, revenue scatter, elbow/silhouette
"""

import textwrap

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import statsmodels.api as sm  # noqa: E402

from . import config  # noqa: E402

# Applied once, so font sizes and the default image colourmap are the same
# on every figure regardless of the caller.
plt.rcParams.update(
    {
        "figure.dpi": config.FIGURE_DPI,
        "savefig.dpi": config.FIGURE_DPI,
        "image.cmap": config.FIGURE_CMAP,
        "axes.titlesize": 11,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "figure.autolayout": False,
    }
)

_CAPTION_WIDTH = 110  # characters per wrapped caption line


def save(fig, name: str, caption: str | None = None, dpi: int | None = None):
    """
    Attach the standard caption, write `outputs/figures/<name>` as PNG at
    >=150 dpi (req 60), close the figure, and return the path.

    `caption` overrides `config.FIGURE_CAPTION` only when a figure needs an
    extra note (e.g. the inactivity charts, req 36) - the base caveat text
    is always included by the caller passing `config.FIGURE_CAPTION + ...`.
    """
    text = caption or config.FIGURE_CAPTION
    wrapped = "\n".join(textwrap.wrap(text, width=_CAPTION_WIDTH))

    # Reserve space under the axes so the caption never overlaps the plot;
    # bbox_inches="tight" then trims the surrounding whitespace back.
    fig.subplots_adjust(bottom=0.22)
    fig.text(
        0.5,
        0.015,
        wrapped,
        ha="center",
        va="bottom",
        fontsize=7,
        style="italic",
        color="0.4",
    )

    config.FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    path = config.FIGURE_DIR / name
    fig.savefig(path, dpi=dpi or config.FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"[figures] {name} -> {path}")
    return path


def residual_diagnostics(results, name: str = "residual_diagnostics.png"):
    """
    PRD req 46: residual diagnostics for the hedonic model (task 5.5) -
    residuals vs. fitted on the left, a normal Q-Q plot on the right.

    Residuals-vs-fitted shows whether the log transform left any curvature
    or funnelling in the errors; the Q-Q plot shows how heavy the tails
    are. The fit's own `summary()` already reports Omnibus / Jarque-Bera
    (skew 1.22, kurtosis 5.23) - these plots make that visible.

    `results` is the fitted `RegressionResultsWrapper` from
    `regression.fit_model`. The HC3 covariance does not change residuals
    or fitted values, so the plots are unaffected by it.
    """
    fitted = results.fittedvalues
    resid = results.resid

    fig, (ax_rf, ax_qq) = plt.subplots(1, 2, figsize=(11, 4.5))

    ax_rf.scatter(fitted, resid, s=4, alpha=0.12, color="#3b528b",
                  edgecolors="none", rasterized=True)
    ax_rf.axhline(0.0, color="black", lw=1)
    ax_rf.set_xlabel("Fitted log-price")
    ax_rf.set_ylabel("Residual (log-price)")
    ax_rf.set_title("Residuals vs. fitted")

    # sm.qqplot draws the reference line via OLS on the ordered quantiles
    # (line="s"); markers kept small and translucent for 33k points.
    sm.qqplot(resid, line="s", ax=ax_qq, markersize=2, alpha=0.3,
              markerfacecolor="#3b528b", markeredgecolor="none")
    ax_qq.get_lines()[1].set_color("black")
    ax_qq.set_title("Normal Q-Q of residuals")

    fig.suptitle("Hedonic log-price regression - residual diagnostics",
                 fontsize=12)
    return save(fig, name)


def plot_k_selection(diag, selected_k: int, name: str = "elbow_silhouette.png"):
    """
    PRD req 51: the elbow (inertia) and silhouette curves over k, on one
    figure with a twin y-axis, the selected k marked.

    `diag` is `clustering.k_diagnostics` output - a frame indexed by k with
    `inertia` and `silhouette` columns.
    """
    k = diag.index.to_numpy()

    fig, ax_inertia = plt.subplots(figsize=(8, 5))
    ax_sil = ax_inertia.twinx()

    line_i, = ax_inertia.plot(k, diag["inertia"], "o-", color="#3b528b",
                              label="inertia (elbow)")
    line_s, = ax_sil.plot(k, diag["silhouette"], "s--", color="#5ec962",
                          label="mean silhouette")

    ax_inertia.axvline(selected_k, color="0.4", lw=1, ls=":")
    ax_inertia.set_xlabel("k (number of clusters)")
    ax_inertia.set_ylabel("K-means inertia")
    ax_sil.set_ylabel("mean silhouette score")
    ax_inertia.set_xticks(k)
    ax_inertia.set_title(f"Cluster count selection - k = {selected_k} chosen")

    ax_inertia.legend(handles=[line_i, line_s], loc="upper right")
    ax_inertia.annotate(
        f"selected k = {selected_k}",
        xy=(selected_k, diag.loc[selected_k, "inertia"]),
        xytext=(8, 12), textcoords="offset points", fontsize=8, color="0.3",
    )
    return save(fig, name)

"""
All matplotlib output. PRD requirements 16, 22, 46, 57-60.

Every figure this project emits goes through `save()` here, so all ten
share one look: viridis for continuous indicators, a categorical map for
clusters, 150 dpi PNG, and the fixed caption from `config.FIGURE_CAPTION`
noting the ~August 2020 snapshot and the pandemic caveat (req 61, PRD §6).

The module forces the non-interactive "Agg" backend on import so the
pipeline renders with no display and no network (req 64).

This file grows through the project:
  5.5  residual_diagnostics       - hedonic-model diagnostic plots (req 46)
  6.3  plot_k_selection           - elbow + silhouette over k (req 51)
  7.2  centroid_bubble_map        - one marker per retained neighbourhood (req 57)
  7.4  hexbin_density             - listing density over raw lat/long (req 58)
  7.5  min_nights_histogram       - minimum_nights capped at 90 (req 16)
  7.6  revenue_capped_vs_uncapped - per-neighbourhood revenue scatter (req 22)
"""

import textwrap

import numpy as np
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


# --- geospatial output (task 7.2-7.6) ---------------------------------
#
# Two honest map forms only (PRD §7.2): centroid bubbles, which say "these
# listings share a label and sit roughly here", and a hexbin over raw
# coordinates, which discards the labels. No choropleth (no boundary
# geometry in the CSV) and explicitly no Voronoi (req 59 - synthesised
# polygons imply spatial extent the data does not contain).

def _extent(lon, lat, margin=0.04):
    """Bounding box of the points, padded, so every marker is on-frame -
    including Avalon on Catalina, ~35 km off the mainland (req 57 wants one
    marker per retained neighbourhood, so none may fall outside the axes)."""
    lon, lat = np.asarray(lon, dtype=float), np.asarray(lat, dtype=float)
    dx = (lon.max() - lon.min()) * margin or 0.05
    dy = (lat.max() - lat.min()) * margin or 0.05
    return (lon.min() - dx, lon.max() + dx), (lat.min() - dy, lat.max() + dy)


def _basemap(ax, xlim, ylim):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_xlabel("longitude")
    ax.set_ylabel("latitude")
    ax.set_aspect(1.0 / np.cos(np.deg2rad(np.mean(ylim))))
    ax.grid(True, color="0.9", lw=0.5)


def centroid_bubble_map(retained, values, *, title, legend_label, name,
                        categorical=False, category_labels=None):
    """
    PRD req 57: one marker per retained neighbourhood at its mean lat/long
    (`centroid_lat` / `centroid_lon`), sized by `listing_count`, coloured by
    the indicator.

    `retained` is the exclusion-filtered neighbourhood table (it carries
    `centroid_lat`, `centroid_lon`, `listing_count`). `values` is a Series
    of the indicator to colour by, aligned to `retained.index`; rows missing
    from it are dropped from the map.

    `categorical=True` switches to the discrete cluster colourmap
    (`config.FIGURE_CMAP_CATEGORICAL`) and draws a labelled legend instead
    of a colour bar; pass `category_labels={id: text}` for the legend.
    """
    v = values.reindex(retained.index).dropna()
    sub = retained.loc[v.index]
    lon = sub["centroid_lon"].to_numpy()
    lat = sub["centroid_lat"].to_numpy()
    counts = sub["listing_count"].to_numpy(dtype=float)
    # marker area 20-400 pt^2, sqrt so area (not radius) tracks listing count
    sizes = 20 + 380 * np.sqrt(
        (counts - counts.min()) / max(counts.max() - counts.min(), 1)
    )

    fig, ax = plt.subplots(figsize=(9, 7))
    xlim, ylim = _extent(lon, lat)
    _basemap(ax, xlim, ylim)

    # The geographic aspect makes the axes tall and narrow and Avalon plots
    # at the very bottom, so the indicator legend goes BELOW the axes and
    # only the small size key sits in the (empty) upper-right corner.
    if categorical:
        cats = np.asarray(v, dtype=int)
        cmap = plt.get_cmap(config.FIGURE_CMAP_CATEGORICAL)
        cat_handles = []
        for c in sorted(np.unique(cats)):
            m = cats == c
            lbl = (category_labels or {}).get(int(c), f"cluster {c}")
            h = ax.scatter(lon[m], lat[m], s=sizes[m], color=cmap(int(c) % 10),
                           alpha=0.8, edgecolors="white", linewidths=0.5,
                           label=f"{c} - {lbl}")
            cat_handles.append(h)
        ax.add_artist(ax.legend(
            handles=cat_handles, title=legend_label, fontsize=7,
            title_fontsize=8, loc="upper left", framealpha=0.92))
    else:
        cvals = np.asarray(v, dtype=float)
        # Clip the colour scale to the 2nd/98th percentile so a single
        # extreme neighbourhood (Avalon's host HHI, say) does not flatten
        # every other marker to one colour. The colour bar carries extend
        # arrows to show values run past the ends.
        lo, hi = np.percentile(cvals, [2, 98])
        extend = "both" if (cvals.min() < lo or cvals.max() > hi) else "neither"
        sc = ax.scatter(lon, lat, s=sizes, c=cvals, cmap=config.FIGURE_CMAP,
                        alpha=0.85, edgecolors="white", linewidths=0.5,
                        vmin=lo, vmax=hi)
        fig.colorbar(sc, ax=ax, label=legend_label, shrink=0.85, pad=0.02,
                     extend=extend)

    # listing-count size key (three reference bubbles), upper-right corner
    span = max(counts.max() - counts.min(), 1)
    size_handles = [
        ax.scatter([], [], s=20 + 380 * np.sqrt((q - counts.min()) / span),
                   color="0.6", edgecolors="white", label=f"{int(q)} listings")
        for q in (counts.min(), np.median(counts), counts.max())
    ]
    ax.legend(handles=size_handles, fontsize=7, loc="lower right",
              framealpha=0.9, title="marker size (listing count)",
              title_fontsize=8)

    ax.set_title(title)
    return save(fig, name)


def hexbin_density(df, name: str = "hexbin_listing_density.png"):
    """
    PRD req 58: hexbin count of listings over raw latitude/longitude,
    independent of neighbourhood labels - it recovers the spatial detail the
    missing boundary polygons would have carried (PRD §7.2). `df` is the
    cleaned listing frame.
    """
    fig, ax = plt.subplots(figsize=(9, 6))
    xlim, ylim = _extent(df["longitude"], df["latitude"])
    hb = ax.hexbin(df["longitude"], df["latitude"], gridsize=60,
                   extent=(*xlim, *ylim), cmap=config.FIGURE_CMAP,
                   bins="log", mincnt=1)
    _basemap(ax, xlim, ylim)
    fig.colorbar(hb, ax=ax, label="listings per cell (log scale)", shrink=0.85)
    ax.set_title("Listing density over raw coordinates "
                 f"(n = {len(df):,}, no neighbourhood labels)")
    return save(fig, name)


def min_nights_histogram(df, name: str = "hist_minimum_nights.png"):
    """
    PRD req 16: histogram of `minimum_nights` capped at 90, annotated at the
    non-organic spike at exactly 30 - a 30-night minimum exempts a listing
    from LA's 2019 Home-Sharing Ordinance, so the spike is the
    regulatory-evasion signal, not an organic distribution. `df` is the
    cleaned listing frame.
    """
    capped = df["minimum_nights"].clip(upper=90)
    over_90 = int((df["minimum_nights"] > 90).sum())
    at_30 = int((df["minimum_nights"] == 30).sum())

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(capped, bins=range(0, 92), color="#3b528b", edgecolor="white",
            linewidth=0.3)
    ax.axvline(30, color="#d1495b", lw=1.2, ls="--")
    ax.annotate(
        f"spike at exactly 30 nights: {at_30:,} listings "
        f"({100 * at_30 / len(df):.1f}%)\n"
        "— the Home-Sharing Ordinance exemption threshold",
        xy=(30, at_30), xytext=(40, at_30 * 0.85),
        fontsize=8, color="0.2",
        arrowprops=dict(arrowstyle="->", color="0.4", lw=0.8),
    )
    ax.set_xlabel("minimum_nights (capped at 90)")
    ax.set_ylabel("listings")
    ax.set_title("Minimum-nights distribution — regulatory-evasion signal "
                 f"({over_90:,} listings above 90 not shown)")
    return save(fig, name)


def revenue_capped_vs_uncapped(
    retained, name: str = "scatter_revenue_capped_vs_uncapped.png"
):
    """
    PRD req 22: per-neighbourhood scatter of capped vs. uncapped estimated
    annual revenue, so the divergence introduced by the ~32% of listings at
    30+ nights is visible rather than assumed away. `retained` is the
    exclusion-filtered neighbourhood table.
    """
    x = retained["rev_capped_median"].to_numpy(dtype=float)
    y = retained["rev_uncapped_median"].to_numpy(dtype=float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]

    fig, ax = plt.subplots(figsize=(7, 6.5))
    lim = max(x.max(), y.max()) * 1.05
    ax.plot([0, lim], [0, lim], color="0.6", lw=1, ls="--",
            label="capped = uncapped")
    ax.scatter(x, y, s=28, color="#3b528b", alpha=0.75, edgecolors="white",
               linewidths=0.4)
    ax.set_xlim(0, lim)
    ax.set_ylim(0, lim)
    ax.set_xlabel("capped-variant median revenue ($/yr, min_nights capped at 5)")
    ax.set_ylabel("uncapped-variant median revenue ($/yr)")
    ax.set_title("Estimated revenue: capped vs. uncapped, per retained "
                 f"neighbourhood (n = {ok.sum()})")
    ax.legend(fontsize=8, loc="upper left")
    return save(fig, name)

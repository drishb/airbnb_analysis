"""
Single entry point. PRD req 65: the whole pipeline runs from
`python run_analysis.py` on the raw CSV, no manual steps.

Stage order is dependency order (req 65):

    ingest -> text topics -> neighbourhood table -> CSV export
           -> hedonic regression (+ diagnostics)
           -> clustering (+ k-selection plot)
           -> threshold sensitivity -> exclusion report
           -> maps and charts
           -> limitations.md

Every artefact lands in `outputs/` (req 66; `outputs-<dataset>/` for
non-default datasets, see `--dataset`). All randomness is seeded in
`set_seeds` plus the fixed `random_state` on every sklearn estimator
(req 69), so repeated runs of the same dataset produce byte-identical CSV
output.

`--dataset` selects which of `config.DATASETS` to run (default `la`,
preserving the original single-dataset behaviour). It must be applied
before any other project module runs, since every module reads
dataset-specific values as plain `config.X` attributes.
"""
import argparse
import random

import numpy as np

from src import config


def set_seeds():
    """PRD req 69: global seeds so repeated runs are identical. The sklearn
    estimators (KMeans, PCA, NMF) additionally pin `random_state` to
    `config.RANDOM_SEED` at construction — see the individual modules."""
    random.seed(config.RANDOM_SEED)
    np.random.seed(config.RANDOM_SEED)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset", choices=sorted(config.DATASETS), default="la",
        help="which Inside Airbnb snapshot to run (default: la)",
    )
    args = parser.parse_args()
    config.select_dataset(args.dataset)

    # Imported after select_dataset so nothing reads a stale default - none
    # of these modules touch dataset-specific config at import time today,
    # but keeping the import here removes that as a future footgun.
    from src import (
        aggregate, clustering, figures, indicators_text, ingest, regression,
        report,
    )

    set_seeds()
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    config.FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    # --- ingestion (req 1-6) -----------------------------------------
    df = ingest.run()

    # --- text-derived indicators (req 28-34) ------------------------
    loadings = indicators_text.write_report(df)

    # --- neighbourhood table + CSV export (req 37-42) ---------------
    tbl = aggregate.build_table(df, loadings=loadings)
    aggregate.export_table(tbl)

    # --- hedonic price regression (req 43-48) ----------------------
    frame = regression.build_model_frame(df)
    formula = regression.build_formula(df)
    results = regression.fit_model(frame, formula)
    regression.write_summary(results, formula)                # truncates the file
    regression.compare_neighbourhood_fixed_effects(df)       # appends (order matters)
    figures.residual_diagnostics(results)                    # req 46

    # --- clustering (req 49-56) -----------------------------------
    feats = aggregate.feature_frame(tbl)
    standardized = clustering.standardize(feats)
    weighted = clustering.family_weight(standardized)
    diag = clustering.k_diagnostics(weighted)
    figures.plot_k_selection(diag, config.CLUSTER_K)         # req 51
    _, labels = clustering.fit_kmeans(weighted)
    pca_result = clustering.pca_clustering(standardized, labels)
    centroids = clustering.centroid_table(feats, labels, tbl)
    cluster_labels = clustering.label_clusters(centroids)
    clustering.write_summary(centroids, cluster_labels, labels, diag, pca_result)

    # --- threshold sensitivity + exclusion report (req 40-41) -----
    sensitivity = clustering.threshold_sensitivity(tbl)
    aggregate.write_exclusion_report(tbl, sensitivity=sensitivity)

    # --- maps and charts (req 16, 22, 57-60) ---------------------
    retained = aggregate.exclude_low_confidence(tbl)
    figures.centroid_bubble_map(
        retained, retained["price_median"],
        title="Median nightly price by neighbourhood",
        legend_label="median price ($)", name="map_median_price.png")
    figures.centroid_bubble_map(
        retained, retained["host_hhi"],
        title="Host concentration (Herfindahl-Hirschman index)",
        legend_label="host HHI", name="map_host_hhi.png")
    figures.centroid_bubble_map(
        retained, retained["tour_reviews_per_month_mean"],
        title="Tourism intensity (mean reviews per month)",
        legend_label="mean reviews / month", name="map_tourism_intensity.png")
    figures.centroid_bubble_map(
        retained, retained["reg_min30_share"],
        title="Share of listings with a 30-night minimum stay",
        legend_label="30-night-minimum share", name="map_min_nights_30.png")
    figures.centroid_bubble_map(
        retained, labels,
        title=f"Neighbourhood clusters (family-weighted K-means, k={config.CLUSTER_K})",
        legend_label="cluster", name="map_clusters.png",
        categorical=True, category_labels=cluster_labels)

    figures.hexbin_density(df)                               # req 58
    figures.min_nights_histogram(df)                         # req 16
    figures.revenue_capped_vs_uncapped(retained)             # req 22

    # --- limitations + success-metric check (req 67, task 8.8) ---
    report.write_limitations(df, tbl, results, diag, pca_result, sensitivity)
    report.write_success_metrics(
        tbl, results, diag, pca_result, cluster_labels, sensitivity)

    print("[run] pipeline complete — all artefacts in", config.OUTPUT_DIR)
    return df


if __name__ == "__main__":
    main()

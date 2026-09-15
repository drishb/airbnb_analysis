"""
Neighbourhood clustering. PRD requirements 49-56.

Segments the retained neighbourhoods (n >= 100 listings) into interpretable
market types with family-weighted K-means, labels assigned post-hoc from
centroid inspection.

Pipeline, one function per task 6.x sub-task:
  6.1  standardize          - z-score every feature (req 49)
  6.2  family_weight        - divide by sqrt(family size) (req 50, PRD §7.1)
  6.3  select_k             - elbow + silhouette over k = 2..10 (req 51)
  6.4  fit_kmeans           - K-means at the fixed seed (req 52)
  6.5  pca_clustering       - PCA robustness check, ARI vs weighted (req 53)
  6.6  centroid_table       - centroids in original units (req 54)
  6.7  label_clusters       - post-hoc labels from centroid profiles (req 55)
  6.8  write_summary        - member neighbourhoods per cluster (req 56)

Every step is deterministic given `config.RANDOM_SEED`.
"""

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler

from . import aggregate, config, figures


def standardize(frame: pd.DataFrame) -> pd.DataFrame:
    """
    PRD req 49: put every clustering feature on a zero-mean, unit-variance
    scale before any distance is computed.

    The raw features span five orders of magnitude - revenue medians in the
    thousands, share indicators in [0, 1] - so unstandardised Euclidean
    distance would be almost entirely revenue and price. Z-scoring makes a
    one-standard-deviation move worth the same in every feature; task 6.2
    then corrects for how many features each family contributes.

    `StandardScaler` uses the population standard deviation (ddof = 0).
    Returns a DataFrame with the original index and columns.
    """
    scaler = StandardScaler()
    z = scaler.fit_transform(frame)
    out = pd.DataFrame(z, index=frame.index, columns=frame.columns)

    # Cheap invariant: every column now ~N(0, 1).
    means = out.mean().abs()
    stds = out.std(ddof=0)
    if (means > 1e-9).any() or ((stds - 1.0).abs() > 1e-9).any():
        raise ValueError("standardisation did not produce zero-mean/unit-variance columns")

    print(f"[clustering] standardised {out.shape[0]} neighbourhoods x "
          f"{out.shape[1]} features (zero mean, unit variance)")
    return out


def _feature_family_size() -> dict[str, int]:
    """Feature name -> number of features in that feature's indicator family."""
    return {
        feat: len(cols)
        for cols in config.INDICATOR_FAMILIES.values()
        for feat in cols
    }


def family_weight(frame: pd.DataFrame) -> pd.DataFrame:
    """
    PRD req 50 / §7.1: divide each standardised feature by the square root
    of the number of features in its indicator family.

    Why: the families are unequal in size - tourism has 9 features, tenure
    has 1. In plain standardised space K-means would give tourism nine
    times the pull on the segmentation purely because nine columns were
    written for it. Scaling a family of size m by 1/sqrt(m) makes that
    family's summed contribution to squared Euclidean distance equal to 1,
    the same as every other family, while leaving the individual features
    intact and readable (unlike PCA - see §7.1).

    Input must be the output of `standardize` (unit-variance columns), so
    the post-condition below holds: each family's total feature variance
    is 1.0 after weighting.
    """
    sizes = _feature_family_size()
    unknown = [c for c in frame.columns if c not in sizes]
    if unknown:
        raise ValueError(
            f"features with no indicator family in config: {unknown}"
        )

    divisors = pd.Series(
        {c: np.sqrt(sizes[c]) for c in frame.columns}, dtype=float
    )
    out = frame.divide(divisors, axis=1)

    # Post-condition: every family now contributes the same total variance
    # (1.0) to the distance metric. This is the property task 6.9 tests.
    per_family = {
        name: float(out[cols].var(ddof=0).sum())
        for name, cols in config.INDICATOR_FAMILIES.items()
    }
    if any(abs(v - 1.0) > 1e-9 for v in per_family.values()):
        raise ValueError(
            f"family weighting did not equalise family variance: {per_family}"
        )

    print(f"[clustering] family-weighted {out.shape[1]} features across "
          f"{len(config.INDICATOR_FAMILIES)} families "
          f"(each family contributes variance 1.0)")
    return out


def _kmeans(k: int) -> KMeans:
    """K-means at the fixed seed (req 52). One constructor, used everywhere
    so every fit in this module is identical and reproducible."""
    return KMeans(
        n_clusters=k,
        random_state=config.RANDOM_SEED,
        n_init=config.KMEANS_N_INIT,
    )


def k_diagnostics(weighted: pd.DataFrame) -> pd.DataFrame:
    """
    PRD req 51: sweep k over `config.CLUSTER_K_RANGE` (2..10) and record,
    for each, the K-means inertia (the elbow criterion) and the mean
    silhouette score. The plot is `figures.plot_k_selection`; the chosen k
    (`config.CLUSTER_K`) and its justification are written into
    `cluster_summary.md` by `write_summary` (task 6.8).

    `weighted` is the family-weighted feature matrix. Returns a frame
    indexed by k with columns `inertia` and `silhouette`.

    k is clamped to at most `len(weighted) - 1` - K-means requires
    n_clusters <= n_samples, and a thin dataset (e.g. Antwerp's 7 retained
    neighbourhoods) can fall well short of `config.CLUSTER_K_RANGE`'s
    default ceiling of 10.
    """
    X = weighted.values
    k_range = [k for k in config.CLUSTER_K_RANGE if k <= len(weighted) - 1]
    if not k_range:
        raise ValueError(
            f"only {len(weighted)} retained neighbourhoods - too few to "
            f"sweep any k in {config.CLUSTER_K_RANGE}"
        )
    rows = {}
    for k in k_range:
        labels = _kmeans(k).fit(X)
        rows[k] = {
            "inertia": float(labels.inertia_),
            "silhouette": float(silhouette_score(X, labels.labels_)),
        }
    diag = pd.DataFrame.from_dict(rows, orient="index")
    diag.index.name = "k"

    best = diag["silhouette"].idxmax()
    print(f"[clustering] k sweep {k_range[0]}.."
          f"{k_range[-1]}: best silhouette {diag.loc[best, 'silhouette']:.3f} "
          f"at k={best}; selected k={config.CLUSTER_K}")
    return diag


def fit_kmeans(weighted: pd.DataFrame, k: int | None = None):
    """
    PRD req 52: fit K-means on the family-weighted features at the fixed
    seed. `k` defaults to `config.CLUSTER_K` (5, task 6.3). Uses the same
    `_kmeans` constructor as the k sweep, so the fit is identical to the
    one `k_diagnostics` scored.

    Returns `(model, labels)` where `labels` is an integer `Series` indexed
    by neighbourhood. Cluster ids are arbitrary at this point - task 6.7
    assigns names from the centroid profiles.
    """
    k = config.CLUSTER_K if k is None else k
    model = _kmeans(k).fit(weighted.values)
    labels = pd.Series(model.labels_, index=weighted.index, name="cluster")

    sil = silhouette_score(weighted.values, model.labels_)
    sizes = labels.value_counts().sort_index().to_dict()
    print(f"[clustering] K-means k={k} fit: silhouette {sil:.3f}, "
          f"cluster sizes {sizes}")
    return model, labels


def pca_clustering(standardized: pd.DataFrame, weighted_labels: pd.Series,
                   k: int | None = None) -> dict:
    """
    PRD req 53: the PCA robustness check. Run K-means on principal
    components retaining >= `config.PCA_VARIANCE_RETAINED` (85%) of the
    variance, at the same k, and report the adjusted Rand index against the
    family-weighted solution from `fit_kmeans`.

    PCA is the alternative to family weighting (PRD §7.1): it removes the
    redundancy between correlated indicators but at the cost of
    interpretable axes, which is why it is only a cross-check here. Input is
    the *standardised, unweighted* matrix - applying PCA to the weighted
    one would fold the family correction in twice. A high ARI means the
    segmentation is not an artefact of the weighting choice.

    Returns a dict: `n_components`, `variance_explained`, `ari`,
    `pca_labels` (Series), `pca_silhouette`.
    """
    k = config.CLUSTER_K if k is None else k

    pca = PCA(n_components=config.PCA_VARIANCE_RETAINED,
              random_state=config.RANDOM_SEED)
    scores = pca.fit_transform(standardized.values)

    model = _kmeans(k).fit(scores)
    pca_labels = pd.Series(model.labels_, index=standardized.index,
                           name="pca_cluster")

    # align on neighbourhood in case the two came from different frames
    common = weighted_labels.index.intersection(pca_labels.index)
    ari = float(adjusted_rand_score(
        weighted_labels.loc[common], pca_labels.loc[common]
    ))
    result = {
        "n_components": int(pca.n_components_),
        "variance_explained": float(pca.explained_variance_ratio_.sum()),
        "ari": ari,
        "pca_labels": pca_labels,
        "pca_silhouette": float(silhouette_score(scores, model.labels_)),
    }
    print(f"[clustering] PCA check: {result['n_components']} components "
          f"({result['variance_explained']:.1%} variance), "
          f"ARI vs family-weighted = {ari:.3f}")
    return result


def centroid_table(feature_frame: pd.DataFrame, labels: pd.Series,
                   tbl: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    PRD req 54: the centroid table in ORIGINAL units, not standardised
    ones - so a row reads "median price $310, HHI 0.04, entire-home share
    0.72" and can be labelled by eye (req 55).

    Each cluster's centroid is the mean of its member neighbourhoods'
    *raw* feature values (`feature_frame`, pre-standardisation). Because
    standardisation and family weighting are both linear, this equals the
    fitted K-means centroid transformed back to original units.

    `n_neighbourhoods` is prepended; `n_listings` (summed listing count) is
    added when `tbl` is passed. Returns a frame indexed by cluster id.
    """
    if not feature_frame.index.equals(labels.index):
        labels = labels.reindex(feature_frame.index)

    centroids = feature_frame.groupby(labels).mean()
    centroids.insert(0, "n_neighbourhoods",
                     labels.value_counts().sort_index())
    if tbl is not None:
        listings = (
            tbl.loc[feature_frame.index, "listing_count"]
            .groupby(labels).sum()
        )
        centroids.insert(1, "n_listings", listings)
    centroids.index.name = "cluster"

    print(f"[clustering] centroid table {centroids.shape[0]} clusters x "
          f"{feature_frame.shape[1]} features (original units)")
    return centroids


def label_clusters(centroids: pd.DataFrame) -> dict[int, str]:
    """
    PRD req 55: attach the human-readable label to each cluster. The labels
    live in `config.CLUSTER_LABELS`; they were written by hand AFTER fitting
    K-means, by reading `centroids` (task 6.6), and each one's centroid
    evidence is recorded beside it in config.

    Because the labels are keyed by the cluster id the fixed seed produces,
    `config.CLUSTER_LABEL_GUARDS` checks that each cluster's defining
    feature still points at the id its label assumes, and this raises if
    the fit has drifted - a wrong label is worse than a loud failure. Each
    guard is `(feature, "idxmax"|"idxmin", expected_cluster_id)`.

    If `config.CLUSTER_LABELS` is empty - a new dataset whose centroids
    have not been inspected and labelled yet - this returns placeholder
    `"Cluster N"` labels instead of raising, so an exploratory run can
    still produce a real centroid table to label from (task 6.7 workflow,
    done once per dataset).

    Returns `{cluster_id: label}`.
    """
    if not config.CLUSTER_LABELS:
        placeholder = {int(cid): f"Cluster {cid}" for cid in centroids.index}
        print("[clustering] no labels configured for this dataset yet - "
              f"placeholder labels: {placeholder}")
        return placeholder

    if set(centroids.index) != set(config.CLUSTER_LABELS):
        raise ValueError(
            f"cluster ids {sorted(centroids.index)} do not match "
            f"config.CLUSTER_LABELS keys {sorted(config.CLUSTER_LABELS)} - "
            "re-inspect the centroid table and rewrite the labels (req 55)."
        )

    # Each check: "the cluster that is the argmax/argmin on this feature
    # must be the id whose hand-written label describes it."
    for feature, op, expected_id in config.CLUSTER_LABEL_GUARDS:
        got = getattr(centroids[feature], op)()
        if got != expected_id:
            raise ValueError(
                f"label guard failed: {op}({feature}) is cluster {got}, "
                f"but config.CLUSTER_LABELS assumes cluster {expected_id} "
                f'("{config.CLUSTER_LABELS[expected_id]}"). The fit drifted - '
                "re-inspect the centroids and update config.CLUSTER_LABELS."
            )

    print(f"[clustering] labels assigned post-hoc: "
          + "; ".join(f"{i}={lab}" for i, lab in config.CLUSTER_LABELS.items()))
    return dict(config.CLUSTER_LABELS)


def write_summary(centroids: pd.DataFrame, labels: dict[int, str],
                  assignments: pd.Series, diag: pd.DataFrame,
                  pca_result: dict, path=None) -> str:
    """
    PRD req 56: `outputs/cluster_summary.md` - the clustering write-up.

    Contains: the k-selection reasoning and the elbow/silhouette numbers
    (req 51), the centroid table in original units (req 54), the post-hoc
    labels with an explicit statement that they were assigned after fitting
    (req 55), the member neighbourhoods per cluster (req 56, the core
    deliverable), and the PCA robustness result - adjusted Rand index and
    what it implies (req 53, success metric 5).
    """
    k = config.CLUSTER_K
    sil_k = float(diag.loc[k, "silhouette"])
    best_k = int(diag["silhouette"].idxmax())

    lines = [
        "# Neighbourhood Clusters",
        "",
        f"Family-weighted K-means over the **{len(assignments)}** retained "
        f"neighbourhoods (>= {config.MIN_LISTINGS_PER_NEIGHBOURHOOD} listings) "
        f"and **{len(centroids.columns) - _n_meta(centroids)}** engineered "
        "features, grouped into eight indicator families each contributing "
        "equally to the distance metric (PRD §7.1). Excluded neighbourhoods "
        "are in `excluded_neighbourhoods.md` and are not clustered.",
        "",
        "## Choosing k",
        "",
        f"k was swept from {diag.index.min()} to {diag.index.max()} "
        "(`figures/elbow_silhouette.png`); the range may fall short of the "
        f"usual {config.CLUSTER_K_RANGE[0]}-{config.CLUSTER_K_RANGE[-1]} "
        "when there are few retained neighbourhoods (k-means requires "
        "k <= n_samples). Swept over "
        f"**{len(assignments)}** retained neighbourhoods and "
        f"**{len(centroids.columns) - _n_meta(centroids)}** engineered "
        f"features (peak silhouette {diag['silhouette'].max():.2f} at k="
        f"{best_k}).",
        "",
        f"**k = {k}** was selected"
        + (f": {config.CLUSTER_K_JUSTIFICATION}"
           if config.CLUSTER_K_JUSTIFICATION else
           " — justification not yet written for this dataset "
           "(placeholder/exploratory run); see the k-sweep table below."),
        "",
        "| k | inertia | mean silhouette |",
        "|--:|--:|--:|",
    ]
    for kk, row in diag.iterrows():
        mark = "  <- selected" if kk == k else ""
        lines.append(
            f"| {kk} | {row['inertia']:.1f} | {row['silhouette']:.3f}{mark} |"
        )

    lines += [
        "",
        f"> Success metric 4 sets a mean-silhouette bar of 0.25. The chosen "
        f"solution scores **{sil_k:.2f}** "
        f"({'meets' if sil_k >= 0.25 else 'below'} that bar).",
        "",
        "## Cluster labels",
        "",
        "Labels were assigned **after** fitting, by reading the centroid "
        "table below in original units. They are descriptive summaries of "
        "each centroid profile, not inputs to the clustering.",
        "",
        "| Cluster | Label | n neighbourhoods | n listings |",
        "|--:|---|--:|--:|",
    ]
    for cid in sorted(labels):
        lines.append(
            f"| {cid} | {labels[cid]} | "
            f"{int(centroids.loc[cid, 'n_neighbourhoods'])} | "
            f"{int(centroids.loc[cid, 'n_listings'])} |"
        )

    lines += [
        "",
        "## Centroid profiles (original units)",
        "",
        "Mean of each feature over the cluster's member neighbourhoods "
        "(req 54). Columns are cluster ids; see the label table above.",
        "",
        centroids.drop(columns=["n_neighbourhoods", "n_listings"])
        .T.round(3)
        .to_markdown(),
        "",
        "## Member neighbourhoods",
        "",
    ]
    for cid in sorted(labels):
        members = sorted(assignments[assignments == cid].index)
        lines += [
            f"### Cluster {cid} - {labels[cid]} ({len(members)})",
            "",
            ", ".join(members),
            "",
        ]

    lines += [
        "## PCA robustness check (req 53)",
        "",
        f"K-means was re-run at k={k} on principal components retaining "
        f"{pca_result['variance_explained']:.1%} of the variance "
        f"({pca_result['n_components']} components) from the standardised, "
        "unweighted features - the alternative to family weighting (PRD "
        "§7.1). Adjusted Rand index between that solution and the "
        f"family-weighted one: **{pca_result['ari']:.3f}**.",
        "",
        (config.PCA_ARI_NOTE if config.PCA_ARI_NOTE else
         "Interpretation not yet written for this dataset (placeholder/"
         "exploratory run) - compare the two solutions' cluster membership "
         "by eye once real labels exist."),
        "",
    ]

    path = path or (config.OUTPUT_DIR / "cluster_summary.md")
    text = "\n".join(lines)
    path.write_text(text, encoding="utf-8")
    print(f"[clustering] cluster summary -> {path} "
          f"(k={k}, silhouette {sil_k:.3f}, ARI {pca_result['ari']:.3f})")
    return text


def _n_meta(centroids: pd.DataFrame) -> int:
    """Count of non-feature bookkeeping columns on a centroid table."""
    return sum(c in centroids.columns for c in ("n_neighbourhoods", "n_listings"))


def _cluster_at_threshold(tbl: pd.DataFrame, threshold: int, k: int) -> pd.Series | None:
    """
    Full standardise -> family-weight -> K-means pipeline at one
    listing-count threshold. Returns the label Series, or None if fewer
    than k neighbourhoods clear the threshold - k-means requires
    n_samples >= k, and a thin dataset (e.g. Antwerp has only 1
    neighbourhood at n >= 200) can fail that at the stricter thresholds.
    """
    frame = aggregate.feature_frame(tbl, threshold=threshold)
    if len(frame) < max(k, 2):
        print(f"[clustering] threshold {threshold}: only {len(frame)} "
              f"retained neighbourhoods, fewer than k={k} - skipped")
        return None
    weighted = family_weight(standardize(frame))
    _, labels = fit_kmeans(weighted, k=k)
    return labels


def _count_reassigned(a: pd.Series, b: pd.Series, k: int) -> int:
    """
    Neighbourhoods whose cluster differs between two label Series on their
    common index, after aligning b's arbitrary cluster ids to a's by the
    assignment that maximises overlap (Hungarian on the contingency table).
    """
    contingency = np.zeros((k, k), dtype=int)
    for ai, bi in zip(a.to_numpy(), b.to_numpy()):
        contingency[ai, bi] += 1
    row_ind, col_ind = linear_sum_assignment(-contingency)
    remap = {int(col): int(row) for row, col in zip(row_ind, col_ind)}
    b_aligned = b.map(remap).to_numpy()
    return int((a.to_numpy() != b_aligned).sum())


def threshold_sensitivity(tbl: pd.DataFrame, thresholds=None,
                          k: int | None = None) -> pd.DataFrame:
    """
    PRD req 41 / task 4.6: re-run the clustering at each listing-count
    threshold and report how many neighbourhoods change cluster assignment
    between thresholds.

    k is held fixed at `config.CLUSTER_K` so the comparison isolates the
    threshold, not a change in k (task 4.6 decision). For each threshold
    pair, cluster ids are matched by maximum overlap on the neighbourhoods
    common to both fits, then the count that still disagree is reported.

    Rows: each adjacent pair plus the widest pair. Columns: `threshold_low`,
    `threshold_high`, `n_common`, `n_changed`, `pct_changed`. Passed to
    `aggregate.write_exclusion_report(sensitivity=...)`.
    """
    thresholds = sorted(thresholds or config.SENSITIVITY_THRESHOLDS)
    k = config.CLUSTER_K if k is None else k

    labels = {t: _cluster_at_threshold(tbl, t, k) for t in thresholds}
    usable = [t for t in thresholds if labels[t] is not None]

    pairs = list(zip(usable, usable[1:]))
    if len(usable) > 2:
        pairs.append((usable[0], usable[-1]))

    rows = []
    for lo, hi in pairs:
        common = labels[lo].index.intersection(labels[hi].index)
        changed = _count_reassigned(
            labels[lo].loc[common], labels[hi].loc[common], k
        )
        rows.append({
            "threshold_low": lo,
            "threshold_high": hi,
            "n_common": len(common),
            "n_changed": changed,
            "pct_changed": round(100 * changed / len(common), 1),
        })

    out = pd.DataFrame(rows)
    print("[clustering] threshold sensitivity (k={}): ".format(k)
          + "; ".join(f"{r.threshold_low}->{r.threshold_high} "
                      f"{r.n_changed}/{r.n_common}" for r in out.itertuples()))
    return out

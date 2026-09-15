"""
Text-derived indicators from listing titles.
Implements PRD requirements 28-34.

Nothing here uses a fixed keyword list. The tourism / upmarket / commercial
grouping is a hypothesis tested against the derived topics in
`compare_to_hypothesis`, not an input to the analysis (req 34).
"""

import re
import unicodedata

import numpy as np
import pandas as pd
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS

from . import config

# The tourism / upmarket / commercial hypothesis under test (req 34) lives
# in `config.HYPOTHESIS` - it names LA landmarks (hollywood, disney,
# universal), so it is per-dataset. These terms are NOT used to build any
# indicator; they exist only so the derived topics can be checked against
# the prior expectation and the comparison reported honestly.


def tokenize(text) -> str:
    """
    PRD req 28: lowercase, strip punctuation, collapse whitespace.
    Null names (2 in the dataset) become empty strings rather than raising.
    Stopword removal is left to the vectoriser so the vocabulary and the
    stopword list stay in one place.

    Accented Latin characters are folded to their base letter (NFKD
    decompose, drop combining marks) before the alnum strip - without this,
    "próximo" or "confortável" (Rio's Portuguese titles) split into
    fragments ("pr", "ximo") at the punctuation-strip step instead of
    surviving as one word. A no-op for the purely-ASCII English/Dutch
    corpora.
    """
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _stopwords(suppress_place_and_type: bool, neighbourhoods=None) -> list:
    """
    Build the stopword list.

    With suppress_place_and_type=False this is scikit-learn's English list
    and nothing more — the PRD's literal specification.

    With it True, every word appearing in a neighbourhood label is added,
    plus the curated place and room-type sets in config. See the task 3.0
    note in config.py for why: without this, NMF recovers `neighbourhood`
    and `room_type` from the titles and calls them topics.
    """
    words = set(ENGLISH_STOP_WORDS) | set(config.EXTRA_STOPWORDS)
    if not suppress_place_and_type:
        return list(words)
    words |= config.SUPPRESS_PLACE_EXTRA
    words |= config.SUPPRESS_ROOM_TYPE
    for label in (neighbourhoods if neighbourhoods is not None else []):
        words.update(re.sub(r"[^a-z ]", " ", str(label).lower()).split())
    return list(words)


def build_tfidf(df: pd.DataFrame, min_df: int = None,
                suppress_place_and_type: bool = True):
    """
    PRD req 29: TF-IDF over all listing titles, unigrams and bigrams,
    excluding terms appearing in fewer than min_df listings.

    suppress_place_and_type defaults True (task 3.0 decision). Pass False to
    reproduce the unsuppressed baseline that motivated the choice.
    """
    min_df = config.TFIDF_MIN_DF if min_df is None else min_df
    corpus = df["name"].map(tokenize)
    vec = TfidfVectorizer(
        stop_words=_stopwords(suppress_place_and_type,
                              df["neighbourhood"].unique()),
        ngram_range=(1, 2),
        min_df=min_df,
        sublinear_tf=True,
    )
    matrix = vec.fit_transform(corpus)
    return vec, matrix


def distinguishing_terms(df, vec, matrix, top_k: int = 15) -> dict:
    """
    PRD req 30: mean TF-IDF vector per neighbourhood, top terms extracted.
    These are the terms that separate a neighbourhood's listings from the
    corpus as a whole.
    """
    vocab = np.array(vec.get_feature_names_out())
    out = {}
    for name, idx in df.groupby("neighbourhood").indices.items():
        mean_vec = np.asarray(matrix[idx].mean(axis=0)).ravel()
        top = np.argsort(mean_vec)[::-1][:top_k]
        out[name] = [(vocab[i], float(mean_vec[i])) for i in top if mean_vec[i] > 0]
    return out


def topic_coherence(model, vec, matrix, top_n: int = 10) -> float:
    """
    UMass-style coherence over the top terms of each topic. Higher is better
    (values are negative). Computed on the binarised document-term matrix so
    it measures genuine co-occurrence rather than weighted similarity.
    """
    vocab_terms = np.array(vec.get_feature_names_out())
    binary = (matrix > 0).astype(int)
    n_docs = binary.shape[0]
    scores = []
    for comp in model.components_:
        top_idx = np.argsort(comp)[::-1][:top_n]
        for i in range(1, len(top_idx)):
            for j in range(i):
                di = binary[:, top_idx[i]]
                dj = binary[:, top_idx[j]]
                co = int(di.multiply(dj).sum())
                dj_count = int(dj.sum())
                if dj_count == 0:
                    continue
                scores.append(np.log((co + 1) / dj_count))
    _ = vocab_terms, n_docs
    return float(np.mean(scores)) if scores else float("nan")


def select_topics(vec, matrix, k_range=None):
    """
    PRD req 31: fit NMF for each k, select by coherence, record the
    justification. NMF rather than LDA: titles average under 10 tokens and
    LDA's Dirichlet prior behaves poorly at that length (PRD §7.3).
    """
    k_range = config.NMF_K_RANGE if k_range is None else k_range
    results = []
    for k in k_range:
        model = NMF(
            n_components=k,
            random_state=config.RANDOM_SEED,
            init="nndsvda",
            max_iter=400,
        )
        W = model.fit_transform(matrix)
        results.append({
            "k": k,
            "coherence": topic_coherence(model, vec, matrix),
            "reconstruction_err": float(model.reconstruction_err_),
            "model": model,
            "W": W,
        })
    # Coherence is a weak selector on this corpus — the candidate k values
    # span roughly 0.1 of each other and the metric trends with k, which is
    # its known failure mode. The selection is therefore reported with its
    # margin so a reader can see how thin it is, rather than presented as a
    # clean optimum.
    best = max(results, key=lambda r: r["coherence"])
    ranked = sorted((r["coherence"] for r in results), reverse=True)
    best["margin_over_runner_up"] = (
        ranked[0] - ranked[1] if len(ranked) > 1 else float("nan")
    )
    return best, results


def topic_terms(model, vec, top_n: int = 12) -> list:
    """PRD req 32: top-weighted terms per topic."""
    vocab = np.array(vec.get_feature_names_out())
    return [
        [(vocab[i], float(comp[i])) for i in np.argsort(comp)[::-1][:top_n]]
        for comp in model.components_
    ]


def neighbourhood_loadings(df, W) -> pd.DataFrame:
    """
    PRD req 33: mean topic distribution across each neighbourhood's
    listings, row-normalised so loadings are comparable across
    neighbourhoods of different sizes.
    """
    W_norm = W / np.clip(W.sum(axis=1, keepdims=True), 1e-12, None)
    frame = pd.DataFrame(
        W_norm,
        columns=[f"topic_{i}_loading" for i in range(W.shape[1])],
        index=df.index,
    )
    frame["neighbourhood"] = df["neighbourhood"].values
    return frame.groupby("neighbourhood").mean()


def compare_to_hypothesis(terms_per_topic) -> pd.DataFrame:
    """
    PRD req 34: check the derived topics against the tourism / upmarket /
    commercial prior. Reports overlap, not a score to optimise — the point
    is to state whether the prior held, either way.
    """
    rows = []
    for t_idx, terms in enumerate(terms_per_topic):
        words = {w for w, _ in terms}
        row = {"topic": t_idx}
        for label, expected in config.HYPOTHESIS.items():
            hits = sorted(words & set(expected))
            row[f"{label}_hits"] = len(hits)
            row[f"{label}_terms"] = ", ".join(hits) if hits else "—"
        rows.append(row)
    return pd.DataFrame(rows)


def min_df_sensitivity(df, k, values=None) -> pd.DataFrame:
    """
    PRD §7.3: refit at each min_df and measure whether the topics survive.

    Overlap is Jaccard on each topic's top-10 term set against the closest
    topic from the reference fit. Topics are permutation-invariant across
    NMF runs, so matching is by best overlap rather than by index.
    """
    values = config.TFIDF_MIN_DF_SENSITIVITY if values is None else values
    ref_vec, ref_m = build_tfidf(df, min_df=config.TFIDF_MIN_DF)
    ref_model = NMF(n_components=k, random_state=config.RANDOM_SEED,
                    init="nndsvda", max_iter=400).fit(ref_m)
    ref_sets = [{w for w, _ in t} for t in topic_terms(ref_model, ref_vec, 10)]

    rows = []
    for v in values:
        vec, m = build_tfidf(df, min_df=v)
        model = NMF(n_components=k, random_state=config.RANDOM_SEED,
                    init="nndsvda", max_iter=400).fit(m)
        sets = [{w for w, _ in t} for t in topic_terms(model, vec, 10)]
        overlaps = [
            max(len(a & b) / len(a | b) for b in sets) for a in ref_sets
        ]
        rows.append({
            "min_df": v,
            "vocabulary": len(vec.get_feature_names_out()),
            "mean_topic_overlap": float(np.mean(overlaps)),
            "min_topic_overlap": float(np.min(overlaps)),
        })
    return pd.DataFrame(rows)


def write_report(df, path=None) -> pd.DataFrame:
    """
    Run both vocabularies, write topic_model.md, and return the
    per-neighbourhood topic loadings for the suppressed fit.

    Both runs are reported because the suppression is a researcher choice.
    The baseline is the evidence for why it was made; omitting it would
    present a decision as if the data had made it.
    """
    lines = ["# Topic Model", ""]
    loadings = None

    for suppressed in (False, True):
        label = "Suppressed vocabulary (used)" if suppressed else "Baseline vocabulary"
        vec, m = build_tfidf(df, suppress_place_and_type=suppressed)
        best, results = select_topics(vec, m)
        terms = topic_terms(best["model"], vec, 10)

        lines += [
            f"## {label}",
            "",
            f"- Vocabulary: {len(vec.get_feature_names_out())} terms "
            f"(unigrams + bigrams, min_df={config.TFIDF_MIN_DF})",
            f"- Selected k = **{best['k']}** by UMass coherence "
            f"({best['coherence']:.4f}), margin over runner-up "
            f"{best['margin_over_runner_up']:.4f}",
            "",
            "| k | coherence | reconstruction error |",
            "|---:|---:|---:|",
        ]
        for r in results:
            lines.append(f"| {r['k']} | {r['coherence']:.4f} | "
                         f"{r['reconstruction_err']:.2f} |")
        lines += ["", "| Topic | Top terms |", "|---:|---|"]
        for i, t in enumerate(terms):
            lines.append(f"| {i} | {', '.join(w for w, _ in t)} |")
        lines.append("")

        if suppressed:
            hyp = compare_to_hypothesis(terms)
            lines += [
                "### Hypothesis check (req 34)",
                "",
                "The tourism / upmarket / commercial grouping was a prior, "
                "not an input. Overlap with the derived topics:",
                "",
                hyp.to_markdown(index=False),
                "",
                "Sensitivity to `min_df` (topic-set Jaccard vs. the "
                f"min_df={config.TFIDF_MIN_DF} fit):",
                "",
                min_df_sensitivity(df, best["k"]).to_markdown(index=False),
                "",
            ]
            loadings = neighbourhood_loadings(df, best["W"])
        else:
            lines += [
                "**Why this run is not used.** Most topics here reproduce "
                "place names and room types — information already held in "
                "`neighbourhood`, `room_type`, and the five distance columns "
                "from task 2.0. Using these loadings as clustering features "
                "would weight geography a second time. The suppressed run "
                "above is used instead; this one is the evidence for that "
                "choice.",
                "",
            ]

    path = path or (config.OUTPUT_DIR / "topic_model.md")
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[text] topic model -> {path}")
    return loadings

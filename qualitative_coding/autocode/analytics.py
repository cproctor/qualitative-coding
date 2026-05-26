"""Embedding-based code analytics: outliers, cohesion, similar codes."""
import numpy as np
from collections import defaultdict
import structlog

log = structlog.get_logger()


def _get_code_embeddings(corpus, embedder, codes=None, coders=None,
                         pattern=None, file_list=None):
    """Return {code_name: [(doc_id, line, vec), ...]} for all matching codes."""
    with corpus.session():
        coded_lines = corpus.get_coded_lines(
            codes=codes,
            coders=list(coders) if coders else None,
            pattern=pattern,
            file_list=file_list,
        )

    by_doc = defaultdict(set)
    line_to_codes = defaultdict(lambda: defaultdict(list))
    for code_id, coder_id, line, doc_id in coded_lines:
        by_doc[doc_id].add(line)
        line_to_codes[doc_id][line].append(code_id)

    code_vecs = defaultdict(list)
    for doc_id, lines in by_doc.items():
        embedder.ensure_embedded(doc_id)
        matrix, line_numbers = embedder.get_embeddings(doc_id)
        for line in lines:
            idx = embedder.embedding_key_for_line(line, line_numbers)
            if idx is not None:
                vec = matrix[idx]
                for code in line_to_codes[doc_id][line]:
                    code_vecs[code].append((doc_id, line, vec))

    return {code: data for code, data in code_vecs.items()}


def _l2_normalize(vecs):
    """L2-normalize a matrix of row vectors, handling zero-norm rows."""
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1, norms)
    return vecs / norms


def compute_outliers(corpus, embedder, classifiers, codes=None, coders=None,
                     pattern=None, file_list=None, n=5):
    """For each code, find N positive examples the classifier is least confident about.

    Uses the trained classifier's calibrated probability on training examples.
    A positive example with low P(positive) lies near the decision boundary—
    likely a miscode or edge case worth reviewing.

    Returns {code_name: [(doc_id, line, confidence), ...]}.
    """
    code_data = _get_code_embeddings(corpus, embedder, codes=codes, coders=coders,
                                     pattern=pattern, file_list=file_list)
    results = {}
    for code_name, items in code_data.items():
        clf = classifiers.get(code_name)
        if clf is None or len(items) < 2:
            continue
        vecs = _l2_normalize(np.array([v for _, _, v in items]))
        confidences = clf.predict_proba(vecs)[:, 1]
        idx_sorted = np.argsort(confidences)[:n]  # ascending: lowest confidence first
        results[code_name] = [
            (items[i][0], items[i][1], float(confidences[i])) for i in idx_sorted
        ]
    return results


def compute_cohesion(corpus, embedder, codes=None, coders=None,
                     pattern=None, file_list=None):
    """Compute per-code cohesion as fraction of variance explained by first PCA component.

    Embeddings are L2-normalized before PCA, respecting the hyperspherical geometry
    of the embedding space. High explained variance indicates a tight, semantically
    coherent code; low explained variance suggests the code covers disparate concepts
    and may benefit from splitting.

    Returns {code_name: {"examples": N, "variance_explained": float, "suggestion": str}}.
    """
    from sklearn.decomposition import PCA

    code_data = _get_code_embeddings(corpus, embedder, codes=codes, coders=coders,
                                     pattern=pattern, file_list=file_list)
    results = {}
    for code_name, items in code_data.items():
        n = len(items)
        if n < 2:
            results[code_name] = {"examples": n, "variance_explained": None,
                                  "suggestion": "too few examples"}
            continue
        vecs = _l2_normalize(np.array([v for _, _, v in items]))
        pca = PCA(n_components=1)
        pca.fit(vecs)
        var_explained = float(pca.explained_variance_ratio_[0])
        if var_explained >= 0.5:
            suggestion = "tight — well-defined code"
        elif var_explained >= 0.25:
            suggestion = "moderate cohesion"
        else:
            suggestion = "scattered — consider splitting"
        results[code_name] = {
            "examples": n,
            "variance_explained": round(var_explained, 3),
            "suggestion": suggestion,
        }
    return results


def compute_similar(corpus, embedder, classifiers, codes=None, coders=None,
                    pattern=None, file_list=None, threshold=0.5):
    """Find pairs of codes whose classifiers generalize to each other's examples.

    For each pair (A, B): computes mean P(B | A's examples) and mean P(A | B's examples).
    High scores in both directions suggest merge candidates; asymmetric scores suggest
    a subset relationship. Only pairs where both codes have trained classifiers are included.

    Returns [(code_a, code_b, p_b_on_a, p_a_on_b), ...] sorted by max score descending.
    """
    code_data = _get_code_embeddings(corpus, embedder, codes=codes, coders=coders,
                                     pattern=pattern, file_list=file_list)

    normalized = {}
    for code_name, items in code_data.items():
        if not items or code_name not in classifiers:
            continue
        normalized[code_name] = _l2_normalize(np.array([v for _, _, v in items]))

    code_names = sorted(normalized.keys())
    pairs = []
    for i, ca in enumerate(code_names):
        for cb in code_names[i + 1:]:
            p_b_on_a = float(classifiers[cb].predict_proba(normalized[ca])[:, 1].mean())
            p_a_on_b = float(classifiers[ca].predict_proba(normalized[cb])[:, 1].mean())
            if max(p_b_on_a, p_a_on_b) >= threshold:
                pairs.append((ca, cb, round(p_b_on_a, 3), round(p_a_on_b, 3)))

    pairs.sort(key=lambda x: max(x[2], x[3]), reverse=True)
    return pairs

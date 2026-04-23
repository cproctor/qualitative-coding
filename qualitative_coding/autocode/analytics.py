"""Embedding-based code analytics: outliers, density, similar codes."""
import numpy as np
from collections import defaultdict
import structlog

log = structlog.get_logger()


def _get_code_embeddings(corpus, embedder, codes=None, coders=None,
                         pattern=None, file_list=None):
    """Return {code_name: np.ndarray of shape (n, dim)} for all matching codes."""
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

    # Load embeddings per document
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


def compute_outliers(corpus, embedder, codes=None, coders=None,
                     pattern=None, file_list=None, n=5):
    """For each code, find the N most distant coded lines from the centroid.

    Returns {code_name: [(doc_id, line, distance), ...]}.
    """
    code_data = _get_code_embeddings(corpus, embedder, codes=codes, coders=coders,
                                     pattern=pattern, file_list=file_list)
    results = {}
    for code_name, items in code_data.items():
        if len(items) < 2:
            continue
        vecs = np.array([v for _, _, v in items])
        centroid = vecs.mean(axis=0)
        dists = np.linalg.norm(vecs - centroid, axis=1)
        idx_sorted = np.argsort(dists)[::-1][:n]
        results[code_name] = [
            (items[i][0], items[i][1], float(dists[i])) for i in idx_sorted
        ]
    return results


def compute_density(corpus, embedder, codes=None, coders=None,
                    pattern=None, file_list=None):
    """Compute per-code cohesion as mean pairwise cosine distance.

    Returns {code_name: {"examples": N, "mean_distance": float, "suggestion": str}}.
    """
    code_data = _get_code_embeddings(corpus, embedder, codes=codes, coders=coders,
                                     pattern=pattern, file_list=file_list)
    results = {}
    for code_name, items in code_data.items():
        n = len(items)
        if n < 2:
            results[code_name] = {"examples": n, "mean_distance": None,
                                  "suggestion": "too few examples"}
            continue
        vecs = np.array([v for _, _, v in items])
        # Normalize for cosine distance
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)
        normalized = vecs / norms
        # Pairwise cosine distance = 1 - cosine similarity
        sim_matrix = normalized @ normalized.T
        np.fill_diagonal(sim_matrix, 1.0)
        mean_dist = float(1.0 - sim_matrix[np.triu_indices(n, k=1)].mean())
        if mean_dist < 0.2:
            suggestion = "tight — well-defined code"
        elif mean_dist < 0.5:
            suggestion = "moderate cohesion"
        else:
            suggestion = "scattered — consider splitting"
        results[code_name] = {
            "examples": n,
            "mean_distance": round(mean_dist, 3),
            "suggestion": suggestion,
        }
    return results


def compute_similar(corpus, embedder, codes=None, coders=None,
                    pattern=None, file_list=None, threshold=0.8):
    """Find pairs of codes whose embedding centroids are similar.

    Returns [(code_a, code_b, similarity), ...] sorted descending.
    """
    code_data = _get_code_embeddings(corpus, embedder, codes=codes, coders=coders,
                                     pattern=pattern, file_list=file_list)

    centroids = {}
    for code_name, items in code_data.items():
        if not items:
            continue
        vecs = np.array([v for _, _, v in items])
        centroid = vecs.mean(axis=0)
        norm = np.linalg.norm(centroid)
        centroids[code_name] = centroid / norm if norm > 0 else centroid

    code_names = sorted(centroids.keys())
    pairs = []
    for i, ca in enumerate(code_names):
        for cb in code_names[i + 1:]:
            sim = float(np.dot(centroids[ca], centroids[cb]))
            if sim >= threshold:
                pairs.append((ca, cb, round(sim, 3)))

    pairs.sort(key=lambda x: x[2], reverse=True)
    return pairs

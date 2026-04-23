from collections import defaultdict
from random import sample
import numpy as np
import structlog

log = structlog.get_logger()


class AutocodeTrainer:
    """Trains per-code classifiers from hand-coded corpus lines.

    For each qualifying code, fits a CalibratedClassifierCV(LinearSVC())
    on the embeddings of coded lines (positives) vs a random sample of
    other coded lines (negatives). Classifiers are never persisted — they
    are always rebuilt on demand from the embeddings cache and DB.
    """

    def __init__(self, corpus, embedder):
        self.corpus = corpus
        self.embedder = embedder
        settings = corpus.settings
        self.min_examples = settings.get("autocode_min_examples", 5)

    def _load_all_embeddings(self, coders=None, pattern=None, file_list=None):
        """Load embeddings for all relevant coded lines.

        Returns {(document_id, line): embedding_vector}.
        Also ensures embeddings are available (embeds on demand if needed).
        """
        with self.corpus.session():
            coded_lines = self.corpus.get_coded_lines(
                coders=list(coders) if coders else None,
                pattern=pattern,
                file_list=file_list,
            )

        by_doc = defaultdict(set)
        for code_id, coder_id, line, doc_id in coded_lines:
            by_doc[doc_id].add(line)

        embeddings = {}
        for doc_id, lines in by_doc.items():
            self.embedder.ensure_embedded(doc_id)
            matrix, line_numbers = self.embedder.get_embeddings(doc_id)
            for line in lines:
                idx = self.embedder.embedding_key_for_line(line, line_numbers)
                if idx is not None:
                    embeddings[(doc_id, line)] = matrix[idx]
        return embeddings

    def describe(self, codes=None, coders=None, pattern=None, file_list=None):
        """Return training statistics without fitting any classifiers.

        Returns {code_name: {"positive_examples": N, "status": "trained"|"skipped"}}.
        """
        with self.corpus.session():
            all_coded = self.corpus.get_coded_lines(
                codes=codes,
                coders=list(coders) if coders else None,
                pattern=pattern,
                file_list=file_list,
            )

        by_code = defaultdict(set)
        for code_id, coder_id, line, doc_id in all_coded:
            by_code[code_id].add((doc_id, line))

        result = {}
        for code_name, units in by_code.items():
            n = len(units)
            result[code_name] = {
                "positive_examples": n,
                "status": "trained" if n >= self.min_examples else "skipped",
            }
        return result

    def train(self, codes=None, coders=None, pattern=None, file_list=None):
        """Fit one CalibratedClassifierCV(LinearSVC()) per qualifying code.

        Returns {code_name: fitted_classifier}.
        """
        from sklearn.svm import LinearSVC
        from sklearn.calibration import CalibratedClassifierCV

        all_embeddings = self._load_all_embeddings(
            coders=coders, pattern=pattern, file_list=file_list
        )
        if not all_embeddings:
            log.warning("autocode train: no embeddings found")
            return {}

        with self.corpus.session():
            all_coded = self.corpus.get_coded_lines(
                codes=codes,
                coders=list(coders) if coders else None,
                pattern=pattern,
                file_list=file_list,
            )

        # Group coded units by code
        by_code = defaultdict(set)
        for code_id, coder_id, line, doc_id in all_coded:
            by_code[code_id].add((doc_id, line))

        all_units = set(all_embeddings.keys())
        classifiers = {}

        for code_name, positive_units in by_code.items():
            positives = [u for u in positive_units if u in all_embeddings]
            n_pos = len(positives)
            if n_pos < self.min_examples:
                log.debug("autocode train: skipping code (too few examples)",
                          code=code_name, n=n_pos, min=self.min_examples)
                continue

            # Negatives: sample 2x positives from all other coded units
            negative_pool = list(all_units - positive_units)
            n_neg = min(len(negative_pool), 2 * n_pos)
            negatives = sample(negative_pool, n_neg) if negative_pool else []

            X = np.array(
                [all_embeddings[u] for u in positives]
                + [all_embeddings[u] for u in negatives]
            )
            y = [1] * len(positives) + [0] * len(negatives)

            cv = min(5, n_pos, len(negatives)) if negatives else 2
            clf = CalibratedClassifierCV(LinearSVC(max_iter=2000), cv=cv)
            clf.fit(X, y)
            classifiers[code_name] = clf
            log.debug("autocode train: trained classifier",
                      code=code_name, n_pos=n_pos, n_neg=n_neg)

        log.info("autocode train", n_trained=len(classifiers),
                 n_skipped=len(by_code) - len(classifiers))
        return classifiers

from collections import defaultdict
import numpy as np
import structlog

log = structlog.get_logger()

AUTOCODE_DEFAULTS = {
    "autocode_confidence_threshold": 0.6,
    "autocode_child_threshold": 0.4,
}


class AutocodePredictor:
    """Applies trained classifiers to corpus lines, writing CodedLines."""

    def __init__(self, corpus, embedder, classifiers):
        self.corpus = corpus
        self.embedder = embedder
        self.classifiers = classifiers
        s = corpus.settings
        self.confidence_threshold = s.get(
            "autocode_confidence_threshold",
            AUTOCODE_DEFAULTS["autocode_confidence_threshold"],
        )
        self.child_threshold = s.get(
            "autocode_child_threshold",
            AUTOCODE_DEFAULTS["autocode_child_threshold"],
        )

    def predict_line(self, embedding):
        """Return {code: P(positive)} for all trained codes."""
        result = {}
        vec = embedding.reshape(1, -1)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        for code_name, clf in self.classifiers.items():
            proba = clf.predict_proba(vec)[0]
            # proba[1] is P(positive label)
            result[code_name] = float(proba[1])
        return result

    def apply_tree_descent(self, raw_predictions, apply_hierarchy=True):
        """Post-process predictions using tree-descent.

        Walks the codebook tree top-down. At each node: if confidence
        exceeds autocode_confidence_threshold, consider children. If no
        child exceeds autocode_child_threshold, predict the parent and
        stop descending.

        When apply_hierarchy=False, simply threshold all predictions.
        """
        if not apply_hierarchy:
            return [
                code for code, conf in raw_predictions.items()
                if conf >= self.confidence_threshold
            ]

        with self.corpus.session():
            tree = self.corpus.get_codebook()

        predicted = []

        def descend(node):
            if node.is_root():
                for child in node.children:
                    descend(child)
                return
            conf = raw_predictions.get(node.name, 0.0)
            if conf < self.confidence_threshold:
                return
            # Check if any child meets the child threshold
            qualifying_children = [
                c for c in node.children
                if raw_predictions.get(c.name, 0.0) >= self.child_threshold
            ]
            if qualifying_children:
                for child in qualifying_children:
                    descend(child)
            else:
                predicted.append(node.name)

        descend(tree)
        return predicted

    def apply(self, coder, pattern=None, file_list=None,
              codes=None, only_uncoded=True, apply_hierarchy=True):
        """Predict codes for corpus lines and write CodedLines to DB.

        Returns {code_name: count_written}.
        """
        with self.corpus.session():
            documents = self.corpus.get_documents(pattern=pattern, file_list=file_list)

        counts = defaultdict(int)
        for doc in documents:
            self.embedder.ensure_embedded(doc.file_path)
            matrix, line_numbers = self.embedder.get_embeddings(doc.file_path)

            with self.corpus.session():
                existing = set()
                if only_uncoded:
                    for cl in self.corpus.get_coded_lines(
                        file_list=[doc.file_path]
                    ):
                        existing.add(cl[2])  # line number

            unit = self.embedder.unit
            coded_line_data = []
            for idx, line_num in enumerate(line_numbers):
                if only_uncoded:
                    # For document unit, skip entire document if anything is coded.
                    # For line/paragraph, skip the specific representative line.
                    if unit == "document" and existing:
                        continue
                    elif unit != "document" and line_num in existing:
                        continue
                embedding = matrix[idx]
                raw = self.predict_line(embedding)

                if codes:
                    raw = {k: v for k, v in raw.items() if k in codes}

                predicted = self.apply_tree_descent(raw, apply_hierarchy)
                for code in predicted:
                    coded_line_data.append({"line": line_num, "code_id": code})
                    counts[code] += 1

            if coded_line_data:
                with self.corpus.session():
                    self.corpus.update_coded_lines(
                        doc.file_path, coder, coded_line_data
                    )

        log.info("autocode apply", coder=coder,
                 total=sum(counts.values()), by_code=dict(counts))
        return dict(counts)

    def score_all_lines(self, pattern=None, file_list=None):
        """Return [(document_id, line, code, confidence), ...] without writing to DB."""
        with self.corpus.session():
            documents = self.corpus.get_documents(pattern=pattern, file_list=file_list)

        scores = []
        for doc in documents:
            self.embedder.ensure_embedded(doc.file_path)
            matrix, line_numbers = self.embedder.get_embeddings(doc.file_path)
            for idx, line_num in enumerate(line_numbers):
                raw = self.predict_line(matrix[idx])
                for code, conf in raw.items():
                    scores.append((doc.file_path, line_num, code, conf))
        return scores

from tests.fixtures import QCTestCase
from unittest.mock import MagicMock
import numpy as np

EMBED_DIM = 8


def make_fixture_classifiers():
    """Return fake classifiers that return controllable probabilities."""
    def make_clf(positive_prob):
        clf = MagicMock()
        clf.predict_proba.return_value = np.array([[1 - positive_prob, positive_prob]])
        return clf
    return {
        "pace": make_clf(0.9),    # high confidence → should be predicted
        "light": make_clf(0.3),   # below threshold → should not be predicted
    }


class TestAutocodePredictor(QCTestCase):
    def setUp(self):
        super().setUp()
        self.run_in_testpath("qc corpus import macbeth.txt --importer verbatim")
        # Populate codebook so tree descent has nodes to work with
        with self.corpus.session():
            self.corpus.update_coded_lines("macbeth.txt", "human", [
                {"line": 0, "code_id": "pace"},
                {"line": 1, "code_id": "pace"},
                {"line": 2, "code_id": "light"},
            ])
        rng = np.random.default_rng(42)
        self.matrix = rng.random((10, EMBED_DIM), dtype=np.float32)
        self.line_numbers = list(range(10))

        self.mock_embedder = MagicMock()
        self.mock_embedder.get_embeddings.return_value = (
            self.matrix, self.line_numbers
        )
        self.mock_embedder.ensure_embedded.return_value = None

        from qualitative_coding.autocode.predictor import AutocodePredictor
        self.predictor = AutocodePredictor(
            self.corpus,
            self.mock_embedder,
            make_fixture_classifiers(),
        )

    def test_predict_line_returns_confidences(self):
        embedding = self.matrix[0]
        result = self.predictor.predict_line(embedding)
        self.assertIn("pace", result)
        self.assertIn("light", result)
        self.assertAlmostEqual(result["pace"], 0.9)
        self.assertAlmostEqual(result["light"], 0.3)

    def test_apply_tree_descent_flat_threshold(self):
        raw = {"pace": 0.9, "light": 0.3}
        predicted = self.predictor.apply_tree_descent(raw, apply_hierarchy=False)
        self.assertIn("pace", predicted)
        self.assertNotIn("light", predicted)

    def test_apply_tree_descent_with_hierarchy(self):
        # With no codebook hierarchy, tree descent falls back to threshold
        raw = {"pace": 0.9, "light": 0.3}
        predicted = self.predictor.apply_tree_descent(raw, apply_hierarchy=True)
        self.assertIn("pace", predicted)
        self.assertNotIn("light", predicted)

    def test_apply_writes_coded_lines(self):
        # Pre-register the mock embedder's document
        with self.corpus.session():
            # Check no coded lines exist yet under 'autocode'
            counts_before = self.corpus.count_codes(coders=["autocode"])
        self.assertEqual(sum(counts_before.values()), 0)

        result = self.predictor.apply("autocode")
        self.assertIn("pace", result)
        self.assertGreater(result["pace"], 0)

        with self.corpus.session():
            counts_after = self.corpus.count_codes(coders=["autocode"])
        self.assertGreater(sum(counts_after.values()), 0)

    def test_apply_only_uncoded_skips_existing(self):
        # First pass: code all lines
        self.predictor.apply("autocode", only_uncoded=False)
        with self.corpus.session():
            first_count = sum(
                self.corpus.count_codes(coders=["autocode"]).values()
            )
        # Second pass with only_uncoded=True: no new predictions for already-coded lines
        result2 = self.predictor.apply("autocode2", only_uncoded=True)
        # All lines already coded by autocode, so autocode2 gets nothing
        self.assertEqual(sum(result2.values()), 0)

    def test_score_all_lines_returns_scores(self):
        scores = self.predictor.score_all_lines()
        self.assertGreater(len(scores), 0)
        # Each score is (doc_id, line, code, confidence)
        doc_id, line, code, conf = scores[0]
        self.assertIsInstance(doc_id, str)
        self.assertIsInstance(line, int)
        self.assertIsInstance(code, str)
        self.assertIsInstance(conf, float)

from tests.fixtures import QCTestCase
from unittest.mock import patch, MagicMock
import numpy as np

EMBED_DIM = 8


def make_embedder_mock(corpus, n_lines=10):
    """Return a mock embedder that serves synthetic embeddings."""
    rng = np.random.default_rng(42)
    matrix = rng.random((n_lines, EMBED_DIM), dtype=np.float32)
    line_numbers = list(range(n_lines))

    mock_embedder = MagicMock()
    mock_embedder.get_embeddings.return_value = (matrix, line_numbers)
    mock_embedder.ensure_embedded.return_value = None
    mock_embedder.corpus = corpus
    return mock_embedder


class TestAutocodeTrainer(QCTestCase):
    def setUp(self):
        super().setUp()
        self.run_in_testpath("qc corpus import macbeth.txt --importer verbatim")
        with self.corpus.session():
            self.corpus.update_coded_lines("macbeth.txt", "chris", [
                {"line": 0, "code_id": "pace"},
                {"line": 1, "code_id": "pace"},
                {"line": 2, "code_id": "pace"},
                {"line": 3, "code_id": "pace"},
                {"line": 4, "code_id": "pace"},
                {"line": 5, "code_id": "light"},
                {"line": 6, "code_id": "light"},
                {"line": 7, "code_id": "light"},
                {"line": 8, "code_id": "light"},
                {"line": 9, "code_id": "light"},
            ])
        from qualitative_coding.autocode.trainer import AutocodeTrainer
        self.mock_embedder = make_embedder_mock(self.corpus)
        self.trainer = AutocodeTrainer(self.corpus, self.mock_embedder)

    def test_describe_returns_code_stats(self):
        stats = self.trainer.describe()
        self.assertIn("pace", stats)
        self.assertIn("light", stats)
        self.assertEqual(stats["pace"]["positive_examples"], 5)
        self.assertEqual(stats["pace"]["status"], "trained")

    def test_describe_marks_skipped_codes(self):
        # Add a code with fewer than min_examples (default 5) examples
        with self.corpus.session():
            self.corpus.update_coded_lines("macbeth.txt", "chris", [
                {"line": 0, "code_id": "pace"},
                {"line": 1, "code_id": "pace"},
                {"line": 2, "code_id": "pace"},
                {"line": 3, "code_id": "pace"},
                {"line": 4, "code_id": "pace"},
                {"line": 5, "code_id": "light"},
                {"line": 6, "code_id": "light"},
                {"line": 7, "code_id": "light"},
                {"line": 8, "code_id": "light"},
                {"line": 9, "code_id": "light"},
                {"line": 0, "code_id": "rare"},  # Only 1 example
            ])
        stats = self.trainer.describe()
        self.assertEqual(stats["rare"]["status"], "skipped")

    def test_train_returns_classifiers(self):
        classifiers = self.trainer.train()
        self.assertIn("pace", classifiers)
        self.assertIn("light", classifiers)

    def test_train_classifiers_predict_proba(self):
        classifiers = self.trainer.train()
        # Each classifier should support predict_proba
        rng = np.random.default_rng(0)
        x = rng.random((1, EMBED_DIM), dtype=np.float32)
        for code, clf in classifiers.items():
            proba = clf.predict_proba(x)
            self.assertEqual(proba.shape, (1, 2))
            self.assertAlmostEqual(sum(proba[0]), 1.0, places=5)

    def test_train_skips_insufficient_codes(self):
        with self.corpus.session():
            self.corpus.update_coded_lines("macbeth.txt", "chris", [
                {"line": 0, "code_id": "pace"},
                {"line": 1, "code_id": "pace"},
                {"line": 2, "code_id": "pace"},
                {"line": 3, "code_id": "pace"},
                {"line": 4, "code_id": "pace"},
                {"line": 5, "code_id": "light"},
                {"line": 6, "code_id": "light"},
                {"line": 7, "code_id": "light"},
                {"line": 8, "code_id": "light"},
                {"line": 9, "code_id": "light"},
                {"line": 0, "code_id": "rare"},
            ])
        classifiers = self.trainer.train()
        self.assertNotIn("rare", classifiers)

    def test_train_coder_filter(self):
        with self.corpus.session():
            self.corpus.update_coded_lines("macbeth.txt", "varun", [
                {"line": 0, "code_id": "other"},
                {"line": 1, "code_id": "other"},
                {"line": 2, "code_id": "other"},
                {"line": 3, "code_id": "other"},
                {"line": 4, "code_id": "other"},
            ])
        classifiers = self.trainer.train(coders=["chris"])
        self.assertNotIn("other", classifiers)

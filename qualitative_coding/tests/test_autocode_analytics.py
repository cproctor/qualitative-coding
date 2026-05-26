from tests.fixtures import QCTestCase
from unittest.mock import MagicMock
import numpy as np

EMBED_DIM = 8


def make_mock_embedder(corpus):
    rng = np.random.default_rng(99)
    n_lines = 10
    matrix = rng.random((n_lines, EMBED_DIM), dtype=np.float32)
    line_numbers = list(range(n_lines))
    mock = MagicMock()
    mock.get_embeddings.return_value = (matrix, line_numbers)
    mock.ensure_embedded.return_value = None
    mock.unit = "line"
    mock.embedding_key_for_line.side_effect = (
        lambda line, lnums: line if line in lnums else None
    )
    mock.corpus = corpus
    return mock


class TestEmbeddingAnalytics(QCTestCase):
    def setUp(self):
        super().setUp()
        self.run_in_testpath("qc corpus import macbeth.txt --importer verbatim")
        with self.corpus.session():
            self.corpus.update_coded_lines("macbeth.txt", "human", [
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
        self.mock_embedder = make_mock_embedder(self.corpus)
        from qualitative_coding.autocode.trainer import AutocodeTrainer
        trainer = AutocodeTrainer(self.corpus, self.mock_embedder)
        self.classifiers = trainer.train()

    def test_compute_outliers_returns_results(self):
        from qualitative_coding.autocode.analytics import compute_outliers
        result = compute_outliers(self.corpus, self.mock_embedder, self.classifiers)
        self.assertIn("pace", result)
        self.assertIn("light", result)
        for items in result.values():
            for doc_id, line, confidence in items:
                self.assertIsInstance(confidence, float)
                self.assertGreaterEqual(confidence, 0.0)
                self.assertLessEqual(confidence, 1.0)

    def test_compute_cohesion_returns_results(self):
        from qualitative_coding.autocode.analytics import compute_cohesion
        result = compute_cohesion(self.corpus, self.mock_embedder)
        self.assertIn("pace", result)
        self.assertIn("light", result)
        for info in result.values():
            self.assertIn("examples", info)
            self.assertIn("variance_explained", info)
            self.assertIn("suggestion", info)

    def test_compute_similar_returns_list(self):
        from qualitative_coding.autocode.analytics import compute_similar
        pairs = compute_similar(self.corpus, self.mock_embedder, self.classifiers,
                                threshold=0.0)
        code_pairs = {(min(a, b), max(a, b)) for a, b, _, _ in pairs}
        self.assertIn(("light", "pace"), code_pairs)

    def test_compute_similar_threshold_filters(self):
        from qualitative_coding.autocode.analytics import compute_similar
        # Threshold above maximum possible probability — always empty
        pairs = compute_similar(self.corpus, self.mock_embedder, self.classifiers,
                                threshold=2.0)
        self.assertEqual(pairs, [])

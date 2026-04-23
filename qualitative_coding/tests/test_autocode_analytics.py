from tests.fixtures import QCTestCase
from unittest.mock import MagicMock, patch
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
                {"line": 3, "code_id": "light"},
                {"line": 4, "code_id": "light"},
                {"line": 5, "code_id": "light"},
            ])
        self.mock_embedder = make_mock_embedder(self.corpus)

    def test_compute_outliers_returns_results(self):
        from qualitative_coding.autocode.analytics import compute_outliers
        result = compute_outliers(self.corpus, self.mock_embedder)
        self.assertIn("pace", result)
        self.assertIn("light", result)
        for items in result.values():
            for doc_id, line, dist in items:
                self.assertIsInstance(dist, float)
                self.assertGreaterEqual(dist, 0)

    def test_compute_density_returns_results(self):
        from qualitative_coding.autocode.analytics import compute_density
        result = compute_density(self.corpus, self.mock_embedder)
        self.assertIn("pace", result)
        self.assertIn("light", result)
        for info in result.values():
            self.assertIn("examples", info)
            self.assertIn("mean_distance", info)
            self.assertIn("suggestion", info)

    def test_compute_similar_returns_list(self):
        from qualitative_coding.autocode.analytics import compute_similar
        # With random embeddings and threshold=0 all pairs should appear
        pairs = compute_similar(self.corpus, self.mock_embedder, threshold=0.0)
        # Should have at least one pair (pace, light)
        code_pairs = {(min(a, b), max(a, b)) for a, b, _ in pairs}
        self.assertIn(("light", "pace"), code_pairs)

    def test_compute_similar_threshold_filters(self):
        from qualitative_coding.autocode.analytics import compute_similar
        # Very high threshold should return empty list (random vectors unlikely to be similar)
        pairs = compute_similar(self.corpus, self.mock_embedder, threshold=0.999)
        self.assertEqual(pairs, [])

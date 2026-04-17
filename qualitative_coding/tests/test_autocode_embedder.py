from tests.fixtures import QCTestCase
from unittest.mock import patch, MagicMock
from pathlib import Path
import numpy as np
import json

EMBED_DIM = 4


def make_mock_client(n_texts):
    """Return a mock OpenAI client that returns random float32 vectors."""
    mock_item = lambda i: MagicMock(embedding=[float(i)] * EMBED_DIM)
    mock_response = MagicMock()
    mock_response.data = [mock_item(i) for i in range(n_texts)]
    mock_client = MagicMock()
    mock_client.embeddings.create.return_value = mock_response
    return mock_client


class TestCorpusEmbedder(QCTestCase):
    def setUp(self):
        super().setUp()
        self.run_in_testpath("qc corpus import macbeth.txt --importer verbatim")
        from qualitative_coding.autocode.embedder import CorpusEmbedder
        self.embedder = CorpusEmbedder(self.corpus)

    def _mock_embed(self, n_texts=None):
        """Context manager that patches the API client."""
        corpus_path = self.corpus.corpus_dir / "macbeth.txt"
        actual_n = sum(
            1 for line in corpus_path.read_text().splitlines() if line.strip()
        )
        n = n_texts if n_texts is not None else actual_n
        mock_client = make_mock_client(n)
        return patch.object(self.embedder, "_client", return_value=mock_client)

    def test_embed_creates_cache_files(self):
        with self._mock_embed():
            self.embedder.embed_corpus()
        self.assertTrue(self.embedder.cache_path("macbeth.txt").exists())
        self.assertTrue(self.embedder.sidecar_path("macbeth.txt").exists())

    def test_embed_sidecar_has_correct_fields(self):
        with self._mock_embed():
            self.embedder.embed_corpus()
        sidecar = json.loads(self.embedder.sidecar_path("macbeth.txt").read_text())
        self.assertIn("model", sidecar)
        self.assertIn("window", sidecar)
        self.assertIn("hash", sidecar)
        self.assertIn("lines", sidecar)

    def test_embed_npy_has_correct_shape(self):
        with self._mock_embed():
            self.embedder.embed_corpus()
        matrix, lines = self.embedder.get_embeddings("macbeth.txt")
        self.assertEqual(matrix.shape[1], EMBED_DIM)
        self.assertEqual(len(lines), matrix.shape[0])

    def test_cache_valid_after_embed(self):
        self.assertFalse(self.embedder.is_cache_valid("macbeth.txt"))
        with self._mock_embed():
            self.embedder.embed_corpus()
        self.assertTrue(self.embedder.is_cache_valid("macbeth.txt"))

    def test_cache_invalid_after_invalidate(self):
        with self._mock_embed():
            self.embedder.embed_corpus()
        self.embedder.invalidate("macbeth.txt")
        self.assertFalse(self.embedder.is_cache_valid("macbeth.txt"))

    def test_embed_skips_valid_cache(self):
        with self._mock_embed() as mock_ctx:
            self.embedder.embed_corpus()
            call_count_1 = mock_ctx.return_value.embeddings.create.call_count
        with self._mock_embed() as mock_ctx:
            self.embedder.embed_corpus()
            call_count_2 = mock_ctx.return_value.embeddings.create.call_count
        # Second run should make no API calls
        self.assertEqual(call_count_2, 0)

    def test_force_re_embeds(self):
        with self._mock_embed() as mock_ctx:
            self.embedder.embed_corpus()
            first = mock_ctx.return_value.embeddings.create.call_count
        with self._mock_embed() as mock_ctx:
            self.embedder.embed_corpus(force=True)
            second = mock_ctx.return_value.embeddings.create.call_count
        self.assertGreater(second, 0)

    def test_cache_invalidated_by_model_change(self):
        with self._mock_embed():
            self.embedder.embed_corpus()
        self.embedder.model = "different-model"
        self.assertFalse(self.embedder.is_cache_valid("macbeth.txt"))

    def test_cache_invalidated_by_window_change(self):
        with self._mock_embed():
            self.embedder.embed_corpus()
        self.embedder.window_before = 99
        self.assertFalse(self.embedder.is_cache_valid("macbeth.txt"))

    def test_windowed_text_uses_context(self):
        """Verify that the windowed text passed to the API includes context lines."""
        captured_texts = []
        corpus_path = self.corpus.corpus_dir / "macbeth.txt"
        lines = corpus_path.read_text().splitlines()
        non_blank = [l for l in lines if l.strip()]
        n = len(non_blank)
        mock_client = make_mock_client(n)

        def capture_call(model, input):
            captured_texts.extend(input)
            return mock_client.embeddings.create.return_value

        mock_client.embeddings.create.side_effect = capture_call
        with patch.object(self.embedder, "_client", return_value=mock_client):
            self.embedder.embed_corpus()

        # The first non-blank line's embedding text should include context
        # (window_before=2, window_after=2 by default; line 0 has no preceding context)
        self.assertGreater(len(captured_texts), 0)
        # A windowed text should contain newlines when window > 0
        multi_line = [t for t in captured_texts if "\n" in t]
        self.assertGreater(len(multi_line), 0)

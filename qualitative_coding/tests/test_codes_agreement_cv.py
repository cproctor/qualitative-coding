"""Test the cv metric for qc codes agreement."""
from tests.fixtures import QCTestCase
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from qualitative_coding.cli import cli
import numpy as np

EMBED_DIM = 8


def make_mock_embedder(corpus, n_lines=10):
    rng = np.random.default_rng(42)
    matrix = rng.random((n_lines, EMBED_DIM), dtype=np.float32)
    line_numbers = list(range(n_lines))
    mock = MagicMock()
    mock.get_embeddings.return_value = (matrix, line_numbers)
    mock.ensure_embedded.return_value = None
    mock.corpus = corpus
    return mock


class TestAgreementCV(QCTestCase):
    def setUp(self):
        super().setUp()
        self.run_in_testpath("qc corpus import macbeth.txt --importer verbatim")
        # 5+ examples per code for training
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
        self.runner = CliRunner()
        self.settings_path = str(self.testpath / "settings.yaml")

    def test_cv_metric_runs(self):
        mock_embedder = make_mock_embedder(self.corpus)
        with patch(
            "qualitative_coding.autocode.embedder.CorpusEmbedder",
            return_value=mock_embedder,
        ):
            result = self.runner.invoke(cli, [
                "codes", "agreement",
                "-c", "human",
                "--metric", "cv",
                "--folds", "2",
            ], env={"QC_SETTINGS": self.settings_path}, catch_exceptions=False)
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("pace", result.output)
        self.assertIn("Precision", result.output)
        self.assertIn("F1", result.output)

    def test_cv_skips_codes_with_few_examples(self):
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
                {"line": 0, "code_id": "rare"},  # only 1 example
            ])
        mock_embedder = make_mock_embedder(self.corpus)
        with patch(
            "qualitative_coding.autocode.embedder.CorpusEmbedder",
            return_value=mock_embedder,
        ):
            result = self.runner.invoke(cli, [
                "codes", "agreement",
                "-c", "human",
                "--metric", "cv",
                "--folds", "2",
            ], env={"QC_SETTINGS": self.settings_path}, catch_exceptions=False)
        self.assertIn("skipped", result.output)

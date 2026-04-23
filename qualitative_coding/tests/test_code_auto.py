"""Integration tests for qc code --auto and --auto --no-edit."""
from tests.fixtures import QCTestCase
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from qualitative_coding.cli import cli
import numpy as np

EMBED_DIM = 8


def make_mock_embedder(corpus, n_lines=10):
    """Return a mock CorpusEmbedder that serves synthetic embeddings."""
    rng = np.random.default_rng(7)
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
    mock.model = "test-model"
    mock.window_before = 2
    mock.window_after = 2
    return mock


class TestCodeAuto(QCTestCase):
    def setUp(self):
        super().setUp()
        self.run_in_testpath("qc corpus import macbeth.txt --importer verbatim")
        # Code only lines 0-7 (leaving lines 8-9 uncoded for autocode to predict on)
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
                # MACBETH also imported via moby_dick.md alias; only 10 lines exist
                # Using pace 5x and light 3x — trainer.min_examples defaults to 5
                # so only pace will train, which is enough for this test
            ])
        self.runner = CliRunner()
        self.settings_path = str(self.testpath / "settings.yaml")

    def _invoke(self, args):
        env = {"QC_SETTINGS": self.settings_path}
        return self.runner.invoke(cli, args, env=env, catch_exceptions=False)

    def test_no_edit_requires_auto(self):
        result = self.run_in_testpath("qc code chris --no-edit")
        self.assertNotEqual(result.returncode, 0)

    def test_auto_no_edit_writes_predictions(self):
        mock_embedder = make_mock_embedder(self.corpus)
        with patch(
            "qualitative_coding.autocode.embedder.CorpusEmbedder",
            return_value=mock_embedder,
        ):
            result = self._invoke([
                "code", "autocode",
                "--auto", "--no-edit",
                "-c", "human",
            ])
        self.assertEqual(result.exit_code, 0, result.output)
        with self.corpus.session():
            counts = self.corpus.count_codes(coders=["autocode"])
        self.assertGreater(sum(counts.values()), 0)

    def test_auto_no_edit_respects_only_uncoded(self):
        mock_embedder = make_mock_embedder(self.corpus)
        with patch(
            "qualitative_coding.autocode.embedder.CorpusEmbedder",
            return_value=mock_embedder,
        ):
            self._invoke([
                "-s", self.settings_path,
                "code", "autocode",
                "--auto", "--no-edit",
                "-c", "human",
            ])
        with self.corpus.session():
            human_lines = set(
                cl[2] for cl in self.corpus.get_coded_lines(coders=["human"])
            )
            auto_lines = set(
                cl[2] for cl in self.corpus.get_coded_lines(coders=["autocode"])
            )
        # autocode should not have coded lines that human already coded
        self.assertEqual(auto_lines & human_lines, set())

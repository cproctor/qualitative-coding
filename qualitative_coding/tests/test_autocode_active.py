from tests.fixtures import QCTestCase
from unittest.mock import MagicMock
import numpy as np

EMBED_DIM = 8


class TestUncertaintySampler(QCTestCase):
    def setUp(self):
        super().setUp()
        self.run_in_testpath("qc corpus import macbeth.txt --importer verbatim")
        # Populate codebook
        with self.corpus.session():
            self.corpus.update_coded_lines("macbeth.txt", "human", [
                {"line": 0, "code_id": "pace"},
                {"line": 1, "code_id": "light"},
            ])

        # Mock predictor that returns controllable scores
        self.mock_predictor = MagicMock()
        # score_all_lines returns (doc_id, line, code, confidence)
        self.mock_predictor.score_all_lines.return_value = [
            ("macbeth.txt", 5, "pace", 0.9),   # high confidence → large margin
            ("macbeth.txt", 6, "pace", 0.55),  # near threshold → small margin
            ("macbeth.txt", 6, "light", 0.45), # near threshold → small margin
            ("macbeth.txt", 7, "pace", 0.8),
            ("macbeth.txt", 8, "light", 0.7),
        ]
        self.mock_predictor.corpus = self.corpus

        from qualitative_coding.autocode.active import UncertaintySampler
        self.sampler = UncertaintySampler(self.corpus, self.mock_predictor)

    def test_rank_by_margin_returns_sorted_list(self):
        ranked = self.sampler.rank_by_margin()
        self.assertGreater(len(ranked), 0)
        # Should be sorted ascending by margin (most uncertain first)
        margins = [m for _, _, m in ranked]
        self.assertEqual(margins, sorted(margins))

    def test_rank_most_uncertain_first(self):
        ranked = self.sampler.rank_by_margin()
        # Line 6 has two codes at 0.55 and 0.45 → margin = 0.10 (most uncertain)
        # Line 5 has only pace at 0.9 → margin = 0.9 (most certain)
        doc, line, margin = ranked[0]
        self.assertEqual(line, 6)

    def test_rank_excludes_coded_by(self):
        ranked = self.sampler.rank_by_margin(exclude_coded_by=["human"])
        lines = [line for _, line, _ in ranked]
        # Human coded lines 0 and 1 — they should be excluded
        self.assertNotIn(0, lines)
        self.assertNotIn(1, lines)

    def test_rank_respects_code_filter(self):
        ranked = self.sampler.rank_by_margin(codes=["light"])
        # Only light codes should be in the ranking
        # Lines with only pace confidence should not appear unless they have light scores
        all_codes = set()
        for doc_id, line, margin in ranked:
            for d, l, c, conf in self.mock_predictor.score_all_lines.return_value:
                if d == doc_id and l == line:
                    all_codes.add(c)
        # Since we filtered to light, only lines with light scores remain
        self.assertTrue(all(
            any(c == "light" for d, l, c, conf
                in self.mock_predictor.score_all_lines.return_value
                if d == doc_id and l == line)
            for doc_id, line, _ in ranked
        ))

    def test_get_context_returns_window(self):
        context = self.sampler.get_context("macbeth.txt", 5, context_lines=2)
        self.assertGreater(len(context), 0)
        lines = [ln for ln, text, is_target in context]
        self.assertIn(5, lines)
        # Target line should be marked
        targets = [is_target for ln, text, is_target in context if ln == 5]
        self.assertTrue(any(targets))

    def test_get_context_respects_document_boundaries(self):
        # Line 0 is at the start — context should not go below 0
        context = self.sampler.get_context("macbeth.txt", 0, context_lines=5)
        lines = [ln for ln, text, is_target in context]
        self.assertGreaterEqual(min(lines), 0)

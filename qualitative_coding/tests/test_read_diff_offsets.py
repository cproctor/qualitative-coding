from difflib import unified_diff
from unittest import TestCase
from qualitative_coding.diff import read_diff_offsets

doc0 = [t + '\n' for t in 'abcdefghijklmnop']
doc1 = [t + '\n' for t in '1bcdef12lmnopqr']
diff = ''.join(unified_diff(doc0, doc1, n=1))

class TestReadDiffOffsets(TestCase):
    def test_read_diff_offsets_reads_correct_offsets(self):
        expected = [(9, -3), (17, 2)]
        observed = read_diff_offsets(diff)
        self.assertEqual(expected, observed)

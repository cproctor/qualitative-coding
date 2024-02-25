from unittest import TestCase
from qualitative_coding.tests.fixtures import MockCorpus
from qualitative_coding.views.viewer import QCCorpusViewer
from qualitative_coding.exceptions import CodeFileParseError

class TestCodeParsing(TestCase):
    def setUp(self):
        self.viewer = QCCorpusViewer(MockCorpus())

    def test_codes_are_validated(self):
        cases = [
            ['funny', True],
            ['funny-sort-of', True],
            ['FUNNY!', True],
            ['funny?', True],
            ['0', True],
            ['', False],
            [':colon', False],
            ['#hashtag', False],
        ]
        for code, ok in cases:
            if ok: 
                self.viewer.parse_code(code)
            else:
                with self.assertRaises(CodeFileParseError):
                    self.viewer.parse_code(code)

    def test_parses_valid_codes_file(self):
        self.viewer = QCCorpusViewer(MockCorpus())
        codes = self.viewer.parse_codes(CODES_FILE, 6)
        self.assertEqual(len(codes), 4)
        self.assertEqual(codes[0]['line'], 2)

    def test_checks_codes_file_length(self):
        self.viewer = QCCorpusViewer(MockCorpus())
        with self.assertRaises(CodeFileParseError):
            self.viewer.parse_codes(CODES_FILE, 7)

    def test_checks_for_misplaced_commas(self):
        for case in [TRAILING_COMMA, LEADING_COMMA]:
            with self.assertRaises(CodeFileParseError):
                self.viewer.parse_codes(case, 6)
            

CODES_FILE = """

funny, inappropriate
dull
trite

"""

TRAILING_COMMA = """
code,
"""
LEADING_COMMA = """
,code
"""



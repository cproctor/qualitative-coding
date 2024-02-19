from tests.fixtures import QCTestCase
from pathlib import Path
from qualitative_coding.corpus import QCCorpus

class TestCode(QCTestCase):
    def setUp(self):
        super().setUp()
        self.run_in_testpath("qc import macbeth.txt --importer verbatim")
        self.set_mock_editor(verbose=True)

    def test_code_applies_codes(self):
        self.run_in_testpath("qc code chris")
        with self.corpus.session():
            code_counts = self.corpus.count_codes()
        self.assertEqual(code_counts.get('line'), 2)
        self.assertEqual(code_counts.get('one'), 1)
        self.assertFileDoesNotExist("codes.txt")

    # Waiting until code command is complete
    def XXX_test_code_saves_state_on_crash(self):
        self.set_mock_editor(verbose=True, crash=True)
        self.run_in_testpath("qc code chris", debug=True)
        self.assertFileExists("codes.txt")
        self.assertFileExists(".coding_session")

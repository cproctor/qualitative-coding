from tests.fixtures import QCTestCase
from pathlib import Path
from qualitative_coding.corpus import QCCorpus

class TestCode(QCTestCase):

    def setUp(self):
        super().setUp()
        self.run_in_testpath("qc corpus import macbeth.txt --importer verbatim")
        self.set_mock_editor(verbose=True)

    def test_code_applies_codes(self):
        self.run_in_testpath("qc code chris")
        with self.corpus.session():
            code_counts = self.corpus.count_codes()
        self.assertEqual(code_counts.get('line'), 2)
        self.assertEqual(code_counts.get('one'), 1)
        self.assertFileDoesNotExist("codes.txt")

    def test_code_saves_state_on_crash(self):
        self.set_mock_editor(verbose=True, crash=True)
        self.run_in_testpath("qc code chris")
        self.assertFileExists("codes.txt")
        self.assertFileExists(".coding_session")

    def test_code_recovers_incomplete_session(self):
        self.set_mock_editor(verbose=True, crash=True)
        self.run_in_testpath("qc code chris")
        self.set_mock_editor(verbose=True)
        self.run_in_testpath("qc code chris --recover")
        self.assertFileDoesNotExist("codes.txt")
        self.assertFileDoesNotExist(".coding_session")
        result = self.run_in_testpath("qc codes list")
        self.assertTrue("line" in result.stdout)
        self.assertTrue("one" in result.stdout)
        self.assertTrue("two" in result.stdout)

    def test_code_will_not_code_when_metadata_file_exists(self):
        (self.testpath / ".coding_session").write_text('a')
        self.set_mock_editor(verbose=True)
        result = self.run_in_testpath("qc code chris")
        self.assertNotEqual(result.returncode, 0)

    def test_code_will_not_code_when_codes_exists(self):
        (self.testpath / "codes.txt").write_text('a')
        self.set_mock_editor(verbose=True)
        result = self.run_in_testpath("qc code chris")
        self.assertNotEqual(result.returncode, 0)

    def test_code_abandon_deletes_session(self):
        (self.testpath / ".coding_session").write_text('a')
        (self.testpath / "codes.txt").write_text('a')
        result = self.run_in_testpath("qc code chris --abandon")






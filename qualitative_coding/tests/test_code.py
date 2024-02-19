from tests.fixtures import QCTestCase
from pathlib import Path
from qualitative_coding.corpus import QCCorpus

class TestCode(QCTestCase):
    def setUp(self):
        super().setUp()
        self.run_in_testpath("qc import macbeth.txt --importer verbatim")
        self.set_editor(verbose=True)

    def test_code_applies_codes(self):
        self.run_in_testpath("qc code chris")
        with self.corpus.session():
            code_counts = self.corpus.count_codes()
        self.assertEqual(code_counts.get('line'), 2)
        self.assertEqual(code_counts.get('one'), 1)
        self.assertFileDoesNotExist("codes.txt")

    def test_code_saves_state_on_crash(self):
        self.set_editor(verbose=True, crash=True)
        self.run_in_testpath("qc code chris", debug=True)
        self.assertFileExists("codes.txt")
        self.assertFileExists(".coding_session")

    def set_editor(self, verbose=False, crash=False):
        """Updates settings['editor'] to the mock editor.
        Also reinitializes corpus.
        """
        mock_editor_path = str(Path("tests/mock_editor.py").resolve())
        command = mock_editor_path + ' "{corpus_file_path}" "{codes_file_path}"'
        if verbose: 
            command += " --verbose"
        if crash: 
            command += " --crash"
        self.update_settings("editor", command)
        self.corpus = QCCorpus(self.testpath / "settings.yaml")




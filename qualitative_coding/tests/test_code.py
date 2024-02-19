from tests.fixtures import QCTestCase
from pathlib import Path
from qualitative_coding.corpus import QCCorpus

class TestCode(QCTestCase):
    def setUp(self):
        super().setUp()
        self.run_in_testpath("qc import macbeth.txt --importer verbatim")
        self.update_settings("editor", 
                './tests/mock_editor.py "{corpus_file_path}" "{codes_file_path}"')
        self.corpus = QCCorpus(self.testpath / "settings.yaml")

    def test_codes_applied(self):
        self.run_in_testpath("qc code chris", debug=True)
        with self.corpus.session():
            codes = self.corpus.get_codes()
        print(codes)


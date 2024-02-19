from tests.fixtures import QCTestCase
from pathlib import Path
from qualitative_coding.corpus import QCCorpus

class TestCode(QCTestCase):
    def setUp(self):
        super().setUp()
        self.run_in_testpath("qc import macbeth.txt --importer verbatim")
        mock_editor_path = Path("tests/mock_editor.py").resolve()
        self.update_settings("editor", 
                str(mock_editor_path) + ' "{corpus_file_path}" "{codes_file_path}" --verbose')
        self.corpus = QCCorpus(self.testpath / "settings.yaml")

    def test_codes_applied(self):
        self.run_in_testpath("qc code chris")
        with self.corpus.session():
            code_counts = self.corpus.count_codes()
        self.assertEqual(code_counts.get('line'), 2)
        self.assertEqual(code_counts.get('one'), 1)


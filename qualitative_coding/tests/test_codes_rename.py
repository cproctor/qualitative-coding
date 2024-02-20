from tests.fixtures import QCTestCase
from qualitative_coding.corpus import QCCorpus
import yaml

class TestRename(QCTestCase):
    def setUp(self):
        super().setUp()
        self.run_in_testpath("qc corpus import macbeth.txt --importer verbatim")
        self.set_mock_editor()
        self.run_in_testpath("qc code chris")

    def test_rename_renames_codes(self):
        self.run_in_testpath("qc codes rename line pace")
        cb = yaml.safe_load((self.testpath / "codebook.yaml").read_text())
        self.assertTrue('pace' in cb)

    def test_rename_does_not_duplicate_codes(self):
        corpus = QCCorpus(self.testpath/"settings.yaml")
        self.run_in_testpath("qc codes rename line one")
        with corpus.session():
            self.assertEqual(len(corpus.get_coded_lines()), 3)

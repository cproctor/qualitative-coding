from tests.fixtures import QCTestCase
import yaml

class TestCodebook(QCTestCase):
    def test_codebook_is_empty_on_init(self):
        cb = yaml.safe_load((self.testpath / "codebook.yaml").read_text())
        self.assertEqual(cb, None)

    def test_codebook_updates_codebook_file(self):
        self.run_in_testpath("qc corpus import macbeth.txt --importer verbatim")
        self.set_mock_editor()
        self.run_in_testpath("qc code chris")
        self.run_in_testpath("qc codebook")
        cb = yaml.safe_load((self.testpath / "codebook.yaml").read_text())
        self.assertEqual(len(cb), 3)




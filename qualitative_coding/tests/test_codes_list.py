from tests.fixtures import QCTestCase
import yaml

class TestList(QCTestCase):
    def setUp(self):
        super().setUp()
        self.run_in_testpath("qc corpus import macbeth.txt --importer verbatim")
        self.set_mock_editor()
        self.run_in_testpath("qc code chris")
        code_tree = [{'line': ['one', 'two']}]
        (self.testpath / "codebook.yaml").write_text(yaml.dump(code_tree))

    def test_find_shows_codes(self):
        result = self.run_in_testpath("qc codes list")
        self.assertTrue("line" in result.stdout)
        self.assertTrue("one" in result.stdout)
        self.assertTrue("two" in result.stdout)

    def test_find_respects_depth(self):
        result = self.run_in_testpath("qc codes list --depth 1")
        self.assertTrue("line" in result.stdout)
        self.assertTrue("one" not in result.stdout)

    def test_find_respects_expanded(self):
        result = self.run_in_testpath("qc codes list --expanded")
        self.assertTrue("line:one" in result.stdout)




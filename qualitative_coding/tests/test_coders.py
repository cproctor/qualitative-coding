from tests.fixtures import QCTestCase
from pathlib import Path

class TestCoders(QCTestCase):
    def test_coders_shows_coders(self):
        self.run_in_testpath("qc corpus import macbeth.txt --importer verbatim")
        self.set_mock_editor()
        self.run_in_testpath("qc code chris")
        self.run_in_testpath("qc code varun")
        result = self.run_in_testpath("qc coders")
        self.assertTrue("chris" in result.stdout)
        self.assertTrue("varun" in result.stdout)

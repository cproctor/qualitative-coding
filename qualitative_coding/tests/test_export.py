from qualitative_coding.tests.fixtures import QCTestCase
from pathlib import Path

class TestExport(QCTestCase):
    def test_creates_qdpx_file(self):
        self.run_in_testpath("qc corpus import macbeth.txt")
        self.set_mock_editor(verbose=True)
        self.run_in_testpath("qc code chris")
        self.run_in_testpath("qc code haley")
        self.run_in_testpath("qc export out.qdpx")
        self.assertFileExists("out.qdpx")

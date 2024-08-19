from tests.fixtures import QCTestCase
from pathlib import Path

class TestCorpusRemove(QCTestCase):
    def test_removes_individual_file(self):
        self.run_in_testpath("qc corpus import macbeth.txt --importer verbatim")
        self.run_in_testpath("qc corpus remove corpus/macbeth.txt")
        self.assertFileDoesNotExist(self.testpath / "corpus" / "macbeth.txt")

    def test_removes_directories(self):
        self.run_in_testpath("qc corpus import macbeth.txt --importer verbatim --corpus-root shx")
        self.run_in_testpath("qc corpus remove corpus/shx --recursive")
        self.assertFileDoesNotExist(self.testpath / "corpus" / "shx" / "macbeth.txt")

from tests.fixtures import QCTestCase
from pathlib import Path

class TestCorpusMove(QCTestCase):

    def test_move_works_with_files(self):
        self.run_in_testpath("qc corpus import macbeth.txt --importer verbatim")
        self.run_in_testpath("qc corpus move corpus/macbeth.txt corpus/m.txt")
        self.assertTrue((self.testpath / "corpus" / "m.txt").exists())
        with self.corpus.session():
            result = self.corpus.get_documents(file_list=["m.txt"])
        self.assertEqual(result[0].file_path, "m.txt")

    def test_move_works_with_files_in_subdirs(self):
        self.run_in_testpath("qc corpus import macbeth.txt --importer verbatim")
        self.run_in_testpath("qc corpus move corpus/macbeth.txt corpus/will/macbeth.txt")
        self.assertTrue((self.testpath / "corpus" / "will" / "macbeth.txt").exists())
        with self.corpus.session():
            result = self.corpus.get_documents(file_list=["will/macbeth.txt"])
        self.assertEqual(result[0].file_path, "will/macbeth.txt")

    def test_move_works_with_recursive_subdirs(self):
        self.run_in_testpath("qc corpus import macbeth.txt --importer verbatim --corpus-root shakespeare")
        self.run_in_testpath("qc corpus move corpus/shakespeare corpus/will --recursive")
        self.assertTrue((self.testpath / "corpus" / "will" / "macbeth.txt").exists())
        with self.corpus.session():
            result = self.corpus.get_documents(file_list=["will/macbeth.txt"])
        self.assertEqual(result[0].file_path, "will/macbeth.txt")

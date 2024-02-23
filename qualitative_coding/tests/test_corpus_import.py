from tests.fixtures import QCTestCase
from pathlib import Path

class TestImport(QCTestCase):
    def test_import_verbatim(self):
        self.run_in_testpath("qc corpus import macbeth.txt --importer verbatim")
        self.assertFileImported("macbeth.txt")

    def test_import_pandoc(self):
        self.run_in_testpath("qc corpus import moby_dick.md --importer pandoc")
        self.assertFileImported("moby_dick.txt")
        nlines = len((self.testpath / "corpus/moby_dick.txt").read_text().split('\n'))
        self.assertEqual(nlines, 5)

    def test_import_recursive(self):
        (self.testpath / "chapters").mkdir()
        (self.testpath / "chapters/one.txt").write_text("one")
        (self.testpath / "chapters/two.txt").write_text("two")
        self.run_in_testpath("qc corpus import chapters --recursive")
        self.assertFileImported("chapters/one.txt")
        self.assertFileImported("chapters/two.txt")

    def assertFileImported(self, path):
        self.assertFileExists(Path("corpus") / path)
        with self.corpus.session():
            file_path = self.corpus.get_document(path).file_path
        self.assertEqual(file_path, path)

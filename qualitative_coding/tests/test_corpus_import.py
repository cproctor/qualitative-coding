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
        (self.testpath / "chapters" / "preface").mkdir()
        (self.testpath / "chapters/preface/note.txt").write_text("two")
        self.run_in_testpath("qc corpus import chapters --recursive")
        self.assertFileImported("one.txt")
        self.assertFileImported("preface/note.txt")

    def test_import_from_absolute_dir(self):
        import_path = (self.testpath / "macbeth.txt").resolve()
        self.run_in_testpath(f"qc corpus import {import_path}")
        self.assertFileImported("macbeth.txt")

    def test_import_recursive_from_absolute_dir(self):
        (self.testpath / "chapters").mkdir()
        (self.testpath / "chapters/one.txt").write_text("one")
        (self.testpath / "chapters" / "preface").mkdir()
        (self.testpath / "chapters/preface/note.txt").write_text("two")
        import_dir = (self.testpath / "chapters").resolve()
        self.run_in_testpath(f"qc corpus import {import_dir} --recursive")
        self.assertFileImported("one.txt")
        self.assertFileImported("preface/note.txt")

    def test_import_from_rel_dir_with_dot_dot(self):
        (self.testpath / "chapters").mkdir()
        self.run_in_testpath("qc corpus import chapters/../macbeth.txt --importer verbatim")
        self.assertFileImported("macbeth.txt")

    def test_import_from_dir_with_spaces(self):
        (self.testpath / "chap ters").mkdir()
        (self.testpath / "chap ters/one.txt").write_text("one")
        (self.testpath / "chap ters" / "preface").mkdir()
        (self.testpath / "chap ters/preface/note.txt").write_text("two")
        self.run_in_testpath('qc corpus import "chap ters" --recursive')
        self.assertFileImported("one.txt")
        self.assertFileImported("preface/note.txt")

    def assertFileImported(self, path):
        self.assertFileExists(Path("corpus") / path)
        with self.corpus.session():
            file_path = self.corpus.get_document(self.testpath / 'corpus' / path).file_path
        self.assertEqual(file_path, path)

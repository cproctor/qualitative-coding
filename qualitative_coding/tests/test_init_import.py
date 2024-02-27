from qualitative_coding.tests.fixtures import QCTestCase
from qualitative_coding.corpus import QCCorpus
from tempfile import TemporaryDirectory
from pathlib import Path
from subprocess import run

class TestInitImport(QCTestCase):
    def test_imports_from_qdpx_file(self):
        """Sort of an elaborate test: exports and then re-imports a project.
        """
        self.run_in_testpath("qc corpus import macbeth.txt")
        self.set_mock_editor(verbose=True)
        self.run_in_testpath("qc code chris")
        self.run_in_testpath("qc code haley")
        self.run_in_testpath("qc export out.qdpx")
        self.assertFileExists("out.qdpx")
        with TemporaryDirectory() as outdir:
            qdxp_file = self.testpath / "out.qdpx"
            result = run(f'qc init --import "{qdxp_file}"', cwd=outdir, shell=True, 
                    check=True, capture_output=True, text=True)
            corpus = QCCorpus(Path(outdir) / "settings.yaml")
            self.assertFileExists(Path(outdir) / "corpus" / "macbeth.txt")
            with corpus.session():
                self.assertEqual(len(corpus.get_codes()), 3)
                self.assertEqual(len(list(corpus.get_all_coders())), 2)
                self.assertEqual(len(corpus.get_coded_lines()), 6)


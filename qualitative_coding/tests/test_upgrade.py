from tests.fixtures import QCTestCase
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.logs import configure_logger

class TestUpgrade(QCTestCase):
    def setUp(self):
        pass

    def test_upgrade_noop(self):
        self.set_up_qc_project()
        result = self.run_in_testpath("qc upgrade")
        self.assertEqual(result.stdout, "")

    def test_upgrade_0_2_3_to_1_0_0(self):
        self.set_up_qc_project_0_2_3()
        configure_logger(self.testpath / "settings.yaml")
        result = self.run_in_testpath("qc upgrade -v 1.0.0")
        corpus = QCCorpus(self.testpath / "settings.yaml")
        self.assertFileDoesNotExist("codes")
        with corpus.session():
            code_counts = corpus.count_codes()
        self.assertEqual(code_counts['prolepsis'], 3)

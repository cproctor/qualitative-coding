from tests.fixtures import QCTestCase
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.logs import configure_logger
import yaml

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

    def read_settings(self):
        return yaml.safe_load((self.testpath / "settings.yaml").read_text())

    def test_upgrade_1_4_0_to_2_0_0_nests_autocode_settings(self):
        self.set_up_qc_project()
        self.update_settings('qc_version', '1.4.0')
        self.update_settings('autocode', None)
        self.update_settings('autocode_min_examples', 7)
        self.update_settings('autocode_api_key', 'sk-test')
        self.run_in_testpath("qc upgrade -v 2.0.0")
        settings = self.read_settings()
        self.assertEqual(settings['qc_version'], '2.0.0')
        self.assertEqual(settings['autocode']['min_examples'], 7)
        self.assertEqual(settings['autocode']['api_key'], 'sk-test')
        self.assertNotIn('autocode_min_examples', settings)
        self.assertNotIn('autocode_api_key', settings)

    def test_upgrade_1_4_0_to_2_0_0_creates_empty_autocode_table_when_unused(self):
        self.set_up_qc_project()
        self.update_settings('qc_version', '1.4.0')
        self.update_settings('autocode', None)
        self.run_in_testpath("qc upgrade -v 2.0.0")
        settings = self.read_settings()
        self.assertEqual(settings['autocode'], {})

    def test_revert_2_0_0_to_1_4_0_restores_flat_autocode_settings(self):
        self.set_up_qc_project()
        self.update_settings('autocode', {'min_examples': 7})
        self.run_in_testpath("qc upgrade -v 1.4.0")
        settings = self.read_settings()
        self.assertEqual(settings['qc_version'], '1.4.0')
        self.assertEqual(settings['autocode_min_examples'], 7)
        self.assertNotIn('autocode', settings)

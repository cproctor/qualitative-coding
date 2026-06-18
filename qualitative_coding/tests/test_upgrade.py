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

    def test_settings_missing_unit_does_not_hard_error(self):
        # Simulates a project left at qc_version 1.4.0 before 'unit' was
        # added to DEFAULT_SETTINGS; such projects are out of date rather
        # than invalid, and should be told to run `qc upgrade`.
        self.set_up_qc_project()
        self.update_settings('qc_version', '1.4.0')
        self.update_settings('unit', None)
        result = self.run_in_testpath("qc codes stats")
        self.assertNotIn("Expected 'unit' in settings", result.stderr)

    def test_upgrade_1_4_0_to_1_4_1_adds_unit(self):
        self.set_up_qc_project()
        self.update_settings('qc_version', '1.4.0')
        self.update_settings('unit', None)
        self.run_in_testpath("qc upgrade -v 1.4.1")
        settings = yaml.safe_load((self.testpath / "settings.yaml").read_text())
        self.assertEqual(settings['unit'], 'line')
        self.assertEqual(settings['qc_version'], '1.4.1')
        result = self.run_in_testpath("qc codes stats")
        self.assertEqual(result.returncode, 0)

from tests.fixtures import QCTestCase
import yaml
from qualitative_coding.exceptions import QCError

class TestInit(QCTestCase):
    def test_init_creates_setup_file(self):
        self.assertFileExists(self.testpath / "settings.yaml")

    def test_init_settings_has_expected_default_params(self):
        settings = yaml.safe_load((self.testpath / "settings.yaml").read_text())
        self.assertEqual(settings['qc_version'], '1.0.0')

    def test_init2_creates_expected_dirs(self):
        self.update_settings("logs_dir", "logz")
        self.run_in_testpath("qc init")
        self.assertDirExists("corpus")
        self.assertDirExists("memos")
        self.assertDirExists("logz")

    def test_init2_creates_db(self):
        self.run_in_testpath("qc init")
        self.assertFileExists('qualitative_coding.sqlite3')

    def test_init_check_catches_errors(self):
        result = self.run_in_testpath("qc init")
        self.assertEqual("", result.stderr)
        self.update_settings("corpus_dir", None)
        result = self.run_in_testpath("qc init")
        self.assertNotEqual("", result.stderr)

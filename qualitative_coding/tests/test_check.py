from tests.fixtures import QCTestCase
from pathlib import Path
from qualitative_coding.corpus import DEFAULT_SETTINGS

class TestCode(QCTestCase):
    def test_check_passes_when_no_errors(self):
        result = self.run_in_testpath("qc check")
        self.assertEqual(result.stdout, "")

    def test_check_identifies_missing_settings(self):
        for setting in DEFAULT_SETTINGS:
            self.update_settings(setting, None)
            message = self.run_in_testpath("qc check").stderr
            self.assertTrue(f"Expected '{setting}' in settings" in message)




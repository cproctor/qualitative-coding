from tests.fixtures import QCTestCase
from logs import configure_logger
import structlog
from pathlib import Path

class TestLogs(QCTestCase):
    def test_log_info_saves_to_file(self):
        configure_logger(self.testpath / "settings.yaml")
        log = structlog.get_logger()
        log.info("test")
        self.assertFileExists("qc.log")
        with open(self.testpath / "qc.log") as fh:
            lines = list(fh)
        self.assertTrue(len(lines) > 0)

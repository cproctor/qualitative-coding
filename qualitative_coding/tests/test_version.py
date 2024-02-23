from tests.fixtures import QCTestCase
from importlib.metadata import metadata

class TestVersion(QCTestCase):
    def test_version_is_correct(self):
        version = metadata('qualitative-coding')['version']
        result = self.run_in_testpath("qc version")
        self.assertTrue(version in result.stdout)



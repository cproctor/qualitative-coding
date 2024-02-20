from tests.fixtures import QCTestCase

class TestVersion(QCTestCase):
    def test_version_is_correct(self):
        result = self.run_in_testpath("qc version")
        self.assertTrue("1.0.0" in result.stdout)



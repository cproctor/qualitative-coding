from tests.fixtures import QCTestCase

class TestUpgrade(QCTestCase):
    def setUp(self):
        pass

    def test_upgrade_noop(self):
        self.set_up_qc_project()
        result = self.run_in_testpath("qc upgrade")
        self.assertEqual(result.stdout, "")

    def test_upgrade_0_2_3_to_1_0_0(self):
        self.set_up_qc_project_0_2_3()
        result = self.run_in_testpath("qc upgrade")
        self.assertEqual(result.stdout.strip(), "Applying migration 1.0.0")



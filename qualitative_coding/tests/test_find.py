from tests.fixtures import QCTestCase

class TestFind(QCTestCase):
    def setUp(self):
        super().setUp()
        self.run_in_testpath("qc import macbeth.txt --importer verbatim")
        self.set_mock_editor()
        self.run_in_testpath("qc code chris")
        self.run_in_testpath("qc codebook")

    def test_find_shows_codes(self):
        result = self.run_in_testpath("qc find one")
        self.assertEqual(len(result.stdout.splitlines()), 9)

    def test_find_respects_context_window(self):
        result = self.run_in_testpath("qc find one -C 5")
        self.assertEqual(len(result.stdout.splitlines()), 12)



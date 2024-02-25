from tests.fixtures import QCTestCase

class TestFind(QCTestCase):
    def setUp(self):
        super().setUp()
        self.run_in_testpath("qc corpus import macbeth.txt --importer verbatim")
        self.set_mock_editor()
        self.run_in_testpath("qc code chris")

    def test_find_shows_codes(self):
        result = self.run_in_testpath("qc codes find one")
        self.assertEqual(len(result.stdout.splitlines()), 8)

    def test_find_respects_context_window(self):
        result = self.run_in_testpath("qc codes find one -C 5")
        self.assertEqual(len(result.stdout.splitlines()), 11)



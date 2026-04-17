from tests.fixtures import QCTestCase

class TestCoders(QCTestCase):
    def setUp(self):
        super().setUp()
        self.run_in_testpath("qc corpus import macbeth.txt --importer verbatim")
        with self.corpus.session():
            self.corpus.update_coded_lines(
                "macbeth.txt", "chris",
                [{"line": 0, "code_id": "pace"}, {"line": 1, "code_id": "light"}],
            )
            self.corpus.update_coded_lines(
                "macbeth.txt", "varun",
                [{"line": 0, "code_id": "pace"}],
            )

    def test_coders_shows_coders(self):
        result = self.run_in_testpath("qc coders")
        self.assertIn("chris", result.stdout)
        self.assertIn("varun", result.stdout)

    def test_coders_delete_removes_coder(self):
        self.run_in_testpath("qc coders delete chris")
        with self.corpus.session():
            coders = [c.name for c in self.corpus.get_all_coders()]
        self.assertNotIn("chris", coders)
        self.assertIn("varun", coders)

    def test_coders_delete_removes_coded_lines(self):
        self.run_in_testpath("qc coders delete chris")
        with self.corpus.session():
            counts = self.corpus.count_codes(coders=["chris"])
        self.assertEqual(sum(counts.values()), 0)

    def test_coders_delete_leaves_other_coders(self):
        self.run_in_testpath("qc coders delete chris")
        with self.corpus.session():
            counts = self.corpus.count_codes(coders=["varun"])
        self.assertTrue(sum(counts.values()) > 0)

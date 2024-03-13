from tests.fixtures import QCTestCase

class TestStats(QCTestCase):
    def test_stats_shows_stats(self):
        self.run_in_testpath("qc corpus import macbeth.txt --importer verbatim")
        self.set_mock_editor()
        self.run_in_testpath("qc code chris")
        result = self.run_in_testpath("qc codes stats --format tsv")
        table = self.read_stats_tsv(result.stdout)
        self.assertEqual(table['line']['Count'], 2)

    def test_stats_distinct_shows_distinct_coders(self):
        self.run_in_testpath("qc corpus import macbeth.txt --importer verbatim")
        self.set_mock_editor()
        self.run_in_testpath("qc code chris")
        self.run_in_testpath("qc code haley")
        result = self.run_in_testpath("qc codes stats --distinct --format tsv")
        table = self.read_stats_tsv(result.stdout)

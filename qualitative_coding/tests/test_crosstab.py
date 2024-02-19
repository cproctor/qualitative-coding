from tests.fixtures import QCTestCase
from pathlib import Path
from io import StringIO
import csv

class TestCrosstab(QCTestCase):
    def test_crosstab_shows_counts(self):
        self.run_in_testpath("qc import macbeth.txt --importer verbatim")
        self.set_mock_editor()
        self.run_in_testpath("qc code chris")
        self.run_in_testpath("qc codebook")
        result = self.run_in_testpath("qc crosstab one two line --format tsv")
        table = self.read_stats_tsv(result.stdout)
        self.assertEqual(table['two']['line'], 1)

    def test_crosstab_with_probs_shows_probs(self):
        self.run_in_testpath("qc import macbeth.txt --importer verbatim")
        self.set_mock_editor()
        self.run_in_testpath("qc code chris")
        self.run_in_testpath("qc codebook")
        result = self.run_in_testpath("qc crosstab one two line --probs --format tsv", debug=True)
        table = self.read_stats_tsv(result.stdout)
        self.assertEqual(table['line']['two'], 0.5)

    def read_stats_tsv(self, stdout):
        reader = csv.reader(StringIO(stdout), delimiter="\t")
        table = [[item.strip() for item in row] for row in reader]
        ix_name, *cols = table[0]
        parse = lambda val: None if val == '' else float(val)
        return {ix: dict(zip(cols, map(parse, vals))) for ix, *vals in table[1:]}


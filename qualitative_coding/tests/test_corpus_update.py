from tests.fixtures import QCTestCase
from qualitative_coding.corpus import QCCorpus

MACBETH_IMPROVED = """Tomorrow, and tomorrow, and tomorrow,
Tomorrow, and tomorrow, and tomorrow,
Tomorrow, and tomorrow, and tomorrow,
Creeps in this petty pace from day to day,
To the last syllable of recorded time;
The way to dusty death. Out, out, brief candle!
Life's but a walking shadow, a poor player,
Something something something,
Told by an idiot, full of sound and fury,
Signifying nothing.
"""

class TestCorpusUpdate(QCTestCase):
    def setUp(self):
        super().setUp()
        self.run_in_testpath("qc corpus import macbeth.txt --importer verbatim")
        with self.corpus.session():
            self.corpus.update_coded_lines("macbeth.txt", "chris", [
                {'line': 1, 'code_id': 'tomorrow'},
                {'line': 2, 'code_id': 'creeps'},
                {'line': 3, 'code_id': 'to'},
                {'line': 4, 'code_id': 'and'},
                {'line': 5, 'code_id': 'the'},
                {'line': 6, 'code_id': 'lifes'},
                {'line': 7, 'code_id': 'that'},
                {'line': 8, 'code_id': 'and'},
                {'line': 9, 'code_id': 'told'},
            ])
        (self.testpath / "macbeth_improved.txt").write_text(MACBETH_IMPROVED)

    def test_corpus_update_updates_line_numbers(self):
        before = self.run_in_testpath("qc codes find speech").stdout
        self.run_in_testpath("qc corpus update corpus/macbeth.txt --new macbeth_improved.txt")
        after = self.run_in_testpath("qc codes find speech").stdout
        self.assertEqual(before, after)

    def test_corpus_update_updates_text(self):
        self.run_in_testpath("qc corpus update corpus/macbeth.txt --new macbeth_improved.txt")
        text = (self.testpath / "corpus/macbeth.txt").read_text()
        self.assertEqual(text, MACBETH_IMPROVED)

    def test_corpus_update_updates_file_hash(self):
        with self.corpus.session():
            old_hash = self.corpus.get_document(self.testpath / "corpus/macbeth.txt").file_hash
        self.run_in_testpath("qc corpus update corpus/macbeth.txt --new macbeth_improved.txt")
        with self.corpus.session():
            new_hash = self.corpus.get_document(self.testpath / "corpus/macbeth.txt").file_hash
        self.assertNotEqual(old_hash, new_hash)




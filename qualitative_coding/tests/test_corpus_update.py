import json

from tests.fixtures import QCTestCase
from qualitative_coding.corpus import QCCorpus

PARAGRAPHS_DOC = """Paragraph one line one.

Paragraph two line one.
"""

PARAGRAPHS_DOC_WITH_NEW_FIRST_PARAGRAPH = """New paragraph zero.

Paragraph one line one.

Paragraph two line one.
"""

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


class TestCorpusUpdateReindexesParagraphs(QCTestCase):
    """Regression test: qc corpus update used to reindex CodedLine line numbers but never
    rebuild the "paragraphs" DocumentIndex's Location rows, leaving them stale relative to the
    new text. An edit that inserts a whole new paragraph before existing text shifts every later
    paragraph's line range; against the stale (unrebuilt) index, the reindexed coded line's new
    line number could fall outside every existing Location, and get_paragraph would raise QCError
    -- or, in cases where it accidentally still matched some Location, return the wrong
    paragraph's text.
    """
    def setUp(self):
        super().setUp()
        (self.testpath / "doc.txt").write_text(PARAGRAPHS_DOC)
        self.run_in_testpath("qc corpus import doc.txt --importer verbatim")
        with self.corpus.session():
            # Line 2 ("Paragraph two line one.") is the second (and last) paragraph.
            self.corpus.update_coded_lines("doc.txt", "chris", [
                {"line": 2, "code_id": "light"},
            ])
        (self.testpath / "doc_updated.txt").write_text(PARAGRAPHS_DOC_WITH_NEW_FIRST_PARAGRAPH)

    def test_update_rebuilds_stale_paragraph_index(self):
        result = self.run_in_testpath("qc corpus update corpus/doc.txt --new doc_updated.txt")
        self.assertEqual(result.returncode, 0, result.stderr)

        find_result = self.run_in_testpath("qc codes find light -n paragraph --json")
        self.assertEqual(find_result.returncode, 0, find_result.stderr)
        records = json.loads(find_result.stdout)
        self.assertEqual(len(records), 1)
        self.assertIn("Paragraph two line one.", records[0]["text"])
        self.assertNotIn("New paragraph zero.", records[0]["text"])

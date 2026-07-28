import json

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


class TestFindFormFeed(QCTestCase):
    """Regression test: str.splitlines() (used to validate a coded document's line count, in
    Viewer.open_editor) treats '\\x0c' (form feed -- a common PDF-extraction page-break artifact)
    as a line break, but the plain '\\n'-only file iteration `codes find` used to use for display
    did not. On any corpus text containing such a character, this silently desynced the line
    number a code was stored under from the line `codes find` displayed for it -- worse the
    further into the document the code was, since the drift is cumulative per occurrence.

    Fixture below has a '\\x0c' embedded inside what a '\\n'-only split would treat as a single
    line, splitting it into two lines by str.splitlines() count. The mock editor (see
    mock_editor.py, now also fixed to use .splitlines() for its own line count) codes the
    document's first two str.splitlines()-lines as "one" and "two" respectively. Before the fix,
    `codes find two` would show the *third* splitlines()-line's content (the line after the form
    feed's line-count inflation caught up); after the fix, it shows the correct second line.
    """
    def setUp(self):
        super().setUp()
        (self.testpath / "form_feed.txt").write_text(
            "First line\x0cSecond piece\nThird real line\n"
        )
        self.run_in_testpath("qc corpus import form_feed.txt --importer verbatim")
        self.set_mock_editor()
        self.run_in_testpath("qc code chris")

    def test_find_shows_correct_line_for_content_after_form_feed(self):
        result = self.run_in_testpath("qc codes find two --json -n line -B0 -C0")
        records = json.loads(result.stdout)
        self.assertEqual(len(records), 1)
        self.assertIn("Second piece", records[0]["text"])
        self.assertNotIn("Third real line", records[0]["text"])



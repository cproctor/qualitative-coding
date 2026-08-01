from tests.fixtures import QCTestCase

PARAGRAPHS_DOC = """Paragraph one line one.
Paragraph one line two.

Paragraph two line one.
Paragraph two line two.
"""

class TestAgreementUnits(QCTestCase):
    def setUp(self):
        super().setUp()
        (self.testpath / "doc.txt").write_text(PARAGRAPHS_DOC)
        self.run_in_testpath("qc corpus import doc.txt --importer verbatim")
        with self.corpus.session():
            # chris and varun code different lines within the same first
            # paragraph (lines 0 and 1), and never overlap on the second
            # paragraph (lines 3 and 4).
            self.corpus.update_coded_lines("doc.txt", "chris", [
                {"line": 0, "code_id": "pace"},
                {"line": 3, "code_id": "light"},
            ])
            self.corpus.update_coded_lines("doc.txt", "varun", [
                {"line": 1, "code_id": "pace"},
                {"line": 4, "code_id": "light"},
            ])

    def test_agreement_unit_defaults_to_line_from_settings(self):
        result = self.run_in_testpath(
            "qc codes agreement pace -c chris -c varun --metric kappa"
        )
        self.assertEqual(result.returncode, 0)
        line_level = result.stdout

        result = self.run_in_testpath(
            "qc codes agreement pace -c chris -c varun --metric kappa -n line"
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(line_level, result.stdout)

    def test_agreement_unit_paragraph_overrides_default(self):
        # At line granularity, chris and varun never code the same line, so
        # both lines look like disagreements.
        line_level = self.run_in_testpath(
            "qc codes agreement pace -c chris -c varun --metric alpha -n line"
        )
        self.assertEqual(line_level.returncode, 0)

        # At paragraph granularity, lines 0 and 1 fall in the same paragraph,
        # so chris and varun agree that the first paragraph contains "pace".
        paragraph_level = self.run_in_testpath(
            "qc codes agreement pace -c chris -c varun --metric alpha -n paragraph"
        )
        self.assertEqual(paragraph_level.returncode, 0)
        self.assertNotEqual(line_level.stdout, paragraph_level.stdout)

    def test_agreement_unit_setting_changes_default(self):
        self.update_settings("unit", "paragraph")
        explicit = self.run_in_testpath(
            "qc codes agreement pace -c chris -c varun --metric alpha -n paragraph"
        )
        default = self.run_in_testpath(
            "qc codes agreement pace -c chris -c varun --metric alpha"
        )
        self.assertEqual(explicit.returncode, 0)
        self.assertEqual(default.returncode, 0)
        self.assertEqual(explicit.stdout, default.stdout)

    def test_agreement_cv_rejects_explicit_unit(self):
        result = self.run_in_testpath(
            "qc codes agreement --metric cv -n document"
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--unit is not supported with --metric cv", result.stderr)


class TestAgreementFormFeed(QCTestCase):
    """Regression test: show_agreement's line-unit domain used to be built with
    `sum(1 for _ in open(path))`, plain file iteration that (unlike str.splitlines(), which is what
    CodedLine.line numbers are actually assigned against everywhere else) does not treat '\\x0c' (form
    feed) as a line break. On a document containing one, this undercounted the domain, silently
    dropping any coded line past the form feed from the reliability computation and undercounting the
    reported "Units" total.
    """
    def setUp(self):
        super().setUp()
        # Plain '\n'-only iteration sees 2 lines here ("First line\x0cSecond piece\n" as one line,
        # "Third real line\n" as the second); str.splitlines() correctly sees 3.
        (self.testpath / "form_feed.txt").write_text(
            "First line\x0cSecond piece\nThird real line\n"
        )
        self.run_in_testpath("qc corpus import form_feed.txt --importer verbatim")
        with self.corpus.session():
            self.corpus.update_coded_lines("form_feed.txt", "chris", [
                {"line": 2, "code_id": "pace"},
            ])
            self.corpus.update_coded_lines("form_feed.txt", "varun", [
                {"line": 2, "code_id": "pace"},
            ])

    def test_line_unit_domain_includes_line_after_form_feed(self):
        result = self.run_in_testpath(
            "qc codes agreement pace -c chris -c varun --metric alpha -n line"
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("3", result.stdout.splitlines()[-1].split())


class TestAgreement(QCTestCase):
    def setUp(self):
        super().setUp()
        self.run_in_testpath("qc corpus import macbeth.txt --importer verbatim")
        with self.corpus.session():
            # chris and varun agree on lines 0-2, disagree on line 3 (0-indexed)
            self.corpus.update_coded_lines("macbeth.txt", "chris", [
                {"line": 0, "code_id": "pace"},
                {"line": 1, "code_id": "pace"},
                {"line": 2, "code_id": "light"},
                {"line": 3, "code_id": "light"},
            ])
            self.corpus.update_coded_lines("macbeth.txt", "varun", [
                {"line": 0, "code_id": "pace"},
                {"line": 1, "code_id": "pace"},
                {"line": 2, "code_id": "light"},
                # varun does not code line 3
            ])

    def test_agreement_alpha_runs(self):
        result = self.run_in_testpath(
            "qc codes agreement -c chris -c varun --metric alpha"
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("pace", result.stdout)
        self.assertIn("light", result.stdout)
        self.assertIn("Alpha", result.stdout)

    def test_agreement_kappa_runs(self):
        result = self.run_in_testpath(
            "qc codes agreement -c chris -c varun --metric kappa"
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Kappa", result.stdout)

    def test_agreement_f1_runs(self):
        result = self.run_in_testpath(
            "qc codes agreement -c chris -c varun --metric f1"
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Precision", result.stdout)
        self.assertIn("Recall", result.stdout)
        self.assertIn("F1", result.stdout)

    def test_agreement_irr_alias(self):
        result = self.run_in_testpath(
            "qc codes irr -c chris -c varun --metric alpha"
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Alpha", result.stdout)

    def test_agreement_kappa_requires_two_coders(self):
        result = self.run_in_testpath(
            "qc codes agreement -c chris --metric kappa"
        )
        self.assertNotEqual(result.returncode, 0)

    def test_agreement_f1_requires_two_coders(self):
        result = self.run_in_testpath(
            "qc codes agreement -c chris --metric f1"
        )
        self.assertNotEqual(result.returncode, 0)

    def test_agreement_code_filter(self):
        result = self.run_in_testpath(
            "qc codes agreement pace -c chris -c varun --metric alpha"
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("pace", result.stdout)
        self.assertNotIn("light", result.stdout)

    def test_agreement_perfect_alpha_is_one(self):
        # Make varun's codes identical to chris's
        with self.corpus.session():
            self.corpus.update_coded_lines("macbeth.txt", "varun", [
                {"line": 0, "code_id": "pace"},
                {"line": 1, "code_id": "pace"},
                {"line": 2, "code_id": "light"},
                {"line": 3, "code_id": "light"},
            ])
        result = self.run_in_testpath(
            "qc codes agreement pace -c chris -c varun --metric alpha"
        )
        self.assertEqual(result.returncode, 0)
        # Perfect agreement — alpha should be 1 (displayed as "1" or "1.0")
        self.assertRegex(result.stdout, r"\b1\.?0?\b")

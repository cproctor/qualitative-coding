from tests.fixtures import QCTestCase

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

from tests.fixtures import QCTestCase
from subprocess import run
import yaml

class TestAutocodeCLI(QCTestCase):
    "Regression tests for qc autocode subcommand dispatch and qc autocode init"

    def test_autocode_help_lists_subcommands_and_hides_interactive(self):
        result = self.run_in_testpath("qc autocode --help")
        self.assertIn("init", result.stdout)
        self.assertIn("embed", result.stdout)
        commands_section = result.stdout.split("Commands:")[1]
        self.assertNotIn("interactive", commands_section)

    def test_autocode_subcommand_dispatch_is_not_swallowed_by_coder_argument(self):
        result = self.run_in_testpath("qc autocode embed --help")
        self.assertIn("Generate and cache embeddings", result.stdout)

    def test_autocode_coder_argument_still_dispatches_to_interactive_loop(self):
        result = self.run_in_testpath("qc autocode some_coder --help")
        self.assertIn("Interactively code the most uncertain lines", result.stdout)

    def test_autocode_init_writes_nested_settings(self):
        accept_all_defaults = "\n" * 9
        run(
            "qc autocode init", shell=True, cwd=self.testpath,
            input=accept_all_defaults, capture_output=True, text=True,
        )
        settings = yaml.safe_load((self.testpath / "settings.yaml").read_text())
        self.assertEqual(settings["autocode"]["min_examples"], 5)
        self.assertEqual(settings["autocode"]["window"], [2, 2])
        self.assertEqual(settings["autocode"]["confidence_threshold"], 0.6)

    def test_autocode_init_adds_embeddings_dir_to_gitignore(self):
        accept_all_defaults = "\n" * 9
        run(
            "qc autocode init", shell=True, cwd=self.testpath,
            input=accept_all_defaults, capture_output=True, text=True,
        )
        gitignore = (self.testpath / ".gitignore").read_text()
        self.assertIn("embeddings/", gitignore)

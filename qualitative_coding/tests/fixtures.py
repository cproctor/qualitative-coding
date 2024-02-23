from unittest import TestCase
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory
from qualitative_coding.corpus import QCCorpus
from io import StringIO
import yaml
import csv


class QCTestCase(TestCase):
    """A subclass of TestCase with methods for instantiating a QC project.
    """

    def setUp(self):
        self.set_up_qc_project()
        self.corpus = QCCorpus(self.testpath / "settings.yaml")

    def tearDown(self):
        self.tear_down_qc_project()

    def set_up_qc_project(self):
        self.tempdir = TemporaryDirectory()
        self.testpath = Path(self.tempdir.name)
        self.run_in_testpath("qc init")
        self.run_in_testpath("qc init")
        (self.testpath / "macbeth.txt").write_text(MACBETH)
        (self.testpath / "moby_dick.md").write_text(MOBY_DICK)

    def set_up_qc_project_0_2_3(self):
        self.tempdir = TemporaryDirectory()
        self.testpath = Path(self.tempdir.name)
        settings_0_2_3 = {
            'qc_version': "0.2.3",
            'corpus_dir': 'corpus',
            'codes_dir': 'codes',
            'logs_dir': 'logs',
            'memos_dir': 'memos',
            'codebook': 'codebook.yaml',
        }
        (self.testpath / "settings.yaml").write_text(yaml.dump(settings_0_2_3))
        for k, v in settings_0_2_3.items():
            if k.endswith("_dir"):
                (self.testpath / v).mkdir()
        (self.testpath / "codebook.yaml").touch()
        (self.testpath / "corpus" / "macbeth.txt").write_text(MACBETH)
        (self.testpath / "codes" / "macbeth.txt.cp.codes").write_text(MACBETH_CODES_0_2_3)

    def tear_down_qc_project(self):
        self.tempdir.cleanup()

    def run_in_testpath(self, command, debug=False):
        """Runs `command` with testpath as cwd.
        When debug is False, 
        """
        result = run(command, shell=True, check=not debug, cwd=self.testpath, 
                capture_output=True, text=True)
        if debug:
            print(result.stdout)
            print(result.stderr)
        return result

    def show_tree(self):
        self.run_in_testpath("tree", debug=True)

    def update_settings(self, key, value):
        settings_path = self.testpath / "settings.yaml"
        settings = yaml.safe_load(settings_path.read_text())
        if value is None:
            del settings[key]
        else:
            settings[key] = value
        settings_path.write_text(yaml.dump(settings))

    def assertFileExists(self, path, is_dir=False, message=None):
        if not Path(self.testpath / path).exists():
            message = message or f"Expected {path} to exist"
            raise AssertionError(message)
        if is_dir and not Path(self.testpath / path).is_dir():
            message = message or f"Expected {path} to be a directory"
            raise AssertionError(message)
        if not is_dir and Path(self.testpath / path).is_dir():
            message = message or f"Expected {path} to be a file, not a directory"
            raise AssertionError(message)

    def assertFileDoesNotExist(self, path, message=None):
        if Path(self.testpath / path).exists():
            message = message or f"Expected {path} not to exist"
            raise AssertionError(message)

    def set_mock_editor(self, verbose=False, crash=False):
        """Updates settings['editor'] to the mock editor.
        Also reinitializes corpus.
        """
        command = str(Path("tests/mock_editor.py").resolve())
        if verbose: 
            command += " --verbose"
        if crash: 
            command += " --crash"
        code_command = command + ' "{corpus_file_path}" "{codes_file_path}"'
        memo_command = command + ' --memo "{memo_file_path}"'
        self.update_settings("editor", "mock_editor")
        self.update_settings("editors", {
            'mock_editor': {
                'name': "Mock Editor",
                'code_command': code_command, 
                'memo_command': memo_command,
            }
        })
        self.corpus = QCCorpus(self.testpath / "settings.yaml")

    def read_stats_tsv(self, stdout):
        reader = csv.reader(StringIO(stdout), delimiter="\t")
        table = [[item.strip() for item in row] for row in reader]
        ix_name, *cols = table[0]
        parse = lambda val: None if val == '' else float(val)
        return {ix: dict(zip(cols, map(parse, vals))) for ix, *vals in table[1:]}

class MockCorpus:
    log = None
    settings = {}

MACBETH = """Tomorrow, and tomorrow, and tomorrow,
Creeps in this petty pace from day to day,
To the last syllable of recorded time;
And all our yesterdays have lighted fools
The way to dusty death. Out, out, brief candle!
Life's but a walking shadow, a poor player,
That struts and frets his hour upon the stage,
And then is heard no more. It is a tale
Told by an idiot, full of sound and fury,
Signifying nothing.
"""

MACBETH_CODES_0_2_3 = """pace, prolepsis
pace
speech, prolepsis
light
light, prolepsis
shadow, acting
acting
acting, speech
speech
speech
"""

MOBY_DICK = "Call me *Ishmael*. Some years ago- never mind how long precisely- having little or no money in my purse, and nothing particular to interest me on shore, I thought I would sail about a little and see the watery part of the world. It is a way I have of driving off the spleen and regulating the circulation."

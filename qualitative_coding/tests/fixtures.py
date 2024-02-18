from unittest import TestCase
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory
import yaml


class QCTestCase(TestCase):
    """A subclass of TestCase with methods for instantiating a QC project.
    """

    def setUp(self):
        self.set_up_qc_project()

    def tearDown(self):
        self.tear_down_qc_project()

    def set_up_qc_project(self):
        self.tempdir = TemporaryDirectory()
        self.testpath = Path(self.tempdir.name)
        self.run_in_testpath("qc init")
        self.run_in_testpath("qc init")
        (self.testpath / "macbeth.txt").write_text(DOC)

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
        (self.testpath / "corpus" / "macbeth.txt").write_text(DOC)
        (self.testpath / "codes" / "macbeth.txt.cp.codes").write_text(CODES_0_2_3)

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

DOC = """
Tomorrow, and tomorrow, and tomorrow,
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

CODES_0_2_3 = """
pace, prolepsis
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


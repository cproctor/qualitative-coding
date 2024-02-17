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

    def tear_down_qc_project(self):
        self.tempdir.cleanup()

    def run_in_testpath(self, command):
        return run(command, shell=True, check=True, cwd=self.testpath, capture_output=True, 
                text=True)

    def update_settings(self, key, value):
        settings_path = self.testpath / "settings.yaml"
        settings = yaml.safe_load(settings_path.read_text())
        if value is None:
            del settings[key]
        else:
            settings[key] = value
        settings_path.write_text(yaml.dump(settings))

    def assertFileExists(self, path, message=None):
        if not Path(self.testpath / path).exists():
            message = message or f"Expected {path} to exist"
            raise AssertionError(message)

    def assertDirExists(self, path, message=None):
        if not Path(self.testpath / path).exists():
            message = message or f"Expected dir {path} to exist"
            raise AssertionError(message)
        if not Path(self.testpath / path).is_dir():
            message = message or f"Expected {path.resolve()} to be a directory"
            raise AssertionError(message)



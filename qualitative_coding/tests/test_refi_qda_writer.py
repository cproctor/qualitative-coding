from pathlib import Path
from tests.fixtures import QCTestCase
from qualitative_coding.refi_qda.writer import REFIQDAWriter
from tempfile import TemporaryDirectory
from xmlschema import validate
import importlib.resources

class TestREFIQDAWriter(QCTestCase):
    def setUp(self):
        super().setUp()
        self.writer = REFIQDAWriter(self.testpath / "settings.yaml")

    def test_write_corpus(self):
        self.run_in_testpath("qc corpus import macbeth.txt")
        with TemporaryDirectory() as tempdir:
            project_path = Path(tempdir)
            self.writer.write_corpus(project_path / "sources")
            self.assertFileExists(project_path / "sources" / "macbeth.txt")

    def test_xml_validates(self):
        schema_path = importlib.resources.files("qualitative_coding") / "refi_qda" / "schema.xsd"
        self.run_in_testpath("qc corpus import macbeth.txt")
        self.set_mock_editor(verbose=True)
        self.run_in_testpath("qc code chris")
        with TemporaryDirectory() as tempdir:
            project_path = Path(tempdir)
            xml_path = project_path / "project.qde"
            self.writer.write_xml(xml_path)
            validate(xml_path, schema_path)
            



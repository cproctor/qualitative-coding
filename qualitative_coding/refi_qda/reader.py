from qualitative_coding.exceptions import QCError
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.tree_node import TreeNode
from xmlschema.validators.exceptions import XMLSchemaValidationError
from collections import defaultdict
from subprocess import run
from xmlschema import validate
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import importlib.resources
import shutil
import zipfile

class REFIQDAReader:
    """Imports an existing REFI-QDA project.
    NOTE: Currently does not support importing memos.
    """
    default_coder = "default"

    def __init__(self, qdpxfile):
        self.qdpxfile = qdpxfile
        self.validate(qdpxfile)

    def unpack_project(self, destination):
        self.dest_path = Path(destination)
        if not self.dest_path.exists():
            raise QCError(f"Cannot import project to {dest_path}; no such directory.")
        if len(list(self.dest_path.iterdir())) > 0:
            raise QCError("You can only import a project into an empty directory.")
        QCCorpus.initialize(accept_defaults=True)
        self.corpus = QCCorpus(self.dest_path / "settings.yaml")
        (self.dest_path / "source").mkdir()
        with zipfile.ZipFile(self.qdpxfile, 'r', zipfile.ZIP_DEFLATED) as zf:
            zf.extractall((self.dest_path / "source"))
        tree = ET.parse(self.dest_path / "source" / "project.qde")
        with self.corpus.session():
            self.unpack_xml(tree.getroot())

    def unpack_xml(self, root):
        self.coder_guids = {}
        for child in root:
            if child.tag.endswith("Users"):
                self.unpack_coders(child)
        for child in root:
            if child.tag.endswith("CodeBook"):
                self.unpack_codebook(child)
        for child in root:
            if child.tag.endswith("Variables"):
                self.log("{self.qdpxfile} contains Variables, which are not supported by qc.")
        self.unpack_unsupported(root, "Variables")
        self.unpack_unsupported(root, "Cases")
        for child in root:
            if child.tag.endswith("Sources"):
                self.unpack_sources(child)
        self.unpack_unsupported(root, "Notes")
        self.unpack_unsupported(root, "Links")
        self.unpack_unsupported(root, "Graphs")
        self.unpack_unsupported(root, "Description")
        self.unpack_unsupported(root, "NoteRef")

    def unpack_unsupported(self, root, tagname):
        for child in root:
            if child.tag.endswith(tagname):
                self.log(f"{self.qdpxfile} contains {tagname}, which are not supported by qc.")

    def unpack_coders(self, users):
        for user in users:
            name = user.attrib['name']
            guid = user.attrib['guid']
            self.corpus.get_or_create_coder(name)
            self.coder_guids[guid] = name

    def create_default_coder_if_none_defined(self):
        if not hasattr(self, "coder_guids"):
            self.corpus.get_or_create_coder("default")

    def unpack_codebook(self, codebook):
        for child in codebook:
            self.unpack_codes(child)

    def unpack_codes(self, codes):
        self.code_guids = {}
        self.code_tree = TreeNode(TreeNode.root)

        def unpack_code(code, parent):
            name = code.attrib['name']
            guid = code.attrib['guid']
            self.corpus.get_or_create_code(name)
            self.code_guids[guid] = name
            node = TreeNode(name, parent=parent)
            parent.children.append(node)
            for child in code:
                if child.tag.endswith("Code"):
                    unpack_code(child, node)

        for code in codes:
            unpack_code(code, self.code_tree)

        TreeNode.write_yaml(self.corpus.codebook_path, self.code_tree)

    def unpack_sources(self, sources):
        self.document_guids = {}
        for source in sources:
            guid = source.attrib['guid']
            file_path = source.attrib['plainTextPath']
            self.document_guids[guid] = file_path
            self.corpus.import_media(self.dest_path / "source" / "sources" / file_path, importer="verbatim")
            line_positions = self.line_positions(file_path)
            coded_lines = defaultdict(list)
            for selection in source:
                if selection.tag.endswith("PlainTextSelection"):
                    match = re.match("line:(\d+)", selection.attrib.get("name", ""))
                    if match:
                        line = int(match.group(1))
                    else:
                        position = int(selection.attrib['startPosition'])
                        line = self.get_line_for_position(position, line_positions)
                    for coding in selection:
                        if coding.tag.endswith("Coding"):
                            coder_guid = coding.attrib['creatingUser']
                            coder = self.coder_guids.get(coder_guid, self.default_coder)
                            for coderef in coding:
                                if coderef.tag.endswith("CodeRef"):
                                    code = self.code_guids[coderef.attrib['targetGUID']]
                                    coded_lines[coder].append({'line': line, 'code_id': code})
            for coder, cls in coded_lines.items():
                self.corpus.update_coded_lines(file_path, coder, cls)

    def get_line_for_position(self, position, line_positions):
        for line, (start, end) in enumerate(line_positions):
            if position >= start:
                return line

    def validate(self, qdpxfile):
        if not Path(qdpxfile).suffix == ".qdpx":
            raise QCError(f"{qdpxfile} must end in .qdpx")
        if not zipfile.is_zipfile(qdpxfile):
            raise QCError(f"{qdpxfile} is not a zipfile")
        with zipfile.ZipFile(qdpxfile, 'r', zipfile.ZIP_DEFLATED) as zf:
            zroot = zipfile.Path(zf)
            qde = zroot / "project.qde"
            if not qde.exists():
                raise QCError("{qdpxfile} does not contain project.qde")
            qcf = importlib.resources.files("qualitative_coding")
            schema_path = qcf / "refi_qda" / "schema.xsd"
            try:
                validate(qde.read_text(), schema_path)
            except XMLSchemaValidationError as err:
                raise QCError(
                    f"When reading {qdpxfile}, project.qde did not validate " + 
                    f"against the REFI-QDA schema:\n" + 
                    repr(err)
                )

    def line_positions(self, corpus_file_path):
        """returns a list of (start, end) character positions for lines in doc.
        """
        text = (self.corpus.corpus_dir / corpus_file_path).read_text()
        lines = []
        index = 0
        for line in text:
            start = index
            end = index + len(line)
            lines.append((start, end))
            index += len(line)
        return lines

    def log(self, message):
        self.corpus.log.info(message)

    def print_tree(self, project_path):
        result = run("tree", cwd=project_path, capture_output=True, text=True, shell=True)
        print(result.stdout)


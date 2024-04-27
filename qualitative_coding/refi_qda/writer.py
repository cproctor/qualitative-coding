from qualitative_coding.corpus import QCCorpus
from qualitative_coding.exceptions import QCError, InvalidParameter
from tempfile import TemporaryDirectory
from shutil import copytree
from pathlib import Path
from subprocess import run
from collections import defaultdict
from hashlib import md5
import os
from importlib.metadata import metadata
from zipfile import ZipFile, ZIP_DEFLATED
from uuid import UUID
from xml.etree.ElementTree import (
    Element,
    Comment,
    tostring,
)

class REFIQDAWriter:
    """Exports a QC project as a REFI-QDA project.
    See specification at https://www.qdasoftware.org/
    """
    def __init__(self, settings, debug=False):
        self.settings = settings
        self.corpus = QCCorpus(settings)
        self.debug = debug

    def write(self, outpath):
        """Write a zip file at the given outpath
        """
        if Path(outpath).suffix != ".qdpx":
            raise InvalidParameter("REFI-QDA projects must have suffix .qdpx")
        with TemporaryDirectory() as tempdir:
            project_path = Path(tempdir)
            self.write_xml(project_path / "project.qde")
            self.write_corpus(project_path / "sources")
            if self.debug:
                self.print_tree(project_path)
            with ZipFile(outpath, 'w', ZIP_DEFLATED) as zf:
                for dirpath, dirnames, filenames in os.walk(tempdir):
                    for fn in filenames:
                        path = Path(dirpath) / fn
                        zf.write(path, arcname=path.relative_to(tempdir))

    def write_xml(self, outpath):
        root = self.xml_root()
        root.append(self.users_to_xml())
        root.append(self.codebook_to_xml())
        root.append(self.sources_to_xml())
        if self.debug:
            print(tostring(root, encoding="unicode"))
        outpath.write_text(tostring(root, encoding="unicode"))

    def write_corpus(self, outpath):
        copytree(self.corpus.corpus_dir, outpath)

    def print_tree(self, project_path):
        result = run("tree", cwd=project_path, capture_output=True, text=True, shell=True)
        print(result.stdout)

    def xml_root(self):
        root = Element("Project")
        root.set("xmlns", "urn:QDA-XML:project:1.0")
        root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        version = metadata('qualitative-coding')['version']
        root.set("origin", f"qc {version}")
        root.set("name", "qc project")
        return root

    def codebook_to_xml(self):
        """Render the codebook as XML.
        Note that qc allows codes to appear at multiple places in the codebook. 
        However, each code in the xml tree requires its own GUID. Therefore, 
        Codings will artibrarily (but deterministically) specify the GUID of a code 
        when it appears multiple times in the codebook.
        Must be called before sources_to_xml.
        """
        def node_to_xml(node):
            xnode = Element("Code")
            xnode.set("name", node.name)
            guid = self.code_guid(node.expanded_name())
            if node.name not in self.code_guids:
                self.code_guids[node.name] = guid
            xnode.set("guid", guid)
            xnode.set("isCodable", "true")
            for child in node.children:
                xnode.append(node_to_xml(child))
            return xnode

        self.code_guids = {}
        codebook = Element("CodeBook")
        codes = Element("Codes")
        codebook.append(codes)
        with self.corpus.session():
            root = self.corpus.get_codebook()
        for node in root.children:
            codes.append(node_to_xml(node))
        return codebook

    def users_to_xml(self):
        users = Element("Users")
        with self.corpus.session():
            for coder in self.corpus.get_all_coders():
                user = Element("User")
                user.set("name", coder.name)
                user.set("guid", self.guid(coder.name))
                users.append(user)
        return users

    def sources_to_xml(self):
        sources = Element("Sources")
        with self.corpus.session():
            docs = self.corpus.get_documents()
            sources = Element("Sources")
            for doc in docs:
                source = Element("TextSource")
                source.set("plainTextPath", doc.file_path)
                source.set("guid", self.guid(doc.file_path))
                doc_line_positions = self.line_positions(doc.file_path)
                coded_lines = self.corpus.get_coded_lines(file_list=[doc.file_path])
                lines_with_codes = defaultdict(list)
                for cl in coded_lines:
                    lines_with_codes[cl.line].append(cl)
                for line, cls in lines_with_codes.items():
                    selection = Element("PlainTextSelection")
                    selection.set("guid", self.selection_guid(doc.file_path, line))
                    selection.set("name", f"line:{line}")
                    selection.set("startPosition", str(doc_line_positions[line][0]))
                    selection.set("endPosition", str(doc_line_positions[line][1]))
                    for code, coder, line, file_path in cls:
                        coding = Element("Coding")
                        coding.set("guid", self.coding_guid(code, coder, line, file_path))
                        coding.set("creatingUser", self.coder_guid(coder))
                        code_ref = Element("CodeRef")
                        code_ref.set("targetGUID", self.code_guids[code])
                        coding.append(code_ref)
                        selection.append(coding)
                    source.append(selection)
                sources.append(source)
        return sources

    def line_positions(self, corpus_file_path):
        """returns a list of (start, end) character positions for lines in doc.
        """
        lines = []
        index = 0
        with (self.corpus.corpus_dir / corpus_file_path).open() as fh:
            for line in fh:
                start = index
                end = index + len(line)
                lines.append((start, end))
                index += len(line)
        return lines

    def coder_guid(self, coder):
        return self.guid(coder)

    def coding_guid(self, code, coder, line, file_path):
        return self.guid(':'.join([file_path, str(line), coder, code]))

    def selection_guid(self, file_path, line):
        return self.guid(f"{file_path}:{line}")

    def code_guid(self, code):
        return self.guid(code)

    def guid(self, source):
        digest = md5(source.encode('utf8')).hexdigest()[:16]
        return str(UUID(bytes=digest.encode('utf8')))

from pathlib import Path
import shutil
from sqlalchemy import (
    create_engine,
)
from qualitative_coding.migrations.migration import QCMigration
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.media_importers import media_importers
from qualitative_coding.helpers import read_settings
from qualitative_coding.logs import get_logger
from qualitative_coding.database.models import (
    Base,
    Document,
    CodedLine
)
from qualitative_coding.views.styles import (
    address, 
    question, 
    debug,
    info,
    warn,
    confirm,
    error,
    success
)
import os

class Migrate_1_0_0(QCMigration):
    _version = "1.0.0"

    def apply(self, settings_path):
        self.set_setting(settings_path, "qc_version", self._version)
        self.set_setting(settings_path, "database", 'qualitative_coding.sqlite3')
        self.set_setting(settings_path, "editor", 'vim')
        QCCorpus.initialize(settings_path)
        corpus = QCCorpus(settings_path)
        corpus_v0 = QCCorpusV0(settings_path)
        with corpus.session():
            for filepath in corpus.corpus_dir.iterdir():
                if filepath.is_dir():
                    corpus.import_media(filepath, recursive=True, importer="verbatim")
                else:
                    corpus.import_media(filepath, importer="verbatim")
            for dir_path, dir_names, filenames in os.walk(corpus.corpus_dir):
                for fn in filenames:
                    file_path = Path(dir_path) / fn
                    document = corpus.get_document(file_path)
                    coded_lines = []
                    for coder_name, code_data in corpus_v0.get_codes(file_path).items():
                        coder = corpus.get_or_create_coder(coder_name)
                        for line_num, code_name in code_data:
                            coded_lines.append({
                                "line": line_num,
                                "code_id": corpus.get_or_create_code(code_name).name
                            })
                    corpus.update_coded_lines(document, coder_name, coded_lines)
        shutil.rmtree(corpus_v0.codes_dir)

    def revert(self, settings_path):
        self.delete_setting(settings_path, "qc_version")
        self.delete_setting(settings_path, "database")
        self.delete_setting(settings_path, "editor")

class QCCorpusV0:
    def __init__(self, settings_file="settings.yaml"):
        self.settings_file = Path(settings_file)
        self.settings = read_settings(settings_file)
        self.log = get_logger(__name__, self.settings['logs_dir'], self.settings.get('debug'))
        self.corpus_dir = Path(self.settings['corpus_dir']).resolve()
        self.codes_dir = Path(self.settings['codes_dir']).resolve()

    def get_codes(self, corpus_text_path, coder=None, merge=False, unit='line'):
        """
        Returns codes pertaining to a corpus text.
        Returns a dict like {coder_id: [(line_num, code)...]}. 
        If merge or coder, there is no ambiguity;instead returns a list of [(line_num, code)...]
        If unit is 'document', returns a set of codes when coder or merge is given, otherwise
        returns a dict mapping coders to sets of codes.
        """
        codes = {}
        for f in self.get_code_files_for_corpus_file(corpus_text_path, coder=coder):
            codes[self.get_coder_from_code_path(f)] = self.read_codes(f)
        if coder:
            return codes.get(coder, {})
        elif merge:
            if unit == 'line': 
                return sum(codes.values(), [])
            elif unit == 'document': 
                return set().union(*codes.values())
            else:
                raise NotImplementedError("Unit must be 'line' or 'document'.")
        else:
            return codes

    def get_code_files_for_corpus_file(self, corpus_text_path, coder=None):
        "Returns an iterator over code files pertaining to a corpus file"
        text_path = corpus_text_path.relative_to(self.corpus_dir)
        name_parts = text_path.name.split('.')
        return self.codes_dir.glob(str(text_path) + '.' + (coder or '*') + '.codes')

    def get_coder_from_code_path(self, code_file_path):
        "Maps Path('some_interview.txt.cp.codes') -> 'cp'"
        parts = code_file_path.name.split('.')
        return parts[-2]

    def read_codes(self, code_file_path):
        """When passed a file object, returns a list of (line_num, code) if unit is 'line'. 
        When unit is 'document', Returns a set of codes.
        """
        codes = []
        with open(code_file_path) as inf:
            for line_num, line in enumerate(inf):
                codes += [(line_num, code.strip()) for code in line.split(",") if code.strip()]
        return codes

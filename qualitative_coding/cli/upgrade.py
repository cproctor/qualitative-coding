import click
import yaml
from pathlib import Path
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.cli.decorators import handle_qc_errors
from qualitative_coding.media_importers import media_importers
from qualitative_coding.database.models import (
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
import shutil

@click.command()
@click.argument("old_settings")
@click.option("-s", "--settings", default="settings.yaml", type=click.Path(),
        help="Settings file")
@click.option("-i", "--importer", type=click.Choice(media_importers.keys()),
        default="verbatim",
        help="Importer class to use")
@click.option("-c", "--clean", is_flag=True, help="Remove existing project data")
@handle_qc_errors
def upgrade(old_settings, settings, importer, clean):
    "Upgrade from qc v0 -> v1"
    s = yaml.safe_load(Path(settings).read_text())
    if clean:
        shutil.rmtree(s['corpus_dir'])
        os.unlink(s['database'])
    old_s = yaml.safe_load(Path(old_settings).read_text())
    QCCorpus.initialize(settings)
    corpus = QCCorpus(s)
    with corpus.session():
        corpus_v0 = QCCorpusV0(old_settings)
        corpus_root_path = Path(corpus.settings['corpus_dir'])
        old_corpus_root_path = Path(old_s['corpus_dir'])
        importer = media_importers[importer](corpus.settings)
        for dir_path, dir_names, filenames in os.walk(old_corpus_root_path):
            corpus_dir_path = corpus_root_path / Path(dir_path).relative_to(old_corpus_root_path)
            corpus_dir_path.mkdir(parents=True, exist_ok=True)
            for fn in filenames:
                old_file_path = Path(dir_path) / fn
                new_file_path = (corpus_dir_path / fn).with_suffix(".txt")
                if new_file_path.exists():
                    err = f"Skipping {new_file_path}: File already exists"
                    click.echo(warn(err))
                    continue
                try:
                    importer.import_media(old_file_path, new_file_path)
                except Document.AlreadyExists as err:
                    os.unlink(new_file_path)
                    click.echo(warn(f"Skipping {new_file_path}: Document already exists in database"))
                    continue
                document = corpus.get_document(new_file_path)
                coded_lines = []
                for coder_name, code_data in corpus_v0.get_codes(old_file_path).items():
                    coder = corpus.get_or_create_coder(coder_name)
                    for line_num, code_name in code_data:
                        coded_lines.append({
                            "line": line_num,
                            "coder_id": coder_name, 
                            "code_id": corpus.get_or_create_code(code_name).name
                        })
                corpus.create_coded_lines_if_needed(document, coded_lines)

class QCCorpusV0:
    """Subset of methods from v0 implementation of corpus. 
    Preserved here to support reading old qc projects.
    """
    def __init__(self, settings_file):
        self.settings_file = Path(settings_file)
        self.settings = yaml.safe_load(self.settings_file.read_text())
        self.corpus_dir = Path(self.settings['corpus_dir'])
        self.codes_dir = Path(self.settings['codes_dir'])

    def get_codes(self, corpus_text_path, coder=None, merge=False, unit='line'):
        """
        Returns codes pertaining to a corpus text.
        Returns a dict like {coder_id: [(selection_ix, code)...]}. 
        If merge or coder, returns a list of [(selection_ix, code)...]
        The selection indices are guaranteed to be in order.
        """
        codes = {}
        for f in self.get_code_files_for_corpus_file(corpus_text_path, coder=coder):
            codes[self.get_coder_from_code_path(f)] = self.read_codes(f, unit=unit)
        if coder:
            return codes.get(coder, {})
        elif merge:
            merged_codes = sum(codes.values(), [])
            return sorted(set(merged_codes))
        else:
            return codes

    def get_code_files_for_corpus_file(self, corpus_text_path, coder=None):
        "Returns an iterator over code files pertaining to a corpus file"
        text_path = corpus_text_path.relative_to(self.corpus_dir)
        name_parts = text_path.name.split('.')
        return self.codes_dir.glob(str(text_path) + '.' + (coder or '*') + '.codes')

    def read_codes(self, code_file_path, unit='line'):
        """Reads codes from a code file as a list of (ix, code).
        ix is the selection index and code is a string.
        When unit is 'line', selection index is the line number.
        When unit is 'paragraph', selection index is the paragraph number.
        When unit is 'document', selection index is 0.
        """
        codes = []
        with open(code_file_path) as inf:
            for line_num, line in enumerate(inf):
                codes += [(line_num, code.strip()) for code in line.split(",") if code.strip()]
        if unit == 'line': 
            return codes
        elif unit == 'paragraph':
            corpus_file_path = self.get_corpus_file_path(code_file_path)
            para_starts = self.get_paragraph_start_lines(corpus_file_path)
            return [(self.get_paragraph_index(para_starts, line), code) for line, code in codes]
        elif unit == 'document': 
            return [(0, c) for c in set(code for i, code in codes)]
        else:
            raise NotImplementedError("Unit must be 'line' or 'document'.")

    def get_coder_from_code_path(self, code_file_path):
        "Maps Path('some_interview.txt.cp.codes') -> 'cp'"
        parts = code_file_path.name.split('.')
        return parts[-2]

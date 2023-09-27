import os
import click
from qualitative_coding.corpus import QCCorpus
from pathlib import Path
from textwrap import fill
from qualitative_coding.exceptions import InvalidParameter
from qualitative_coding.cli.decorators import handle_qc_errors
from qualitative_coding.media_importers import media_importers

@click.command(name="import")
@click.argument("file_path")
@click.option("-s", "--settings", default="settings.yaml", help="Settings file")
@click.option("-r", "--recursive", is_flag=True, 
        help="Recursively import from directory")
@click.option("-c", "--corpus-root", 
        help="Relative path to import dir within corpus_dir")
@click.option("-i", "--importer", type=click.Choice(media_importers.keys()),
        default="pandoc",
        help="Importer class to use")
@handle_qc_errors
def import_media(file_path, settings, recursive, corpus_root, importer):
    "Import corpus files"
    path = Path(file_path)
    if not path.exists():
        raise InvalidParameter(f"{path} does not exist.")
    corpus = QCCorpus(settings)
    corpus_root_path = Path(corpus.settings['corpus_dir'])
    if corpus_root:
        corpus_root_path = corpus_root_path / corpus_root
        corpus_root_path.mkdir(parents=True, exist_ok=True)
    imp = media_importers[importer]()
    if recursive:
        for dir_path, dir_names, filenames in os.walk(path):
            corpus_dir_path = corpus_root_path / dir_path
            corpus_dir_path.mkdir(parents=True, exist_ok=True)
            for fn in filenames:
                cfn = (corpus_dir_path / fn).with_suffix(".txt")
                imp.import_media(fn, cfn)
    else:
        if path.is_dir():
            raise IncompatibleOptions(f"{path} is a dir. Use --recursive.")
        imp.import_media(path, (corpus_root_path / path.name).with_suffix(".txt"))

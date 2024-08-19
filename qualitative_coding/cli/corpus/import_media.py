import click
import os
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.cli.decorators import handle_qc_errors
from qualitative_coding.media_importers import media_importers
from qualitative_coding.logs import configure_logger

@click.command(name="import")
@click.argument("file_path")
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
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
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    log = configure_logger(settings_path)
    log.info("corpus import", file_path=file_path, recursive=recursive, corpus_root=corpus_root,
             importer=importer)
    corpus = QCCorpus(settings_path)
    with corpus.session():
        corpus.import_media(
            file_path, 
            recursive=recursive, 
            corpus_root=corpus_root, 
            importer=importer
        )

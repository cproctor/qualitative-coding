import click
import os
from qualitative_coding.corpus import QCCorpus

@click.command()
@click.argument("target")
@click.argument("destination")
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@click.option("-r", "--recursive", is_flag=True, 
        help="Recursively import from directory")
def move(target, destination, settings, recursive):
    "Move a file in the corpus"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    corpus = QCCorpus(settings_path)
    with corpus.session():
        corpus.move_document(target, destination, recursive=recursive)

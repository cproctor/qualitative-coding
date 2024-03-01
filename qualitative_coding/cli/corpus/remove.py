import click
import os
from qualitative_coding.corpus import QCCorpus

@click.command()
@click.argument("target")
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@click.option("-r", "--recursive", is_flag=True, 
        help="Recursively remove from directory")
def remove(target, settings, recursive):
    "Remove a file from the corpus"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    corpus = QCCorpus(settings_path)
    with corpus.session():
        corpus.remove_document(target, recursive=recursive)


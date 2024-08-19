import click
import os
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.logs import configure_logger

@click.command()
@click.argument("target")
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@click.option("-r", "--recursive", is_flag=True, 
        help="Recursively remove from directory")
def remove(target, settings, recursive):
    "Remove a file from the corpus"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    log = configure_logger(settings_path)
    log.info("corpus remove", target=target, recursive=recursive)
    corpus = QCCorpus(settings_path)
    with corpus.session():
        corpus.remove_document(target, recursive=recursive)


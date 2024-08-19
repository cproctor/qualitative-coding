import click
import os
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.logs import configure_logger
from qualitative_coding.cli.decorators import handle_qc_errors

@click.command()
@click.argument("target")
@click.argument("destination")
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@click.option("-r", "--recursive", is_flag=True, 
        help="Recursively import from directory")
@handle_qc_errors
def move(target, destination, settings, recursive):
    "Move a file in the corpus"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    log = configure_logger(settings_path)
    log.info("corpus move", target=target, destination=destination, recursive=recursive)
    corpus = QCCorpus(settings_path)
    with corpus.session():
        corpus.move_document(target, destination, recursive=recursive)

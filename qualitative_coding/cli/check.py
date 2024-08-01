import click
import os
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.logs import configure_logger
from qualitative_coding.cli.decorators import (
    handle_qc_errors,
)

@click.command()
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@handle_qc_errors
def check(settings):
    "Check project for errors"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    log = configure_logger(settings_path)
    log.info("check")
    corpus = QCCorpus(settings_path)
    with corpus.session():
        corpus.validate_corpus_paths()

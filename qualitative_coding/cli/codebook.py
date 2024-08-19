import click
import os
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.cli.decorators import handle_qc_errors
from qualitative_coding.logs import configure_logger

@click.command()
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@handle_qc_errors
def codebook(settings):
    "Update the codebook"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    log = configure_logger(settings_path)
    log.info("codebook")
    corpus = QCCorpus(settings_path)
    with corpus.session():
        corpus.update_codebook()

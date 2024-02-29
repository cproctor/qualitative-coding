import click
import os
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.cli.decorators import handle_qc_errors

@click.command()
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@handle_qc_errors
def codebook(settings):
    "Update the codebook"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    corpus = QCCorpus(settings_path)
    with corpus.session():
        corpus.update_codebook()

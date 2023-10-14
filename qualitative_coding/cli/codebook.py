import yaml
import click
from pathlib import Path
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.cli.decorators import handle_qc_errors

@click.command()
@click.option("-s", "--settings", default="settings.yaml", type=click.Path(exists=True),
        help="Settings file")
@handle_qc_errors
def codebook(settings):
    "Update the codebook"
    s = yaml.safe_load(Path(settings).read_text())
    corpus = QCCorpus(s)
    with corpus.session():
        corpus.update_codebook()

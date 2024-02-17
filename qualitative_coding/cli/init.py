import click
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.cli.decorators import handle_qc_errors
import yaml
from pathlib import Path

@click.command()
@click.option("-s", "--settings", default="settings.yaml", type=click.Path(),
        help="Settings file")
@handle_qc_errors
def init(settings):
    "Initialize a qc project"
    QCCorpus.initialize(settings)

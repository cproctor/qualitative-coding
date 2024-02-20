import click
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.cli.decorators import handle_qc_errors
import yaml
from pathlib import Path

@click.command()
@click.option("-s", "--settings", default="settings.yaml", type=click.Path(),
        help="Settings file")
@click.option("-y", "--accept-defaults", "accept_defaults", is_flag=True, 
        help="Use default values")
@handle_qc_errors
def init(settings, accept_defaults):
    "Initialize a qc project"
    QCCorpus.initialize(settings, accept_defaults)

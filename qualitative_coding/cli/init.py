import click
from qualitative_coding.cli.decorators import handle_qc_errors
from os import getcwd
from pathlib import Path

@click.command()
@click.option("-s", "--settings", default="settings.yaml", type=click.Path(),
        help="Settings file")
@click.option("-y", "--accept-defaults", "accept_defaults", is_flag=True, 
        help="Use default values")
@click.option("-i", "--import", "_import", help="Import an existing qdpx project")
@handle_qc_errors
def init(settings, accept_defaults, _import):
    "Initialize a qc project"
    if _import:
        from qualitative_coding.refi_qda.reader import REFIQDAReader
        reader = REFIQDAReader(_import)
        reader.unpack_project(Path.cwd())
    else:
        from qualitative_coding.corpus import QCCorpus
        QCCorpus.initialize(settings, accept_defaults)

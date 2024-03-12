import click
import os
from qualitative_coding.cli.decorators import handle_qc_errors
from os import getcwd
from pathlib import Path

@click.command()
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@click.option("-y", "--accept-defaults", "accept_defaults", is_flag=True, 
        help="Use default values")
@click.option("-i", "--import", "_import", help="Import an existing qdpx project")
@handle_qc_errors
def init(settings, accept_defaults, _import):
    "Initialize a qc project"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    if _import:
        from qualitative_coding.refi_qda.reader import REFIQDAReader
        reader = REFIQDAReader(_import)
        reader.unpack_project(Path.cwd())
    else:
        from qualitative_coding.corpus import QCCorpus
        QCCorpus.initialize(settings_path, accept_defaults)

import click
import os
from pathlib import Path
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.refi_qda.writer import REFIQDAWriter
from qualitative_coding.cli.decorators import (
    handle_qc_errors,
)

@click.command()
@click.argument("export_path")
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@handle_qc_errors
def export(export_path, settings):
    "Export project as REFI-QDA"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    path = Path(export_path).with_suffix(".qdpx")
    writer = REFIQDAWriter(settings_path)
    writer.write(export_path)


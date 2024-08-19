import click
import os
import yaml
from pathlib import Path
from qualitative_coding.cli.decorators import handle_qc_errors
from qualitative_coding.migrations import migrations, migrate
from qualitative_coding.helpers import read_settings
from qualitative_coding.logs import configure_logger
import shutil

@click.command()
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@click.option("-v", "--version", type=click.Choice([m._version for m in migrations]),
        default=migrations[-1]._version,
        help="Target upgrade or downgrade version")
@handle_qc_errors
def upgrade(settings, version):
    "Upgrade project to new version of qc"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    log = configure_logger(settings_path)
    log.info("upgrade", version=version)
    migrate(settings_path, version)

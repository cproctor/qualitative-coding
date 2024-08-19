import os
import click
from pathlib import Path
from subprocess import run
from collections import defaultdict
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.exceptions import IncompatibleOptions, QCError, InvalidParameter
from qualitative_coding.cli.decorators import handle_qc_errors
from qualitative_coding.logs import configure_logger

@click.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@click.option("-n", "--new", type=click.Path(exists=True), help="Path to new version")
@click.option("-d", "--dryrun", is_flag=True, 
        help="Show simulated results")
@handle_qc_errors
def update(file_path, settings, new, dryrun):
    "Update the content of corpus files"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    log = configure_logger(settings_path)
    log.info("corpus update", new=new, dryrun=dryrun)
    corpus = QCCorpus(settings_path)
    with corpus.session():
        corpus.update_document(file_path, new, dryrun)

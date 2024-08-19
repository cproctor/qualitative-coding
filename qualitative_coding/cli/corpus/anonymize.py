import os
import click
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.exceptions import QCError
from qualitative_coding.logs import configure_logger

@click.command()
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@click.option("-p", "--pattern", help="Pattern to filter corpus filenames (glob-style)")
@click.option("-f", "--filenames", help="File path containing a list of filenames to use")
@click.option("-k", "--key", help="Path to key file")
@click.option("-u", "--update", is_flag=True, help="Update documents in place")
@handle_qc_errors
def anonymize(settings, pattern, filenames, key, update):
    "Anonymize corpus files"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    log = configure_logger(settings_path)
    log.info("corpus anonymize", pattern=pattern, filenames=filenames, key=key, update=update)
    corpus = QCCorpus(settings_path)
    if key:
        raise QCError("Not implemented: key")


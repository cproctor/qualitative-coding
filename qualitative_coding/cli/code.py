import click
import yaml
import os
from pathlib import Path
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.exceptions import QCError, IncompatibleOptions
from qualitative_coding.views.viewer import QCCorpusViewer
from qualitative_coding.cli.decorators import handle_qc_errors
from qualitative_coding.helpers import read_file_list
from qualitative_coding.logs import configure_logger

@click.command()
@click.argument("coder")
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@click.option("-p", "--pattern", 
        help="Pattern to filter corpus filenames (glob-style)")
@click.option("-f", "--filenames", 
        help="File path containing a list of filenames to use")
@click.option("-u", "--uncoded", is_flag=True, help="Select uncoded files")
@click.option("-1", "--first", is_flag=True, help="Select first uncoded file")
@click.option("-r", "--random", is_flag=True, help="Select random uncoded file")
@click.option("--recover", is_flag=True, help="Recover incomplete coding session")
@click.option("--abandon", is_flag=True, help="Abandon incomplete coding session")
@handle_qc_errors
def code(coder, settings, pattern, filenames, uncoded, first, random, recover, abandon):
    "Open a file for coding"
    if first and random:
        msg = "--first and --random cannot both be used."
        raise IncompatibleOptions(msg)
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    log = configure_logger(settings_path)
    log.info("code", coder=coder, pattern=pattern, filenames=filenames, uncoded=uncoded, 
             first=first, random=random, recover=recover, abandon=abandon)
    corpus = QCCorpus(settings_path)
    viewer = QCCorpusViewer(corpus)
    if recover:
        viewer.recover_incomplete_coding_session(coder)
    elif abandon:
        viewer.abandon_incomplete_coding_session()
    else:
        if viewer.incomplete_coding_session_exists():
            raise QCError(
                "An incomplete coding session exists. " + 
                "Run qc code coder --recover to recover this coding session or " + 
                "qc code coder --abandon to abandon it."
            )
        f = viewer.select_file(
            coder,
            pattern=pattern, 
            file_list=read_file_list(filenames),
            uncoded=uncoded, 
            first=first, 
            random=random,
        )
        viewer.open_editor(f, coder)

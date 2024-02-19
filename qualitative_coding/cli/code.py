import click
import yaml
from pathlib import Path
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.exceptions import IncompatibleOptions
from qualitative_coding.views.viewer import QCCorpusViewer
from qualitative_coding.cli.decorators import handle_qc_errors
from qualitative_coding.helpers import read_file_list

@click.command()
@click.argument("coder")
@click.option("-s", "--settings", default="settings.yaml", type=click.Path(exists=True),
        help="Settings file")
@click.option("-p", "--pattern", 
        help="Pattern to filter corpus filenames (glob-style)")
@click.option("-f", "--filenames", 
        help="File path containing a list of filenames to use")
@click.option("-u", "--uncoded", is_flag=True, help="Select uncoded files")
@click.option("-1", "--first", is_flag=True, help="Select first uncoded file")
@click.option("-r", "--random", is_flag=True, help="Select random uncoded file")
@handle_qc_errors
def code(coder, settings, pattern, filenames, uncoded, first, random):
    "Open a file for coding"
    if first and random:
        msg = "--first and --random cannot both be used."
        raise IncompatibleOptions(msg)

    corpus = QCCorpus(settings)
    viewer = QCCorpusViewer(corpus)
    f = viewer.select_file(
        coder,
        pattern=pattern, 
        file_list=read_file_list(filenames),
        uncoded=uncoded, 
        first=first, 
        random=random,
    )
    viewer.open_editor(f, coder)

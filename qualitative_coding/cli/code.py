import click
import yaml
from pathlib import Path
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.views.viewer import QCCorpusViewer
from qualitative_coding.cli.decorators import (
    handle_qc_errors,
)

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
    s = yaml.safe_load(Path(settings).read_text())
    corpus = QCCorpus(s)
    viewer = QCCorpusViewer(corpus)
    if filenames:
        file_list = Path(args.filenames).read_text().split("\n")
    else:
        file_list = None
    f = viewer.select_file(
        coder,
        pattern=pattern, 
        file_list=file_list,
        uncoded=uncoded, 
        first=first, 
        random=random,
    )
    viewer.open_editor(f, coder)

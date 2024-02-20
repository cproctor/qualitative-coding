import click
import yaml
from pathlib import Path
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.views.viewer import QCCorpusViewer
from qualitative_coding.cli.decorators import handle_qc_errors
from qualitative_coding.exceptions import IncompatibleOptions
from qualitative_coding.helpers import read_file_list
from tabulate import tabulate_formats

@click.command()
@click.argument("code", nargs=-1)
@click.option("-s", "--settings", default="settings.yaml", help="Settings file")
@click.option("-p", "--pattern", 
        help="Pattern to filter corpus filenames (glob-style)")
@click.option("-f", "--filenames", 
        help="File path containing a list of filenames to use")
@click.option("-c", "--coder", help="Coder")
@click.option("-d", "--depth", help="Maximum depth in code tree", type=int)
@click.option("-n", "--unit", default="line", help="Unit of analysis",
        type=click.Choice(['line', 'paragraph', 'document']))
@click.option("-r", "--recursive-codes", "recursive_codes", is_flag=True, 
        help="Include child codes")
@click.option("-a", "--recursive-counts", is_flag=True,
        help="Counts for codes include child codes")
@click.option("-e", "--expanded", is_flag=True,
        help="Show names of codes in expanded form")
@click.option("-m", "--format", "_format", type=click.Choice(tabulate_formats),
        metavar="[tabulate.tabulate_formats]", help="Output format.")
@click.option("-o", "--outfile", help="Filename for CSV export")
@click.option("-u", "--max", "_max", help="Maximum count value to show", type=int)
@click.option("-l", "--min", "_min", help="Minimum count value to show", type=int)
@click.option("-z", "--zeros", is_flag=True, help="Include codes with zero occurrences")
@click.option("-t", "--total-only", is_flag=True,
        help="Show total but not count")
@handle_qc_errors
def stats(code, settings, pattern, filenames, coder, depth, unit, recursive_codes, 
        recursive_counts, expanded, _format, outfile, _max, _min, zeros, total_only):
    "Show statistics about codes"
    if depth and not recursive_codes: 
        msg = "--depth requires --recursive-codes"
        raise IncompatibleOptions(msg)
    if total_only and recursive_counts:
        msg = "--total-only and --recursive-counts are incompatible"
        raise IncompatibleOptions(msg)
    corpus = QCCorpus(settings)
    viewer = QCCorpusViewer(corpus)
    viewer.show_stats(
        code, 
        max_count=_max, 
        min_count=_min, 
        depth=depth, 
        recursive_codes=recursive_codes,
        recursive_counts=recursive_counts,
        expanded=expanded, 
        format=_format, 
        pattern=pattern,
        file_list=read_file_list(filenames),
        coder=coder,
        unit=unit,
        outfile=outfile,
        total_only=total_only,
        zeros=zeros,
    )


import click
import os
import yaml
from pathlib import Path
from tabulate import tabulate_formats
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.views.viewer import QCCorpusViewer
from qualitative_coding.cli.decorators import handle_qc_errors
from qualitative_coding.helpers import read_file_list

@click.command()
@click.argument("codes", nargs=-1)
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@click.option("-p", "--pattern", 
        help="Pattern to filter corpus filenames (glob-style)")
@click.option("-f", "--filenames", 
        help="File path containing a list of filenames to use")
@click.option("-c", "--coders", help="Coders", multiple=True)
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
@click.option("-0", "--probs", is_flag=True, 
        help="Probabilities instead of counts")
@click.option("-z", "--compact", help="Compact display", is_flag=True)
@click.option("-y", "--tidy", help="Return tidy format", is_flag=True)
@click.option("-u", "--max", "_max", help="Maximum count value to show", type=int)
@click.option("-l", "--min", "_min", help="Minimum count value to show", type=int)
@handle_qc_errors
def crosstab(codes, settings, pattern, filenames, coders, depth, unit, recursive_codes,
        recursive_counts, expanded, _format, outfile, probs, compact, tidy, _max, _min):
    "Cross-tabulate code occurrences"
    if depth and not recursive_codes:
        msg = "--depth requires --recursive-codes"
        raise IncompatibleOptions(msg)
    if tidy and compact:
        msg = "--tidy and --compact are incompatible"
        raise IncompatibleOptions(msg)
    if tidy and probs:
        msg = "--tidy and --probs are incompatible"
        raise IncompatibleOptions(msg)
    if _min and not tidy:
        msg = "--min requires --tidy"
        raise IncompatibleOptions(msg)
    if _max and not tidy:
        msg = "--max requires --tidy"
        raise IncompatibleOptions(msg)

    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    corpus = QCCorpus(settings_path)
    viewer = QCCorpusViewer(corpus)
    if tidy:
        viewer.tidy_codes(
            codes, 
            depth=depth, 
            recursive_codes=recursive_codes,
            recursive_counts=recursive_counts,
            expanded=expanded, 
            format=_format, 
            pattern=pattern,
            file_list=read_file_list(filenames),
            coders=coders,
            unit=unit,
            outfile=outfile,
            minimum=_min,
            maximum=_max,
        )
    else:
        viewer.crosstab(
            codes, 
            depth=depth, 
            recursive_codes=recursive_codes,
            recursive_counts=recursive_counts,
            expanded=expanded, 
            format=_format, 
            pattern=pattern,
            file_list=read_file_list(filenames),
            coders=coders,
            unit=unit,
            outfile=outfile,
            probs=probs,
            compact=compact,
        )


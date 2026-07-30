import click
import os
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.views.viewer import QCCorpusViewer
from qualitative_coding.cli.decorators import handle_qc_errors
from qualitative_coding.helpers import read_file_list
from qualitative_coding.logs import configure_logger
from qualitative_coding.exceptions import IncompatibleOptions
from qualitative_coding.views.table_output import TABLE_FORMATS

@click.command(name="agreement")
@click.argument("codes", nargs=-1)
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@click.option("-c", "--coders", help="Coders to compare", multiple=True)
@click.option("--metric", default="alpha",
        type=click.Choice(["alpha", "kappa", "f1", "cv"]),
        help="Agreement metric: alpha, kappa, f1, or cv (cross-validation, requires embeddings)")
@click.option("--folds", default=5, type=int, help="Number of CV folds (with --metric cv)")
@click.option("-r", "--recursive-codes", "recursive_codes", is_flag=True,
        help="Include child codes")
@click.option("-d", "--depth", type=int, help="Maximum depth in code tree")
@click.option("-n", "--unit", default=None, help="Unit of analysis (default from settings)",
        type=click.Choice(['line', 'paragraph', 'document']))
@click.option("-p", "--pattern", help="Pattern to filter corpus filenames")
@click.option("-f", "--filenames", help="File path containing a list of filenames to use")
@click.option("-m", "--format", "_format", type=click.Choice(TABLE_FORMATS),
        metavar="[tabulate_formats|csv]", help="Output format")
@click.option("-o", "--outfile", help="Filename for CSV export")
@handle_qc_errors
def agreement(codes, settings, coders, metric, folds, recursive_codes, depth, unit, pattern,
              filenames, _format, outfile):
    "Compute inter-rater agreement between coders"
    if metric in ("kappa", "f1") and len(coders) != 2:
        raise IncompatibleOptions(f"--metric {metric} requires exactly two --coders")
    if metric == "cv" and unit is not None:
        raise IncompatibleOptions(
            "--unit is not supported with --metric cv; granularity is "
            "determined by the unit embeddings were generated with."
        )
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    log = configure_logger(settings_path)
    log.info("codes agreement", codes=codes, coders=coders, metric=metric,
             recursive_codes=recursive_codes, unit=unit, pattern=pattern)
    corpus = QCCorpus(settings_path)
    unit = unit or corpus.settings.get("unit", "line")
    viewer = QCCorpusViewer(corpus)
    viewer.show_agreement(
        codes=codes,
        coders=coders,
        metric=metric,
        recursive_codes=recursive_codes,
        depth=depth,
        unit=unit,
        pattern=pattern,
        file_list=read_file_list(filenames),
        format=_format,
        outfile=outfile,
        folds=folds,
    )

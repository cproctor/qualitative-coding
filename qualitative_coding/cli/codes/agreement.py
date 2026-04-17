import click
import os
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.views.viewer import QCCorpusViewer
from qualitative_coding.cli.decorators import handle_qc_errors
from qualitative_coding.helpers import read_file_list
from qualitative_coding.logs import configure_logger
from qualitative_coding.exceptions import IncompatibleOptions
from tabulate import tabulate_formats

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
@click.option("-p", "--pattern", help="Pattern to filter corpus filenames")
@click.option("-f", "--filenames", help="File path containing a list of filenames to use")
@click.option("-m", "--format", "_format", type=click.Choice(tabulate_formats),
        metavar="[tabulate_formats]", help="Output format")
@click.option("-o", "--outfile", help="Filename for CSV export")
@handle_qc_errors
def agreement(codes, settings, coders, metric, folds, recursive_codes, depth, pattern,
              filenames, _format, outfile):
    "Compute inter-rater agreement between coders"
    if metric in ("kappa", "f1") and len(coders) != 2:
        raise IncompatibleOptions(f"--metric {metric} requires exactly two --coders")
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    log = configure_logger(settings_path)
    log.info("codes agreement", codes=codes, coders=coders, metric=metric,
             recursive_codes=recursive_codes, pattern=pattern)
    corpus = QCCorpus(settings_path)
    viewer = QCCorpusViewer(corpus)
    viewer.show_agreement(
        codes=codes,
        coders=coders,
        metric=metric,
        recursive_codes=recursive_codes,
        depth=depth,
        pattern=pattern,
        file_list=read_file_list(filenames),
        format=_format,
        outfile=outfile,
        folds=folds,
    )

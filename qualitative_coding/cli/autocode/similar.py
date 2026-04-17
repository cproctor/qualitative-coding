import click
import os
from tabulate import tabulate, tabulate_formats
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.cli.decorators import handle_qc_errors
from qualitative_coding.helpers import read_file_list
from qualitative_coding.logs import configure_logger

@click.command()
@click.argument("codes", nargs=-1)
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@click.option("-c", "--coders", multiple=True, help="Filter by coder")
@click.option("--threshold", default=0.8, type=float,
              help="Minimum cosine similarity to report (default: 0.8)")
@click.option("-p", "--pattern", help="Pattern to filter corpus filenames")
@click.option("-f", "--filenames", help="File path containing a list of filenames")
@click.option("-m", "--format", "_format", type=click.Choice(tabulate_formats),
              metavar="[tabulate_formats]")
@handle_qc_errors
def similar(codes, settings, coders, threshold, pattern, filenames, _format):
    "Find pairs of codes with similar embedding centroids (merge candidates)"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    configure_logger(settings_path)
    corpus = QCCorpus(settings_path)

    from qualitative_coding.autocode.embedder import CorpusEmbedder
    from qualitative_coding.autocode.analytics import compute_similar

    embedder = CorpusEmbedder(corpus)
    filter_codes = list(codes) if codes else None

    pairs = compute_similar(
        corpus, embedder,
        codes=filter_codes,
        coders=list(coders) if coders else None,
        pattern=pattern,
        file_list=read_file_list(filenames),
        threshold=threshold,
    )

    if not pairs:
        click.echo(f"No code pairs found with cosine similarity >= {threshold}.")
        return

    click.echo(tabulate(pairs, ["Code A", "Code B", "Similarity"], tablefmt=_format))

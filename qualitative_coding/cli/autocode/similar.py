import click
import os
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.cli.decorators import handle_qc_errors
from qualitative_coding.helpers import read_file_list
from qualitative_coding.logs import configure_logger
from qualitative_coding.views.table_output import write_table, TABLE_FORMATS

@click.command()
@click.argument("codes", nargs=-1)
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@click.option("-c", "--coders", multiple=True, help="Filter by coder")
@click.option("--threshold", default=0.5, type=float,
              help="Minimum cross-classifier score to report (default: 0.5)")
@click.option("-p", "--pattern", help="Pattern to filter corpus filenames")
@click.option("-f", "--filenames", help="File path containing a list of filenames")
@click.option("-m", "--format", "_format", type=click.Choice(TABLE_FORMATS),
              metavar="[tabulate_formats|csv]")
@handle_qc_errors
def similar(codes, settings, coders, threshold, pattern, filenames, _format):
    "Find pairs of codes whose classifiers generalize to each other's examples"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    configure_logger(settings_path)
    corpus = QCCorpus(settings_path)

    from qualitative_coding.autocode.embedder import CorpusEmbedder
    from qualitative_coding.autocode.trainer import AutocodeTrainer
    from qualitative_coding.autocode.analytics import compute_similar

    embedder = CorpusEmbedder(corpus)
    filter_codes = list(codes) if codes else None

    trainer = AutocodeTrainer(corpus, embedder)
    classifiers = trainer.train(
        codes=filter_codes,
        coders=list(coders) if coders else None,
        pattern=pattern,
        file_list=read_file_list(filenames),
    )

    pairs = compute_similar(
        corpus, embedder, classifiers,
        codes=filter_codes,
        coders=list(coders) if coders else None,
        pattern=pattern,
        file_list=read_file_list(filenames),
        threshold=threshold,
    )

    if not pairs:
        click.echo(f"No code pairs found with cross-classifier score >= {threshold}.")
        return

    write_table(pairs, ["Code A", "Code B", "P(B | A examples)", "P(A | B examples)"],
                format=_format)

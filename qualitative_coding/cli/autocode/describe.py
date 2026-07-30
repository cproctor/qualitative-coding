import click
import os
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.cli.decorators import handle_qc_errors
from qualitative_coding.helpers import read_file_list
from qualitative_coding.logs import configure_logger
from qualitative_coding.autocode.settings import get_autocode_settings
from qualitative_coding.views.table_output import write_table, is_raw_output, TABLE_FORMATS

@click.command()
@click.argument("codes", nargs=-1)
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@click.option("-c", "--coders", multiple=True, help="Training coders")
@click.option("-r", "--recursive-codes", "recursive_codes", is_flag=True,
              help="Include child codes")
@click.option("-p", "--pattern", help="Pattern to filter corpus filenames")
@click.option("-f", "--filenames", help="File path containing a list of filenames")
@click.option("-m", "--format", "_format", type=click.Choice(TABLE_FORMATS),
              metavar="[tabulate_formats|csv]", help="Output format")
@click.option("-o", "--outfile", help="Filename for CSV export")
@handle_qc_errors
def describe(codes, settings, coders, recursive_codes, pattern, filenames,
             _format, outfile):
    "Describe the autocode model configuration and per-code training statistics"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    log = configure_logger(settings_path)
    log.info("autocode describe", codes=codes, coders=coders)
    corpus = QCCorpus(settings_path)
    ac = get_autocode_settings(corpus.settings)

    # Print hyperparameters
    click.echo("Hyperparameters:")
    click.echo(f"  unit: {corpus.settings.get('unit', 'line')}")
    for key in [
        "api_base", "api_model", "window",
        "min_examples", "confidence_threshold",
        "child_threshold", "embeddings_dir",
    ]:
        click.echo(f"  autocode.{key}: {ac[key]}")
    click.echo()

    from qualitative_coding.autocode.embedder import CorpusEmbedder
    from qualitative_coding.autocode.trainer import AutocodeTrainer
    embedder = CorpusEmbedder(corpus)
    trainer = AutocodeTrainer(corpus, embedder)

    if codes and recursive_codes:
        with corpus.session():
            tree = corpus.get_codebook()
        nodes = sum([tree.find(c) for c in codes], [])
        expanded = sum([n.flatten(names=True) for n in nodes], [])
        filter_codes = expanded
    else:
        filter_codes = list(codes) if codes else None

    stats = trainer.describe(
        codes=filter_codes,
        coders=list(coders) if coders else None,
        pattern=pattern,
        file_list=read_file_list(filenames),
    )

    rows = []
    for code_name, info in sorted(stats.items()):
        rows.append([
            code_name,
            info["positive_examples"],
            info["status"],
        ])

    cols = ["Code", "Examples", "Status"]
    if not is_raw_output(_format, outfile):
        click.echo("Per-code training statistics:")
    write_table(rows, cols, format=_format, outfile=outfile)

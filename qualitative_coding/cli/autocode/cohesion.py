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
@click.option("-r", "--recursive-codes", "recursive_codes", is_flag=True)
@click.option("-p", "--pattern", help="Pattern to filter corpus filenames")
@click.option("-f", "--filenames", help="File path containing a list of filenames")
@click.option("-m", "--format", "_format", type=click.Choice(TABLE_FORMATS),
              metavar="[tabulate_formats|csv]")
@handle_qc_errors
def cohesion(codes, settings, coders, recursive_codes, pattern, filenames, _format):
    "Report per-code embedding cohesion (variance explained by first principal component)"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    configure_logger(settings_path)
    corpus = QCCorpus(settings_path)

    from qualitative_coding.autocode.embedder import CorpusEmbedder
    from qualitative_coding.autocode.analytics import compute_cohesion

    embedder = CorpusEmbedder(corpus)

    if codes and recursive_codes:
        with corpus.session():
            tree = corpus.get_codebook()
        nodes = sum([tree.find(c) for c in codes], [])
        filter_codes = sum([n.flatten(names=True) for n in nodes], [])
    else:
        filter_codes = list(codes) if codes else None

    result = compute_cohesion(
        corpus, embedder,
        codes=filter_codes,
        coders=list(coders) if coders else None,
        pattern=pattern,
        file_list=read_file_list(filenames),
    )

    rows = [
        [name, info["examples"], info["variance_explained"] or "—", info["suggestion"]]
        for name, info in sorted(result.items())
    ]
    write_table(rows, ["Code", "Examples", "Variance Explained", "Suggestion"],
                format=_format)

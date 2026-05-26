import click
import os
from tabulate import tabulate
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.cli.decorators import handle_qc_errors
from qualitative_coding.helpers import read_file_list
from qualitative_coding.logs import configure_logger

@click.command()
@click.argument("codes", nargs=-1)
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@click.option("-c", "--coders", multiple=True, help="Filter by coder")
@click.option("-n", "--top-n", "top_n", default=5, type=int,
              help="Number of outliers to show per code")
@click.option("-r", "--recursive-codes", "recursive_codes", is_flag=True)
@click.option("-p", "--pattern", help="Pattern to filter corpus filenames")
@click.option("-f", "--filenames", help="File path containing a list of filenames")
@handle_qc_errors
def outliers(codes, settings, coders, top_n, recursive_codes, pattern, filenames):
    "Find coded lines that are outliers for their code (lowest classifier confidence)"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    configure_logger(settings_path)
    corpus = QCCorpus(settings_path)

    from qualitative_coding.autocode.embedder import CorpusEmbedder
    from qualitative_coding.autocode.trainer import AutocodeTrainer
    from qualitative_coding.autocode.analytics import compute_outliers

    embedder = CorpusEmbedder(corpus)

    if codes and recursive_codes:
        with corpus.session():
            tree = corpus.get_codebook()
        nodes = sum([tree.find(c) for c in codes], [])
        filter_codes = sum([n.flatten(names=True) for n in nodes], [])
    else:
        filter_codes = list(codes) if codes else None

    trainer = AutocodeTrainer(corpus, embedder)
    classifiers = trainer.train(
        codes=filter_codes,
        coders=list(coders) if coders else None,
        pattern=pattern,
        file_list=read_file_list(filenames),
    )

    result = compute_outliers(
        corpus, embedder, classifiers,
        codes=filter_codes,
        coders=list(coders) if coders else None,
        pattern=pattern,
        file_list=read_file_list(filenames),
        n=top_n,
    )

    for code_name in sorted(result):
        click.echo(f"\n{code_name} — {top_n} least confident positives:")
        rows = []
        for doc_id, line, confidence in result[code_name]:
            corpus_path = corpus.corpus_dir / doc_id
            all_lines = corpus_path.read_text().splitlines()
            text = all_lines[line][:60] if line < len(all_lines) else ""
            rows.append([doc_id, line, round(confidence, 3), text])
        click.echo(tabulate(rows, ["Document", "Line", "Confidence", "Text"],
                            tablefmt="simple"))

import click
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.cli.decorators import (
    handle_qc_errors,
)

@click.command()
@click.option("-s", "--settings", default="settings.yaml", type=click.Path(exists=True),
        help="Settings file")
@handle_qc_errors
def check(settings):
    "Check project for errors"
    corpus = QCCorpus(settings)
    with corpus.session():
        corpus.validate_corpus_paths()

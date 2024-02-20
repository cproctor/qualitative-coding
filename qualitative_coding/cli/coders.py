import click
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.cli.decorators import handle_qc_errors

@click.command()
@click.option("-s", "--settings", default="settings.yaml", help="Settings file")
@handle_qc_errors
def coders(settings):
    "List all coders"
    corpus = QCCorpus(settings)
    with corpus.session():
        for coder in corpus.get_all_coders():
            print(coder.name)



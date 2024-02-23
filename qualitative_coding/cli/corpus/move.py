import click
from qualitative_coding.corpus import QCCorpus

@click.command()
@click.argument("target")
@click.argument("destination")
@click.option("-s", "--settings", default="settings.yaml", help="Settings file")
@click.option("-r", "--recursive", is_flag=True, 
        help="Recursively import from directory")
def move(target, destination, settings, recursive):
    "Move a file in the corpus"
    corpus = QCCorpus(settings)
    with corpus.session():
        corpus.move_document(target, destination, recursive=recursive)

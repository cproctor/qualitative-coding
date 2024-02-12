import click
import yaml
from pathlib import Path
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.views.viewer import QCCorpusViewer
from qualitative_coding.cli.decorators import handle_qc_errors

@click.command()
@click.argument("coder")
@click.option("-s", "--settings", default="settings.yaml", type=click.Path(exists=True),
        help="Settings file")
@click.option("-m", "--message", help="short message, title of memo file")
@click.option("-l", "--list", "list_memos", is_flag=True,
        help="list all memos in order")
@handle_qc_errors
def memo(coder, settings, message, list_memos):
    "Write a memo"
    s = yaml.safe_load(Path(settings).read_text())
    corpus = QCCorpus(s)
    viewer = QCCorpusViewer(corpus)
    if list_memos:
        click.echo(viewer.list_memos())
    else:
        viewer.memo(coder, message)
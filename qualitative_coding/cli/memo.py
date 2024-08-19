import click
import os
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.views.viewer import QCCorpusViewer
from qualitative_coding.cli.decorators import handle_qc_errors
from qualitative_coding.logs import configure_logger

@click.command()
@click.argument("coder")
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@click.option("-m", "--message", help="short message, title of memo file")
@click.option("-l", "--list", "list_memos", is_flag=True,
        help="list all memos in order")
@handle_qc_errors
def memo(coder, settings, message, list_memos):
    "Write a memo"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    log = configure_logger(settings_path)
    log.info("memo", coder=coder, message=message, list_memos=list_memos)
    corpus = QCCorpus(settings_path)
    viewer = QCCorpusViewer(corpus)
    if list_memos:
        click.echo(viewer.list_memos())
    else:
        viewer.memo(coder, message)

import click
import os
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.views.viewer import QCCorpusViewer
from qualitative_coding.logs import configure_logger

@click.command(name="list")
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@click.option("-e", "--expanded", is_flag=True, help="Show names of parent codes")
@click.option("-d", "--depth", help="Maximum depth in code tree", type=int)
def _list(settings, expanded, depth):
    "List all codes"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    log = configure_logger(settings_path)
    log.info("codes list", expanded=expanded, depth=depth)
    corpus = QCCorpus(settings_path)
    viewer = QCCorpusViewer(corpus)
    viewer.list_codes(expanded=expanded, depth=depth)

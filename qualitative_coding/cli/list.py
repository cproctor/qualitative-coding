import click
import yaml
from pathlib import Path
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.views.viewer import QCCorpusViewer

@click.command(name="list")
@click.option("-s", "--settings", default="settings.yaml", type=click.Path(exists=True),
        help="Settings file")
@click.option("-e", "--expanded", is_flag=True, help="Show names of parent codes")
@click.option("-d", "--depth", help="Maximum depth in code tree", type=int)
def _list(settings, expanded, depth):
    "List all codes"
    s = yaml.safe_load(Path(settings).read_text())
    corpus = QCCorpus(s)
    viewer = QCCorpusViewer(corpus)
    viewer.list_codes(expanded=expanded, depth=depth)

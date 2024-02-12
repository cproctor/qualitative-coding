import click
import yaml
from pathlib import Path
from qualitative_coding.corpus import QCCorpus

@click.command()
@click.option("-s", "--settings", default="settings.yaml", help="Settings file")
def coders(settings):
    "List all coders"
    s = yaml.safe_load(Path(settings).read_text())
    corpus = QCCorpus(s)
    with corpus.session():
        for coder in corpus.get_all_coders():
            print(coder)



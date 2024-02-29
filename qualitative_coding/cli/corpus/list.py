import click
import os
from qualitative_coding.corpus import QCCorpus
from pathlib import Path

@click.command(name="list")
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
def list_corpus_paths(settings):
    "List corpus paths"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    corpus = QCCorpus(settings_path)
    paths = []
    for dir_path, dirs, filenames in os.walk(corpus.corpus_dir):
        for fn in filenames:
            paths.append(Path(dir_path).relative_to(corpus.corpus_dir) / fn)
    for path in sorted(paths):
        print(path)

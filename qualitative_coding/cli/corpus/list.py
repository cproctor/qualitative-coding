import click
import os
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.helpers import read_file_list
from qualitative_coding.logs import configure_logger
from pathlib import Path

@click.command(name="list")
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@click.option("-p", "--pattern", 
        help="Pattern to filter corpus filenames (glob-style)")
@click.option("-f", "--filenames", 
        help="File path containing a list of filenames to use")
def list_corpus_paths(settings, pattern, filenames):
    "List corpus paths"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    log = configure_logger(settings_path)
    log.info("corpus list", pattern=pattern, filenames=filenames)
    corpus = QCCorpus(settings_path)
    paths = []
    for dir_path, dirs, fns in os.walk(corpus.corpus_dir):
        for fn in fns:
            paths.append(str(Path(dir_path).relative_to(corpus.corpus_dir) / fn))
    if pattern:
        paths = [path for path in paths if pattern in path]
    if filenames:
        file_list = read_file_list(filenames)
        paths = [path for path in paths if path in file_list]
    for path in sorted(paths):
        print(path)

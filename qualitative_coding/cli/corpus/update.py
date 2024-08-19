import os
import click
from pathlib import Path
from subprocess import run
from collections import defaultdict
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.diff import (
    get_diff, 
    get_git_diff,
    reindex_coded_lines,
)
from qualitative_coding.exceptions import IncompatibleOptions, QCError, InvalidParameter
from qualitative_coding.cli.decorators import handle_qc_errors
from qualitative_coding.logs import configure_logger

@click.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@click.option("-n", "--new", type=click.Path(exists=True), help="Path to new version")
@click.option("-r", "--recursive", is_flag=True, 
        help="Recursively import from directory")
@click.option("-d", "--dryrun", is_flag=True, 
        help="Show simulated results")
@handle_qc_errors
def update(file_path, settings, new, recursive, dryrun):
    "Update the content of corpus files"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    log = configure_logger(settings_path)
    log.info("corpus update", new=new, recursive=recursive, dryrun=dryrun)
    corpus = QCCorpus(settings_path)
    if recursive:
        raise QCError("recursive is not yet implemented.")
    if new:
        log.debug("Using new file comparison diff strategy")
        if not Path(new).exists():
            raise InvalidParameter(f"new path {new} does not exist")
        diff = get_diff(file_path, new)
    else:
        log.debug("Using git diff strategy")
        if not in_git_repo():
            raise QCError("update with git strategy can only be used within a git repository")
        diff = get_git_diff(file_path)
    with corpus.session():
        corpus_path = str(corpus.get_corpus_path(file_path))
        coded_lines = corpus.get_coded_lines(file_list=[corpus_path])
        reindexed_coded_lines = reindex_coded_lines(coded_lines, diff)
        coded_lines_by_file_by_coder = defaultdict(lambda: defaultdict(list))
        for code, coder, line, file_path in reindexed_coded_lines:
            coded_lines_by_file_by_coder[file_path][coder].append({
                'line': line, 
                'code_id': code,
            })
        if dryrun:
            print(diff)
        else:
            if new:
                (corpus.corpus_dir / corpus_path).write_text(Path(new).read_text())
            for file_path, lines_by_coder in coded_lines_by_file_by_coder.items():
                for coder, lines in lines_by_coder.items():
                    corpus.update_coded_lines(file_path, coder, lines)

def in_git_repo():
    "Checks whether the current working directory is in a git repo."
    return run("git status", shell=True, capture_output=True).returncode == 0

import click
import os
from qualitative_coding.cli.decorators import handle_qc_errors
from qualitative_coding.logs import configure_logger
from os import getcwd
from pathlib import Path


def _ensure_gitignore_entry(project_root, entry):
    """Add `entry` to .gitignore in project_root if not already present."""
    gitignore = Path(project_root) / ".gitignore"
    entry_line = entry.rstrip("/") + "/"
    if gitignore.exists():
        content = gitignore.read_text()
        if entry_line not in content.splitlines():
            gitignore.write_text(content.rstrip() + "\n" + entry_line + "\n")
    else:
        gitignore.write_text(entry_line + "\n")

@click.command()
@click.option("-s", "--settings", type=click.Path(), help="Settings file")
@click.option("-w", "--write-settings-file", is_flag=True, help="Create a settings file but do not create directories")
@click.option("-i", "--import", "_import", help="Import an existing qdpx project")
@handle_qc_errors
def init(settings, write_settings_file, _import):
    "Initialize a qc project"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    if _import:
        from qualitative_coding.refi_qda.reader import REFIQDAReader
        reader = REFIQDAReader(_import)
        reader.unpack_project(Path.cwd())
    else:
        log = configure_logger(settings_path)
        log.info("init", write_settings_file=write_settings_file)
        from qualitative_coding.corpus import QCCorpus
        QCCorpus.initialize(settings_path, write_settings_file)
        if not write_settings_file:
            _ensure_gitignore_entry(Path(settings_path).parent, "embeddings/")

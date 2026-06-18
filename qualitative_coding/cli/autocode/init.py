import click
import os
import yaml
from pathlib import Path
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.cli.decorators import handle_qc_errors
from qualitative_coding.cli.init import _ensure_gitignore_entry
from qualitative_coding.logs import configure_logger
from qualitative_coding.helpers import read_settings
from qualitative_coding.autocode.settings import get_autocode_settings

@click.command(name="init")
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@handle_qc_errors
def autocode_init(settings):
    "Interactively configure the [autocode] settings table"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    log = configure_logger(settings_path)
    log.info("autocode init")
    corpus = QCCorpus(settings_path)
    ac = get_autocode_settings(corpus.settings)

    click.echo("Configuring autocode settings. Press Enter to accept each default.")
    click.echo()

    embeddings_dir = click.prompt(
        "Directory for cached embeddings", default=ac["embeddings_dir"]
    )
    window_before = click.prompt(
        "Lines of context before each line (window)",
        default=ac["window"][0], type=int,
    )
    window_after = click.prompt(
        "Lines of context after each line (window)",
        default=ac["window"][1], type=int,
    )
    min_examples = click.prompt(
        "Minimum positive examples required to train a classifier for a code",
        default=ac["min_examples"], type=int,
    )
    confidence_threshold = click.prompt(
        "Minimum confidence required to write a prediction",
        default=ac["confidence_threshold"], type=float,
    )
    child_threshold = click.prompt(
        "Minimum confidence required to prefer a child code over its parent",
        default=ac["child_threshold"], type=float,
    )
    api_base = click.prompt(
        "Base URL for the OpenAI-compatible embedding API", default=ac["api_base"]
    )
    api_key = click.prompt(
        "API key for the embedding service (blank for local servers)",
        default=ac["api_key"], show_default=False,
    )
    api_model = click.prompt(
        "Embedding model name on the configured server", default=ac["api_model"]
    )

    settings_data = read_settings(settings_path)
    settings_data["autocode"] = {
        "embeddings_dir": embeddings_dir,
        "window": [window_before, window_after],
        "min_examples": min_examples,
        "confidence_threshold": confidence_threshold,
        "child_threshold": child_threshold,
        "api_base": api_base,
        "api_key": api_key,
        "api_model": api_model,
    }
    Path(settings_path).write_text(yaml.dump(settings_data))
    _ensure_gitignore_entry(Path(settings_path).parent, embeddings_dir)

    click.echo()
    click.echo(f"Wrote autocode settings to {settings_path}.")
    click.echo("Run `qc autocode embed` next to generate embeddings for your corpus.")

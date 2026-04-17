import click
import os
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.cli.decorators import handle_qc_errors
from qualitative_coding.helpers import read_file_list
from qualitative_coding.logs import configure_logger

@click.command()
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@click.option("--force", is_flag=True, help="Re-embed even if cache is valid")
@click.option("-p", "--pattern", help="Pattern to filter corpus filenames")
@click.option("-f", "--filenames", help="File path containing a list of filenames")
@handle_qc_errors
def embed(settings, force, pattern, filenames):
    "Generate and cache embeddings for corpus documents"
    from qualitative_coding.autocode.embedder import CorpusEmbedder
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    log = configure_logger(settings_path)
    log.info("autocode embed", force=force, pattern=pattern)
    corpus = QCCorpus(settings_path)
    embedder = CorpusEmbedder(corpus)
    n = embedder.embed_corpus(
        force=force,
        pattern=pattern,
        file_list=read_file_list(filenames),
    )
    click.echo(f"Embedded {n} lines. Cache saved to {embedder.embeddings_dir}.")
    gitignore = corpus.settings_path.parent / ".gitignore"
    embeddings_rel = embedder.embeddings_dir.relative_to(corpus.settings_path.parent)
    if gitignore.exists():
        content = gitignore.read_text()
        if str(embeddings_rel) not in content:
            click.echo(
                f"Tip: add '{embeddings_rel}/' to .gitignore to exclude embeddings "
                "from version control."
            )
    else:
        click.echo(
            f"Tip: add '{embeddings_rel}/' to .gitignore to exclude embeddings "
            "from version control."
        )

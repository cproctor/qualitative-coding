import click
import os
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.cli.click_aliases import ClickAliasedGroup
from qualitative_coding.cli.decorators import handle_qc_errors
from qualitative_coding.logs import configure_logger

@click.group(name="coders", cls=ClickAliasedGroup, invoke_without_command=True)
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@click.pass_context
def coders(ctx, settings):
    "List or manage coders"
    if ctx.invoked_subcommand is None:
        settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
        configure_logger(settings_path)
        corpus = QCCorpus(settings_path)
        with corpus.session():
            for coder in corpus.get_all_coders():
                print(coder.name)

@coders.command()
@click.argument("coder")
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@handle_qc_errors
def delete(coder, settings):
    "Delete a coder and all their coded lines"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    log = configure_logger(settings_path)
    log.info("coders delete", coder=coder)
    corpus = QCCorpus(settings_path)
    with corpus.session():
        corpus.delete_coder(coder)
    click.echo(f"Deleted coder {coder!r} and all their coded lines.")

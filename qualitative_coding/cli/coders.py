import click
import os
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.cli.decorators import handle_qc_errors

@click.command()
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@click.option("-d", "--delete", help="Delete a coder")
@handle_qc_errors
def coders(settings, delete):
    "List all coders"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    corpus = QCCorpus(settings_path)
    with corpus.session():
        if delete:
            corpus.delete_coder(delete)
        else:
            for coder in corpus.get_all_coders():
                print(coder.name)



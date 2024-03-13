import click
import os
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.helpers import read_file_list

@click.command()
@click.argument("old_codes", nargs=-1)
@click.argument("new_code")
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@click.option("-c", "--coders", help="Coders", multiple=True)
@click.option("-p", "--pattern", 
        help="Pattern to filter corpus filenames (glob-style)")
@click.option("-f", "--filenames", 
        help="File path containing a list of filenames to use")
def rename(old_codes, new_code, settings, coders, pattern, filenames):
    "Rename one or more codes"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    corpus = QCCorpus(settings_path)
    with corpus.session():
        corpus.rename_codes(
            old_codes=old_codes, 
            new_code=new_code, 
            pattern=pattern,
            file_list=read_file_list(filenames),
            coders=coders,
        )

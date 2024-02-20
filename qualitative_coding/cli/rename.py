import click
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.helpers import read_file_list

@click.command()
@click.argument("old_codes", nargs=-1)
@click.argument("new_code")
@click.option("-s", "--settings", default="settings.yaml", type=click.Path(exists=True),
        help="Settings file")
@click.option("-c", "--coder", help="Coder")
@click.option("-p", "--pattern", 
        help="Pattern to filter corpus filenames (glob-style)")
@click.option("-f", "--filenames", 
        help="File path containing a list of filenames to use")
def rename(old_codes, new_code, settings, coder, pattern, filenames):
    "Rename one or more codes"
    corpus = QCCorpus(settings)
    with corpus.session():
        corpus.rename_codes(
            old_codes=old_codes, 
            new_code=new_code, 
            pattern=pattern,
            file_list=read_file_list(filenames),
            coder=coder,
        )

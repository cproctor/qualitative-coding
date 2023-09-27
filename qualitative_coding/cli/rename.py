import click
from qualitative_coding.corpus import QCCorpus

@click.command()
@click.argument("old_codes", nargs=-1)
@click.argument("new_code")
@click.option("-s", "--settings", default="settings.yaml", type=click.Path(exists=True),
        help="Settings file")
@click.option("-u", "--update_codebook", is_flag=True,
        help="force update codebook (even if renaming is scoped)")
@click.option("-c", "--coder", help="Coder")
@click.option("-p", "--pattern", 
        help="Pattern to filter corpus filenames (glob-style)")
@click.option("-f", "--filenames", 
        help="File path containing a list of filenames to use")
@click.option("-i", "--invert", is_flag=True, help="Invert file selection")
def rename(old_codes, new_code, settings, update_codebook, coder,
        pattern, filenames, invert):
    "Rename one or more codes"
    if invert and not (pattern or filenames):
        msg = "--invert may only be used when --pattern or --filenames is given."
        raise IncompatibleOptions(msg)
    if filenames:
        file_list = Path(args.filenames).read_text().split("\n")
    else:
        file_list = None
    corpus = QCCorpus(settings)
    corpus.rename_codes(
        old_codes=old_codes, 
        new_code=new_code, 
        pattern=pattern,
        file_list=file_list,
        invert=invert,
        coder=coder,
        update_codebook=update_codebook,
    )

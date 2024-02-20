import click
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.views.viewer import QCCorpusViewer
from qualitative_coding.cli.decorators import handle_qc_errors
from qualitative_coding.helpers import read_file_list

@click.command()
@click.argument("code", nargs=-1)
@click.option("-s", "--settings", default="settings.yaml", help="Settings file")
@click.option("-p", "--pattern", 
        help="Pattern to filter corpus filenames (glob-style)")
@click.option("-f", "--filenames", 
        help="File path containing a list of filenames to use")
@click.option("-c", "--coder", help="Coder")
@click.option("-d", "--depth", help="Maximum depth in code tree", type=int)
@click.option("-n", "--unit", default="line", help="Unit of analysis",
        type=click.Choice(['line', 'paragraph', 'document']))
@click.option("-r", "--recursive-codes", "recursive_codes", is_flag=True, 
        help="Include child codes")
@click.option("-B", "--before", default=2, type=int, 
        help="Number of lines before the code to show")
@click.option("-C", "--after", default=2, type=int, 
        help="Number of lines after the code to show")
@click.option("-l", "--no-codes", "no_codes", is_flag=True,
        help="Do not show matching codes")
@handle_qc_errors
def find(code, settings, pattern, filenames, coder, depth, unit, recursive_codes, 
         before, after, no_codes):
    "Find all coded text"
    corpus = QCCorpus(settings)
    viewer = QCCorpusViewer(corpus)
    viewer.show_coded_text(
        code, 
        before=before, 
        after=after, 
        recursive_codes=recursive_codes,
        depth=depth,
        unit=unit,
        pattern=pattern,
        file_list=read_file_list(filenames),
        coder=coder,
        show_codes=not no_codes,
    )


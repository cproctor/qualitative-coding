import click
import yaml
from pathlib import Path
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.views.viewer import QCCorpusViewer
from qualitative_coding.cli.decorators import handle_qc_errors
from qualitative_coding.exceptions import IncompatibleOptions
from tabulate import tabulate_formats

@click.command()
@click.argument("codes", nargs=-1)
@click.option("-s", "--settings", default="settings.yaml", help="Settings file")
@click.option("-p", "--pattern", 
        help="Pattern to filter corpus filenames (glob-style)")
@click.option("-f", "--filenames", 
        help="File path containing a list of filenames to use")
@click.option("-c", "--coder", help="Coder")
@click.option("-n", "--unit", default="line", help="Unit of analysis",
        type=click.Choice(['line', 'paragraph', 'document']))
@click.option("-r", "--recursive-codes", "recursive_codes", is_flag=True, 
        help="Include child codes")
@click.option("-a", "--recursive-counts", is_flag=True,
        help="Counts for codes include child codes")
def test(codes, settings, pattern, filenames, coder, unit, recursive_codes, recursive_counts):
    "Tests count_codes_by_unit functionality"

    # This stuff is standard for all tasks...
    s = yaml.safe_load(Path(settings).read_text())
    if filenames:
        file_list = Path(filenames).read_text().split("\n")
    else:
        file_list = None
    corpus = QCCorpus(s)

    # Currently not handled
    if recursive_codes or recursive_counts:
        raise NotImplemented(
            "We don't handle recursive tree traversal in the database. "
            "Therefore, for recursive_codes, you'll need to get all the child code sets" 
            "from the code tree (as in crosstab) and pass in the intersection of those sets "
            "so you look up all needed codes."
        )

    # Select which pre-existing function we want...
    if unit == "line": 
        fn = corpus.get_coded_lines
    elif unit == "paragraph":
        fn = corpus.get_coded_paragraphs
    else:
        fn = corpus.get_coded_documents

    # And run the query within an ORM session
    with corpus.session():
        result = fn(
            codes=codes,
            pattern=pattern,
            file_list=file_list, 
            coder=coder,
        )

    # In your function, you'll want to populate a (units, codes) matrix with the results
    print(result)

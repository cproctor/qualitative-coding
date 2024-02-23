import click
from qualitative_coding.cli.click_aliases import ClickAliasedGroup
from qualitative_coding.cli.corpus.list import list_corpus_paths
from qualitative_coding.cli.corpus.import_media import import_media
from qualitative_coding.cli.corpus.move import move

@click.group(name="corpus", cls=ClickAliasedGroup)
def corpus_group():
    "Corpus commands"

corpus_group.add_command(list_corpus_paths)
corpus_group.add_command(move, aliases=["mv"])
corpus_group.add_command(import_media)

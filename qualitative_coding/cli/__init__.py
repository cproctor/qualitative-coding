import click
from qualitative_coding.cli.click_aliases import ClickAliasedGroup
from qualitative_coding.cli.init import init
from qualitative_coding.cli.export import export
from qualitative_coding.cli.corpus import corpus_group
from qualitative_coding.cli.codes import codes_group
from qualitative_coding.cli.version import version
from qualitative_coding.cli.check import check
from qualitative_coding.cli.codebook import codebook
from qualitative_coding.cli.code import code
from qualitative_coding.cli.coders import coders
from qualitative_coding.cli.memo import memo
from qualitative_coding.cli.upgrade import upgrade

@click.group(cls=ClickAliasedGroup)
def cli():
    "Qualitative coding for computer scientists"

cli.add_command(init)
cli.add_command(export)
cli.add_command(corpus_group)
cli.add_command(codes_group)
cli.add_command(version)
cli.add_command(check)
cli.add_command(codebook, aliases=["cb"])
cli.add_command(code)
cli.add_command(coders)
cli.add_command(memo)
cli.add_command(upgrade)


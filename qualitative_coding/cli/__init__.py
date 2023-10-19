import click
from qualitative_coding.cli.click_aliases import ClickAliasedGroup
from qualitative_coding.cli.init import init
from qualitative_coding.cli.import_media import import_media
from qualitative_coding.cli.version import version
from qualitative_coding.cli.check import check
from qualitative_coding.cli.codebook import codebook
from qualitative_coding.cli.code import code
from qualitative_coding.cli.coders import coders
from qualitative_coding.cli.memo import memo
from qualitative_coding.cli.list import _list
from qualitative_coding.cli.rename import rename
from qualitative_coding.cli.find import find
from qualitative_coding.cli.stats import stats
from qualitative_coding.cli.crosstab import crosstab
from qualitative_coding.cli.upgrade import upgrade

@click.group(cls=ClickAliasedGroup)
def cli():
    "Qualitative coding for computer scientists"

cli.add_command(init)
cli.add_command(import_media)
cli.add_command(version)
cli.add_command(check)
cli.add_command(codebook, aliases=["cb"])
cli.add_command(code)
cli.add_command(coders)
cli.add_command(memo)
cli.add_command(_list, aliases=["ls"])
cli.add_command(rename, aliases=["rn"])
cli.add_command(find)
cli.add_command(stats)
cli.add_command(crosstab, aliases=["ct"])
cli.add_command(upgrade)


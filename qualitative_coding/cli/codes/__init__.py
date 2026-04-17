import click
from qualitative_coding.cli.click_aliases import ClickAliasedGroup
from qualitative_coding.cli.codes.stats import stats
from qualitative_coding.cli.codes.list import _list
from qualitative_coding.cli.codes.rename import rename
from qualitative_coding.cli.codes.crosstab import crosstab
from qualitative_coding.cli.codes.find import find
from qualitative_coding.cli.codes.agreement import agreement

@click.group(name="codes", cls=ClickAliasedGroup)
def codes_group():
    "Codes commands"

codes_group.add_command(agreement, aliases=["irr"])
codes_group.add_command(crosstab, aliases=["ct"])
codes_group.add_command(find)
codes_group.add_command(_list, aliases=['ls'])
codes_group.add_command(rename, aliases=["rn"])
codes_group.add_command(stats)


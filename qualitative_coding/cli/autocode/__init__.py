import click
from qualitative_coding.cli.click_aliases import ClickAliasedGroup
from qualitative_coding.cli.autocode.init import autocode_init
from qualitative_coding.cli.autocode.embed import embed
from qualitative_coding.cli.autocode.describe import describe
from qualitative_coding.cli.autocode.interactive import autocode_interactive
from qualitative_coding.cli.autocode.outliers import outliers
from qualitative_coding.cli.autocode.cohesion import cohesion
from qualitative_coding.cli.autocode.similar import similar

class AutocodeGroup(ClickAliasedGroup):
    """A group whose first positional argument is normally a coder name
    (dispatching to the hidden `interactive` command), but which still
    supports ordinary subcommands like `embed` and `describe`.
    """
    default_command = "interactive"

    def parse_args(self, ctx, args):
        known = set(self.list_commands(ctx)) | set(self._aliases)
        if args and args[0] not in known and args[0] not in ("-h", "--help"):
            args = [self.default_command, *args]
        return super().parse_args(ctx, args)

@click.group(name="autocode", cls=AutocodeGroup)
def autocode_group():
    "AI-assisted autocoding commands (qc autocode CODER for interactive loop)"

autocode_interactive.hidden = True
autocode_group.add_command(autocode_interactive)
autocode_group.add_command(autocode_init)
autocode_group.add_command(embed)
autocode_group.add_command(describe)
autocode_group.add_command(outliers)
autocode_group.add_command(cohesion)
autocode_group.add_command(similar)

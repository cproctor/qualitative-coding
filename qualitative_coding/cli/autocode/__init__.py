import click
from qualitative_coding.cli.click_aliases import ClickAliasedGroup
from qualitative_coding.cli.autocode.embed import embed
from qualitative_coding.cli.autocode.describe import describe
from qualitative_coding.cli.autocode.interactive import autocode_interactive
from qualitative_coding.cli.autocode.outliers import outliers
from qualitative_coding.cli.autocode.density import density
from qualitative_coding.cli.autocode.similar import similar

@click.group(name="autocode", cls=ClickAliasedGroup, invoke_without_command=True)
@click.argument("coder", required=False)
@click.argument("codes", nargs=-1)
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@click.option("-c", "--train-coders", "train_coders", multiple=True,
              help="Coders whose coding to use for training")
@click.option("--context", "context_lines", default=3, type=int,
              help="Lines of context to show around each target line")
@click.option("--uncertainty-threshold", "uncertainty_threshold", default=0.1,
              type=float)
@click.option("-p", "--pattern", help="Pattern to filter corpus filenames")
@click.option("-f", "--filenames", help="File path containing a list of filenames")
@click.pass_context
def autocode_group(ctx, coder, codes, settings, train_coders, context_lines,
                   uncertainty_threshold, pattern, filenames):
    "AI-assisted autocoding commands (qc autocode CODER for interactive loop)"
    if ctx.invoked_subcommand is None:
        if coder is None:
            click.echo(ctx.get_help())
            return
        ctx.invoke(
            autocode_interactive,
            coder=coder,
            codes=codes,
            settings=settings,
            train_coders=train_coders,
            context_lines=context_lines,
            uncertainty_threshold=uncertainty_threshold,
            pattern=pattern,
            filenames=filenames,
        )

autocode_group.add_command(embed)
autocode_group.add_command(describe)
autocode_group.add_command(outliers)
autocode_group.add_command(density)
autocode_group.add_command(similar)

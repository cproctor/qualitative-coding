import click
from importlib.metadata import metadata

@click.command()
def version():
    "Show version number"
    version = metadata('qualitative-coding')['version']
    click.echo(f"qualitative-coding {version}")

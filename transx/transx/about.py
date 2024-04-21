import click
from . import utils
from . import cmd


@cmd.cli.command('version')
def command():
    click.echo(utils.version())


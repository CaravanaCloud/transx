import click
from . import utils
from . import cmd
from .logs import *

@cmd.cli.command('version')
def command():
    """Prints the version of transx."""
    info(utils.version())


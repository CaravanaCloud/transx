import click
from . import cmd
from .logs import *


@cmd.cli.command('logs')
def command():
    """Prints a few logs messages.""" 
    critical("This is an message at [%s] level", "critical")
    error("This is an message at [%s] level", "error")
    warning("This is an message at [%s] level", "warning")
    info("This is an message at [%s] level", "info")
    debug("This is an message at [%s] level", "debug")
    

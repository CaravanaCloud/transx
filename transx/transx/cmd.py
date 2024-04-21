import click
from .logs import debug


@click.group()
@click.option('--force/--no-force', default=False)
def cli(force):
    debug(f"Force mode is {'on' if force else 'off'}")

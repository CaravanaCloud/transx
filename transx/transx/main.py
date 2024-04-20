import click
from .about import version

@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    click.echo(f"Debug mode is {'on' if debug else 'off'}")

@cli.command()
def main():
    click.echo(version())

if __name__ == "__main__":
    main()

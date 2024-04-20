import click
from .utils import version

@click.command('version')
def print_version():
    print(version())

if __name__ == '__main__':
    print_version();


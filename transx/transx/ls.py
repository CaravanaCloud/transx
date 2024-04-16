import click
import logging
from pathlib import Path
from .config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)

def get_files(directory, glob_pattern):
    """
    Retrieve a list of files matching the glob pattern in the specified directory, recursively.
    """
    path = Path(directory)
    files = list(path.rglob(glob_pattern))
    return files

@click.command()
@click.option('--directory', default=None, help='Directory to search in')
@click.option('--glob_pattern', default=None, help='Glob pattern to filter files by')
def ls(directory, glob_pattern):
    """
    List all files matching the glob pattern in the specified directory, recursively.
    """
    directory = Config.resolve(Config.TRANSX_PATH, directory)
    glob_pattern = Config.resolve(Config.TRANSX_GLOB, glob_pattern)
    
    files = get_files(directory, glob_pattern)
    for file in files:
        click.echo(file)
    logging.info(f"Found {len(files)} files.")
    
if __name__ == '__main__':
    ls()

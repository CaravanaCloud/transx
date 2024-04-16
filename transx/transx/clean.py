import click
import logging
from pathlib import Path
from .config import Config


@click.command()
@click.option('--directory', default=None, help='Directory to search in')
def clean(directory):
    """Delete all .transx.json files in the specified directory."""
    logging.basicConfig(level=logging.INFO)
    directory = Config.resolve(Config.TRANSX_PATH, directory)

    logging.info(f"Cleaning up .transx.json files in {directory} ...")
    glob_pattern = "**/*.transx.json"
    path = Path(directory)
    files = list(path.rglob(glob_pattern))
    # delete all files
    logging.info(f"Deleting {len(files)} files...")
    for file_path in files:
        try:
            logging.info(f"Deleting {file_path}")
            file_path.unlink()
        except Exception as e:
            logging.error(f"Failed to delete {file_path}: {e}")
            raise
    logging.info(f"Deleted {len(files)} files.")
    
if __name__ == '__main__':
    clean()
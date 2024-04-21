import os
import json
from pathlib import Path
from .config import Config

def transx_path(directory):
    if not directory:
        directory = str(Path.cwd())
    return Config.resolve(Config.TRANSX_PATH, directory)

def find_metadata_files(directory):
    directory = transx_path(directory)
    glob_pattern = "**/*.transx.json"
    path = Path(directory)
    files = list(path.rglob(glob_pattern))
    return files

def find_metadata(directory):
    metadata = []
    for file in find_metadata_files():
        with open(file) as f:
            metadata.append(json.load(f))
    return metadata

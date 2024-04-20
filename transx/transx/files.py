import os
import json
from pathlib import Path
from .config import Config

def transx_path():
    cwd = Path.cwd()
    return Config.resolve(Config.TRANSX_PATH, cwd)

def find_metadata_files():
    directory = transx_path()
    glob_pattern = "**/*.transx.json"
    path = Path(directory)
    files = list(path.rglob(glob_pattern))
    return files

def find_metadata():
    metadata = []
    for file in find_metadata_files():
        with open(file) as f:
            metadata.append(json.load(f))
    return metadata

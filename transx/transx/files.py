import os
import json
from pathlib import Path
from .config import Config
from .utils import  *


def transx_path(directory):
    if not directory:
        directory = str(Path.cwd())
    return resolve(Config.TRANSX_PATH, directory)


def find_medias(directory):
    return find_glob(directory, "*.mp4")


def find_subtitles(directory):
    srts = find_glob(directory, "*.srt")
    vtts = find_glob(directory, "*.vtt")
    subs = srts + vtts
    return subs


def find_glob(directory, glob_pattern):
    directory = transx_path(directory)
    glob_pattern = glob_pattern
    path = Path(directory)
    files = list(path.rglob(glob_pattern))
    return files


def find_all(directory):
    videos = find_medias(directory)
    subs = find_subtitles(directory)
    result = videos + subs
    return result

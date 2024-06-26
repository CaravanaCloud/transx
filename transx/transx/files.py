import os
import json
from pathlib import Path
from .config import Config
from .utils import  *
from .utils import  *


def find_videos(directory):
    return find_glob(directory, "*.mp4")


def find_medias(directory):
    return find_glob(directory, "*.mp4")


def find_subtitles(directory):
    srts = find_srt(directory)
    vtts = find_vtt(directory)
    subs = srts + vtts
    return subs


def find_vtt(directory):
    return find_glob(directory, "*.vtt")


def find_srt(directory):
    return find_glob(directory, "*.srt")


def find_glob(directory, glob_pattern):

    directory = Config.MEDIA_PATH.resolve(directory)
    glob_pattern = glob_pattern
    path = Path(directory)
    files = list(path.rglob(glob_pattern))
    return files


def find_all(directory):
    videos = find_medias(directory)
    subs = find_subtitles(directory)
    result = videos + subs
    return result

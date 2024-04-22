import os
from enum import Enum, auto
from dynaconf import Dynaconf
from .logs import *
from . import cmd, terms
from pathlib import Path


_file_path = Path.cwd()
_root_path = _file_path
settings_files = [
    os.path.join(_root_path, "templates/config/transx.yaml"),
]

settings = Dynaconf(
    envvar_prefix="TRANSX",
    root_path=_root_path,
    settings_files=settings_files,
    environments=True,
    load_dotenv=True,
)


def get_setting(name):
    return settings.get(name)


def init():
    info("Initializing configuration.")
    info(str(settings))
    info("Configuration initialized.")


class Config(Enum):
    TRANSX_PATH = auto()
    TRANSX_BUCKET_NAME = auto()
    TRANSX_ROLE_NAME = auto()
    TRANSX_SOURCE_LANG = auto()
    TRANSX_TARGET_LANG = auto()
    VIMEO_CLIENT_ID = auto()
    VIMEO_ACCESS_TOKEN = auto()
    VIMEO_CLIENT_SECRET = auto()
    VIMEO_AUTH_URL = auto()
    VIMEO_TOKEN_URL = auto()


@cmd.cli.command("config")
def command():
    """Prints the current configuration."""
    for key in settings.keys():
        value = settings.get(key)
        info(f"{key}: {value}")
    terms = Config.terms(None)
    terms_count = len(terms) if terms else 0
    info(f"[{terms_count}] terms loaded.")

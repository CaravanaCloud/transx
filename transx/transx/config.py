from enum import Enum, auto
from dynaconf import Dynaconf
from .utils import *
from . import cmd, terms
from pathlib import Path


_file_path = Path.cwd()
_root_path = _file_path
settings_files = [
    os.path.join(_root_path, "templates/config/transx.yaml"),
]

_settings = Dynaconf(
    envvar_prefix="TRANSX",
    root_path=_root_path,
    settings_files=settings_files,
    environments=True,
    load_dotenv=True,
)


def get_setting(name):
    return _settings.get(name)


def init():
    info("Initializing configuration.")
    info(str(_settings))
    info("Configuration initialized.")


class Config(Enum):
    TRANSX_PATH = auto()
    S3_BUCKET_NAME = auto()

    @staticmethod
    def defaults():
        return {
            Config.TRANSX_PATH: ('TRANSX_PATH', '.'),
            Config.S3_BUCKET_NAME: ('S3_BUCKET_NAME', f'transx.s3.{datestamp()}'),
        }

    @staticmethod
    def resolve(setting, command_line_value):
        """
        Resolve the value of a setting with the priority:
        command-line option > dynaconf setting > static default.
        """
        if command_line_value is not None:
            return command_line_value
        if _settings.exists(setting.name):
            return _settings.get(setting.name)
        return Config.defaults()[setting][1]


@cmd.cli.command("config")
def command():
    """Prints the current configuration."""
    for key in _settings.keys():
        value = _settings.get(key)
        info(f"{key}: {value}")
    terms = Config.terms(None)
    terms_count = len(terms) if terms else 0
    info(f"[{terms_count}] terms loaded.")

from enum import Enum, auto
from dynaconf import Dynaconf
from .utils import *

settings = Dynaconf(
    envvar_prefix="TRANSX",
    root_path=".",
    settings_files=['settings.tom, "*.terms.yaml" '],
    environments=True,
    load_dotenv=True,
)

class Config(Enum):
    TRANSX_PATH = auto()
    TRANSX_GLOB = auto()
    S3_BUCKET_NAME = auto()

    @staticmethod
    def resolve(setting, command_line_value):
        """
        Resolve the value of a setting with the priority:
        command-line option > dynaconf setting > static default.
        """
        if command_line_value is not None:
            return command_line_value
        
        # Map Enum to dynaconf and static defaults
        defaults = {
            Config.TRANSX_PATH: ('TRANSX_PATH', '.'),
            Config.TRANSX_GLOB: ('TRANSX_GLOB', '**/*.mp4'),
            Config.S3_BUCKET_NAME: ('S3_BUCKET_NAME', f'transx.s3.{datestamp()}'),
        }
        
        setting_key, default_value = defaults[setting]
        return settings.get(setting_key, default_value)

# Example use within the config module
# resolved_path = Config.resolve(Config.TRANSX_PATH, None)

import os
from datetime import datetime
from enum import Enum, auto
from dynaconf import Dynaconf
from .logs import *
from . import terms_static
from . import cmd, terms
from pathlib import Path

_HERE = os.path.dirname(os.path.abspath(__file__))


_SETTINGS = [
    os.path.join(_HERE, "config.transx.yaml"),
    os.path.join(_HERE, "terms.transx.yaml"),
    os.path.join(_HERE, "*.transx.yaml"),
    "*.transx.yaml"
]

settings = Dynaconf(
    envvar_prefix="TX",
    settings_files=_SETTINGS,
    load_dotenv=True,
)


#TODO: Document which settings are required
_now = datetime.now()
_now_str = _now.strftime('%Y%m%d_%H%M%S')
_today_str = _now.strftime('%Y%m%d')

class Config(Enum):

    MEDIA_PATH = os.getcwd()
    BUCKET_NAME = f'transx.s3.{_today_str}'
    ROLE_NAME = f"transx.role.{_today_str}"
    SOURCE_LANG = "en"
    TARGET_LANG = "pt,es,ca"
    TEST_DESCRIPTION = "default description"
    VIMEO_CLIENT_ID = auto()
    VIMEO_ACCESS_TOKEN = auto()
    VIMEO_CLIENT_SECRET = auto()
    VIMEO_USER_ID = auto()
    VIMEO_AUTH_URL = 'https://api.vimeo.com/oauth/authorize'
    VIMEO_TOKEN_URL = 'https://api.vimeo.com/oauth/access_token'

    def resolve(self, prompt_val=None):
        if prompt_val:
            return prompt_val
        val = settings.get(self.name)
        if not val:
            default = self.value
            val = default() if callable(default) else default
        return val

    @staticmethod
    def terms(lang_code=None):
        if not lang_code:
            lang_code = "__all__"
        static_ts = terms_static.default_terms.get(lang_code,{})
        cfg_tts = settings.get("terms", {})
        cfg_ts = cfg_tts.get(lang_code)
        result = static_ts | cfg_ts
        return result


@cmd.cli.command("config")
def command():
    """Prints the current configuration."""
    rich_cfg = Config
    for cfg in rich_cfg:
        info(f"{cfg.name}={cfg.resolve()}")
    info(f"TERMS_LEN__all__={len(Config.terms())}")

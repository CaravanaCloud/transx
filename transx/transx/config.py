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

    PATH = (lambda: os.getcwd())
    BUCKET_NAME = (lambda: f'transx.s3.{_now_str}',)
    ROLE_NAME = (lambda: f"transx.role",)
    SOURCE_LANG = (lambda: f"en",)
    TARGET_LANG = (lambda: f"pt,es,ca",)
    TEST_DESCRIPTION = (lambda: f"default description",)
    VIMEO_CLIENT_ID = (lambda: None,)
    VIMEO_ACCESS_TOKEN = (lambda: None,)
    VIMEO_CLIENT_SECRET = (lambda: None,)
    VIMEO_USER_ID = (lambda: None,)
    VIMEO_AUTH_URL = ('https: //api.vimeo.com/oauth/authorize',)
    VIMEO_TOKEN_URL = ('https: //api.vimeo.com/oauth/access_token',)

    def resolve(self):
        val = settings.get(self.name)
        if not val:
            default = self.value[0]
            match default:
                case str(): val = default
                case func if callable(func): val = func()
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

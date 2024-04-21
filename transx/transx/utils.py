import platform
import uuid
from datetime import datetime
import json

META_EXTENSION = '.transx.json'
semver = "0.0.1"


def version():
    return semver


def system_id():
    system_info = platform.system() + platform.release() + platform.version()
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, system_info))


def datestamp():
    return datetime.now().strftime("%Y%m%d")


def minutestamp():
    return datetime.now().strftime("%Y%m%d%H%M")


def to_json(obj, fp):
    return json.dump(obj, fp, indent=2)

import platform
import uuid
from datetime import datetime

semver = "0.0.1"

def version():
    return semver

def system_id():
    system_info = platform.system() + platform.release() + platform.version()
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, system_info))

def datestamp():
    return datetime.now().strftime("%Y%m%d")

def minstamp():
    return datetime.now().strftime("%Y%m%d%H%M")
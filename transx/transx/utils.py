import os
import platform
import uuid
from datetime import datetime
import json
from .logs import *
from botocore.exceptions import ClientError
import boto3
from .config import *

semver = "0.0.1"

s3 = boto3.client('s3')
iam = boto3.client('iam')


def version():
    return semver


def system_id():
    system_info = platform.system() + platform.release() + platform.version()
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, system_info))


def datestamp():
    return datetime.now().strftime("%Y%m%d")


def minutestamp():
    return datetime.now().strftime("%Y%m%d%H%M")


def secondstamp():
    return datetime.now().strftime("%Y%m%d%H%M%S")


def to_json(obj, fp):
    return json.dump(obj, fp, indent=2)


def user_name():
    return os.environ.get("USER", "anonymous")


def s3_key(data_class, *key_parts):
    username = user_name()
    key_name = "/".join(key_parts)
    result = f"{username}/{data_class}/{key_name}"
    info(f"s3_key({data_class}, {str(key_parts)}) = {result}")
    return result


def s3_url_abs(bucket, *key_parts):
    key_name = "/".join(key_parts)
    result = f"s3://{bucket}/{key_name}"
    info(f"s3_url_abs({bucket}, {str(key_parts)}) = {result}")
    return result


def file_key(directory, file_path):
    relative_path = file_path.relative_to(directory)
    result = s3_key("user", str(relative_path))
    info(f"file_key({directory}, {file_path}) = {result}")
    return result


def dir_key(the_dir):
    folder_name = the_dir.name
    return s3_key(folder_name)


def child_key(file_path, key_prefix, key_name):
    folder_name = file_path.parent.name
    result = s3_key("user", folder_name, key_prefix, key_name)
    return result


def transcribe_key(job_name):
    job_file = job_name.split("__")[1]
    job_key = job_file.split(".")[0]
    result = s3_key("transcribe",   job_name, job_key)
    return result


def get_object(bucket, prefix, file_name, output_file=None):
    """Downloads the transcription results from S3."""
    object_key = prefix
    if not object_key.endswith("/"):
        object_key += "/"
    object_key += file_name
    object_url = s3_url_abs(bucket, object_key)
    try:
        response = s3.get_object(Bucket=bucket, Key=object_key)
        if not output_file:
            output_file = file_name
        info(f"Downloading [{object_url}] as [{output_file}]")
        with open(output_file, 'wb') as f:
            f.write(response['Body'].read())
        info(f"Downloaded [{object_url}] to {output_file}")
    except ClientError as e:
        error(f"Download failed for [{object_url}]: {e}")


def role_exists(role_name):
    if not role_name:
        return False
    try:
        res = iam.get_role(RoleName=role_name)
        result = res.get('Role')
        return result is not None
    except ClientError as e:
        info(f"Role {role_name} does not exist. {e}")
        return False


def create_role(role_name):
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "translate.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    try:
        res = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy)
        )
        info(f"Created role {role_name}: {res}")
    except ClientError as e:
        error(f"Failed to create role {role_name}: {e}")


def assign_policy(role_name, policyName):
    try:
        res = iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn=f"arn:aws:iam::aws:policy/{policyName}"
        )
        info(f"Attached policy {policyName} to role {role_name}: {res}")
    except ClientError as e:
        error(f"Failed to attach policy {policyName} to role {role_name}: {e}")
    pass


def get_role_arn(role_name):
    res = iam.get_role(RoleName=role_name)
    return res.get('Role').get('Arn')


def check_role():
    role_name = resolve(Config.TRANSX_ROLE_NAME, None)
    exists = role_exists(role_name)
    if exists:
        info(f"Role {role_name} exists.")
        return get_role_arn(role_name)
    create_role(role_name)
    assign_policy(role_name, "AmazonS3FullAccess")
    exists = role_exists(role_name)
    if exists:
        info(f"Role {role_name} created.")
        return role_name
    return None

_defaults = {
        Config.TRANSX_PATH:  os.getcwd(),
        Config.TRANSX_BUCKET_NAME: f'transx.s3.{datestamp()}',
        Config.TRANSX_SOURCE_LANG:  'en',
        Config.TRANSX_TARGET_LANG: 'pt,es,ca',
        Config.TRANSX_ROLE_NAME: 'transx-role',
        Config.VIMEO_AUTH_URL: 'https: //api.vimeo.com/oauth/authorize',
        Config.VIMEO_TOKEN_URL: 'https: //api.vimeo.com/oauth/access_token',
}

settings_cache = {}


def resolve(setting, command_line_value=None):
    if setting in settings_cache:
        return settings_cache[setting]
    result = _resolve(setting, command_line_value)
    settings_cache[setting] = result
    return result


def _resolve(setting, command_line_value=None):
    """
    Resolve the value of a setting with the priority:
    command-line option > dynaconf setting > static default.
    """
    if command_line_value is not None:
        info(f"Setting {setting.name} [cli]= {command_line_value}")
        return command_line_value
    if settings.exists(setting):
        setting_value = settings.get(setting)
        info(f"Setting {setting.name} [dynaconf]= {setting_value}")
        return setting_value
    env = os.environ
    if setting.name in env:
        env_value = env.get(setting.name)
        info(f"Setting {setting.name} [env]= {env_value}")
        return env_value
    default_val = _defaults.get(setting)
    info(f"Setting {setting.name} [default]= {default_val}")
    return default_val
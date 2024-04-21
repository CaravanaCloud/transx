import os
import platform
import uuid
from datetime import datetime
import json
from .logs import *
from botocore.exceptions import ClientError
import boto3


s3 = boto3.client('s3')
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


def user_name():
    return os.environ.get("USER", "anonymous")


def _key(folder_name, *key_parts):
    username = user_name()
    key_name = "/".join(key_parts)
    return f"{username}/{folder_name}/{key_name}"


def file_key(file_path):
    folder_name = file_path.parent.name
    file_name = file_path.name
    return _key(folder_name, file_name)


def child_key(file_path, key_prefix, key_name):
    folder_name = file_path.parent.name
    result = _key(folder_name, key_prefix, key_name)
    return result


def s3_url(bucket, key):
    return f"s3://{bucket}/{key}"


def get_object(bucket, prefix, file_name, output_file = None):
    """Downloads the transcription results from S3."""
    object_key = prefix
    if not object_key.endswith("/"):
        object_key += "/"
    object_key += file_name
    object_url = s3_url(bucket, object_key)
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


def write_sibling(file_path, sibling_ext, sibling_data):
    sibling_path = file_path.with_suffix(sibling_ext)
    with open(sibling_path, "w") as f:
        to_json(sibling_data, f)
    return sibling_path


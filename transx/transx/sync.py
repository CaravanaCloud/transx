import click
import boto3
import json
import logging
from hashlib import md5
from botocore.exceptions import ClientError
from .ls import * 
from .config import Config
from .logs import *

s3 = boto3.client('s3')

def calculate_md5(file_path):
    """Calculate MD5 hash of the file for integrity checking."""
    hash_md5 = md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def check_synced(file_path, md5):
    """Check if the file is already synced with S3 by comparing stored md5."""
    json_path = file_path.with_suffix('.transx.json')
    try:
        with open(json_path) as json_file:
            data = json.load(json_file)
            if data['md5'] == md5:
                info(f"No changes detected for {file_path}, skipping upload.")
                print(f"File {file_path} has not changed. Skipping upload.")
                return True
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        print(f"No sync record for {file_path}. Uploading...")
    return False

def ensure_bucket_exists(bucket_name):
    """Ensure the S3 bucket exists, and create it if it does not."""
    try:
        s3.head_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' exists. Proceeding with file uploads.")
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"Bucket '{bucket_name}' does not exist. Creating bucket...")
            try:
                s3.create_bucket(Bucket=bucket_name)
                print(f"Bucket '{bucket_name}' created successfully.")
            except ClientError as ce:
                print(f"Failed to create bucket '{bucket_name}': {ce}")
                raise ce
        else:
            print(f"Failed to access bucket '{bucket_name}': {e}")
            raise e

@click.command()
@click.option('--directory', default=None, help='Directory to search in')
@click.option('--glob_pattern', default=None, help='Glob pattern to filter files by')
@click.option('--bucket_name', default=None, help='Bucket name')
def sync(directory, glob_pattern, bucket_name):
    """Sync files to S3, checking each file for changes and uploading only if necessary."""
    directory = Config.resolve(Config.TRANSX_PATH, directory)
    glob_pattern = Config.resolve(Config.TRANSX_GLOB, glob_pattern)
    bucket_name = Config.resolve(Config.S3_BUCKET_NAME, None)

    # Check if the bucket exists and create if not
    ensure_bucket_exists(bucket_name)

    # Use the ls function to get files
    files = get_files(directory, glob_pattern)  # Now calling ls() which returns the list of files

    for file_path in files:
        md5 = calculate_md5(str(file_path))
        if not check_synced(file_path, md5):
            try:
                s3.upload_file(
                    Filename=str(file_path),
                    Bucket=bucket_name,
                    Key=file_path.name
                )
                print(f"Uploaded {file_path} to S3 bucket '{bucket_name}'.")
                format = file_path.suffix.replace('.', '')
                with open(str(file_path)+('.transx.json'), 'w') as json_file:
                    meta = {
                        'md5': md5,
                        'file': file_path.name,
                        'bucket': bucket_name,
                        'key': file_path.name,
                        'format': format
                    }
                    json.dump(obj=meta, 
                            fp=json_file,
                            indent=2)
            except ClientError as e:
                print(f"Failed to upload {file_path}: {e}")

if __name__ == '__main__':
    sync()
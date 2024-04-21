import boto3
import hashlib
from botocore.exceptions import ClientError
from .utils import *
from .ls import * 
from .config import Config
from .logs import *
from . import cmd
from . import files

DEFAULT_S3CMD_PART_SIZE = 15728640

DEFAULT_AWS_PART_SIZE = 8388608

s3 = boto3.client('s3')


def calc_etag(inputfile, partsize):
    md5_digests = []
    with open(inputfile, 'rb') as f:
        for chunk in iter(lambda: f.read(partsize), b''):
            md5_digests.append(hashlib.md5(chunk).digest())
    return hashlib.md5(b''.join(md5_digests)).hexdigest() + '-' + str(len(md5_digests))


def factor_of_1mb(filesize, num_parts):
    x = filesize / int(num_parts)
    y = x % 1048576
    return int(x + 1048576 - y)


def possible_partsizes(filesize, num_parts):
    return lambda partsize: partsize < filesize and (float(filesize) / float(partsize)) <= num_parts


def is_synced(file_path, s3_bucket, s3_key):
    """Check if the file is already synced with S3 by comparing stored md5."""
    # From https://teppen.io/2018/10/23/aws_s3_verify_etags/
    # Get the S3 object's metadata (including ETag, which is usually the MD5 checksum)
    try:
        response = s3.head_object(Bucket=s3_bucket, Key=s3_key)
        s3_etag = response.get('ETag', None)

        if s3_etag:
            s3_etag = s3_etag.strip('"')
            filesize = os.path.getsize(file_path)
            etag_arr = s3_etag.split('-')
            if len(etag_arr) == 1:
                local_etag = etag_arr[0]
                return s3_etag == local_etag
            if len(etag_arr) == 2:
                num_parts = int(etag_arr[1])
                default_part_sizes = [
                    DEFAULT_AWS_PART_SIZE,
                    DEFAULT_S3CMD_PART_SIZE,
                    factor_of_1mb(filesize, num_parts)
                ]
                for part_size in filter(possible_partsizes(filesize, num_parts), default_part_sizes):
                    local_etag = calc_etag(file_path, part_size)
                    if s3_etag == local_etag:
                        return True

        return False
    except ClientError as e:
        # Handle the case where the S3 object does not exist or an error occurs
        debug(f"Key not found {s3_key}: {e}")
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


@cmd.cli.command('sync')
@click.option('--directory', default=None, help='Directory to search in')
@click.option('--bucket_name', default=None, help='Bucket name')
def command(directory, bucket_name):
    run(directory, bucket_name)


def run(directory, bucket_name):
    """Sync files to S3, checking each file for changes and uploading only if necessary."""
    directory = Config.resolve(Config.TRANSX_PATH, directory)
    bucket_name = Config.resolve(Config.S3_BUCKET_NAME, bucket_name)
    ensure_bucket_exists(bucket_name)
    all_files = files.find_all(directory)
    out_files = []
    for file_path in all_files:
        sync_file(bucket_name, file_path)
        result = {
            "file": file_path,
        }
        out_files.append(result)
    result = {
        "status": "ok",
        "files": out_files
    }
    return result


def sync_file(bucket_name, file_path):
    s3_key = file_key(file_path)
    if is_synced(file_path, bucket_name, s3_key):
        info(f"File {file_path} in sync with s3://{bucket_name}/{s3_key}")
        return
    try:
        s3.upload_file(
            Filename=str(file_path),
            Bucket=bucket_name,
            Key=s3_key)
        info(f"File {file_path} uploaded to s3://{bucket_name}/{s3_key}")
    except ClientError as e:
        error(f"File {file_path} sync failed to s3://{bucket_name}/{s3_key}. Error: {e}")

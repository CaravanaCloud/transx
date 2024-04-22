import click
from . import cmd
from .logs import *
from .utils import *
from .files import *


def clean_directory(directory):
    # delete all media, subtitles, transcriptions, translations
    files = find_all(directory)
    for file_path in files:
        is_output = is_output(file_path)
        if is_output:
            debug(f"Deleting {file_path}")
            file_path.unlink()
    info("Cleaned up directory.")


def clean_bucket(bucket_name):
    # List all objects in the bucket
    objects = s3.list_objects_v2(Bucket=bucket_name)

    # Delete all objects and object versions
    if 'Contents' in objects:
        for obj in objects['Contents']:
            s3.delete_object(Bucket=bucket_name, Key=obj['Key'])

    # List all object versions in the bucket
    object_versions = s3.list_object_versions(Bucket=bucket_name)

    # Delete all object versions
    if 'Versions' in object_versions:
        for version in object_versions['Versions']:
            s3.delete_object(Bucket=bucket_name, Key=version['Key'], VersionId=version['VersionId'])

    # Delete all delete markers (if any)
    if 'DeleteMarkers' in object_versions:
        for delete_marker in object_versions['DeleteMarkers']:
            s3.delete_object(Bucket=bucket_name, Key=delete_marker['Key'], VersionId=delete_marker['VersionId'])

    # Delete bucket policies
    s3.delete_bucket_policy(Bucket=bucket_name)

    # Delete bucket
    s3.delete_bucket(Bucket=bucket_name)

    print(f"All contents in bucket '{bucket_name}' have been deleted.")


def clean (directory, bucket_name):
    """Clean up the local and remote directories."""
    debug("Cleaning up directories.")
    clean_directory(directory)
    clean_bucket(bucket_name)


@cmd.cli.command('clean')
@click.option('--directory', default=None, help='Directory to search in')
@click.option('--bucket_name', default=None, help='Bucket name')
def command(directory, bucket_name):
    directory = resolve(Config.TRANSX_PATH, directory)
    bucket_name = resolve(Config.TRANSX_BUCKET_NAME, bucket_name)
    click.echo(clean(directory, bucket_name))


import click
from pprint import pformat
from .utils import *
from . import cmd, sync
from tenacity import retry, wait_exponential, stop_after_delay
from datetime import datetime
import time
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

translate = boto3.client('translate')


def transcribe_key(file_path, job_name):
    key = file_key(file_path)
    return f"{key}/transcribe/{job_name}/"


def start_translate_job(translate_prefix, bucket_name, job_name):
    """Starts a translate job for the specified dir."""
    job_info = {
        'JobName': job_name,
        'TranslatePrefix': translate_prefix,
    }
    pretty_job_info = pformat(job_info)
    info(f"Starting translate job.\n{pretty_job_info}")
    input_key = s3_key("user", translate_prefix)
    input_uri = s3_url_abs(bucket_name, input_key)
    output_key = s3_key("translate", job_name)
    output_uri = s3_url_abs(bucket_name, output_key)
    role_arn = check_role()
    src_lang = resolve(Config.TRANSX_SOURCE_LANG)
    tgt_lang_str = resolve(Config.TRANSX_TARGET_LANG)
    tgt_langs = tgt_lang_str.split(",")
    job_info = {
        'JobName': job_name,
        'InputUri': input_uri,
        'OutputUri': output_uri,
        'DataAccessRoleArn': role_arn,
        'SourceLanguageCode': src_lang,
        'TargetLanguageCodes': tgt_langs
    }
    pretty_job_info = pformat(job_info)
    info(f"Starting translate job.\n{pretty_job_info}")
    try:
        resp = translate.start_text_translation_job(
            JobName=job_name,
            InputDataConfig={
                'S3Uri': input_uri,
                'ContentType': 'text/plain'
            },
            OutputDataConfig={
                'S3Uri': output_uri
            },
            DataAccessRoleArn=role_arn,
            SourceLanguageCode=src_lang,
            TargetLanguageCodes=tgt_langs
        )
        job_id = resp['JobId']
        job_info['JobId'] = job_id
        return job_info
    except ClientError as e:
        error(f"Failed to start translate job for {dir}: {e}")
        return None


_done_status = ["COMPLETED", "COMPLETED_WITH_ERROR", "FAILED", "STOPPED", "STOP_REQUESTED"]


@retry(wait=wait_exponential(multiplier=1.5, min=30, max=2*60), stop=stop_after_delay(60*60))
def wait_job_done(subtitle_prefix, job_info):
    """Polls the translate job status until completion or failure."""
    job_id = job_info.get('JobId')
    try:
        resp = translate.describe_text_translation_job(JobId=job_id)
        props = resp.get("TextTranslationJobProperties")
        status = props.get("JobStatus")
        now_str = datetime.isoformat(datetime.now())
        info(f"Current status of job {job_id}: {status} {now_str}")
        if status in _done_status:
            job_pp = pformat({}, indent=2)
            info(job_pp)
            return props
        raise Exception(f"Translation job {job_id} done yet.")
    except ClientError as e:
        error(f"Error fetching job status for {job_id}: {e}")
        return None


def s3_download_all(directory, output_s3_url):
    if output_s3_url.startswith("s3://"):
        output_s3_url = output_s3_url[5:]
    bucket_name, prefix = output_s3_url.split('/', 1) if '/' in output_s3_url else (output_s3_url, '')

    # Ensure the prefix ends with '/' if it's not empty
    if prefix and not prefix.endswith('/'):
        prefix += '/'

    # Create the directory if it does not exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    # List objects within the S3 bucket
    paginator = s3.get_paginator('list_objects_v2')

    try:
        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
            for obj in page.get('Contents', []):
                # Construct the path to save the file
                file_path = os.path.join(directory, obj['Key'][len(prefix):])
                file_dir = os.path.dirname(file_path)

                # Create directory structure if it does not exist
                if not os.path.exists(file_dir):
                    os.makedirs(file_dir)

                # Download the file
                s3.download_file(bucket_name, obj['Key'], file_path)
                info(f"Downloaded {obj['Key']} to {file_path}")

    except NoCredentialsError:
        info("Error: No AWS credentials were found.")
    except PartialCredentialsError:
        info("Error: Incomplete AWS credentials.")
    except Exception as e:
        info(f"An error occurred: {e}")


def download(directory, job_info):
    """Downloads the translate results from S3."""
    info(f"Downloading translate results.\n {job_info} ")
    output_config = job_info.get("OutputDataConfig")
    output_s3_url = output_config.get('S3Uri')
    directory_path = Path(directory)
    parent_path = directory_path.parent
    output_dir = parent_path / "subtitles"
    s3_download_all(output_dir, output_s3_url)
    info(f"Downloaded translate results to {output_dir}.")


def write_translate_job(subtitle_prefix, done_job):
    info(f"Writing done translate job info for {subtitle_prefix}\n{str(done_job)}")


@cmd.cli.command('translate')
@click.option('--directory', default=None, help='Directory to search in')
@click.option('--bucket_name', default=None, help='Bucket name')
def command(directory, bucket_name):
    """Transcribes all audio files in the specified directory matching the glob pattern."""
    bucket_name = resolve(Config.TRANSX_BUCKET_NAME, bucket_name)
    directory = resolve(Config.TRANSX_PATH, directory)
    sync_res = sync.run(directory, bucket_name)
    sync_ok = sync_res.get('status') == 'ok'
    if not sync_ok:
        error("Failed to sync files.")
        return
    subtitle_prefixes = sync_res.get('subtitle_prefixes')
    info(f"Found {len(subtitle_prefixes)} synced dirs to transcribe.")
    for subtitle_prefix in subtitle_prefixes:
        subtitle_prefix_id = subtitle_prefix.replace("/", "_")
        job_name = f"traslate__{subtitle_prefix_id}__{secondstamp()}"
        info(f"Starting translate job for {subtitle_prefix}.")
        job_info = start_translate_job(subtitle_prefix, bucket_name, job_name)
        if not job_info:
            error(f"Failed to start translate job for {subtitle_prefix}.")
            continue
        info("Translate job started.")
        t0 = time.time()
        done_job = wait_job_done(subtitle_prefix, job_info)
        t1 = time.time()
        minutes = (t1 - t0) / 60.0
        info(f"Transcribe job completed in {minutes} minutes.")
        status = "ERROR"
        if done_job:
            status = "DONE"
            write_translate_job(subtitle_prefix, done_job)
            download(subtitle_prefix, done_job)
        info(f"Transcribe job completed. status[{status}] dir[{subtitle_prefix}].")

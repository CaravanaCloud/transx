import click
from pprint import pformat
from .utils import *
from . import cmd, sync
from tenacity import retry, wait_exponential, stop_after_attempt
from datetime import datetime
import time

polly = boto3.client('polly')


def transcribe_key(file_path, job_name):
    key = file_key(file_path)
    return f"{key}/transcribe/{job_name}/"


def start_tts_job(tts_prefix, bucket_name, job_name):
    """Starts a tts job for the specified dir."""
    job_info = {
        'JobName': job_name,
        'TranslatePrefix': tts_prefix,
    }
    pretty_job_info = pformat(job_info)
    info(f"Starting tts job.\n{pretty_job_info}")
    input_key = s3_key("user", tts_prefix)
    input_uri = s3_url_abs(bucket_name, input_key)
    output_uri = s3_url_abs(bucket_name, "tts", job_name)
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
    info(f"Starting tts job.\n{pretty_job_info}")
    try:
        resp = tts.start_text_translation_job(
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
        error(f"Failed to start tts job for {dir}: {e}")
        return None


_done_status = ["COMPLETED", "COMPLETED_WITH_ERROR", "FAILED", "STOPPED", "STOP_REQUESTED"]


@retry(wait=wait_exponential(multiplier=2, min=30, max=60 * 60), stop=stop_after_attempt(30))
def wait_job_done(subtitle_prefix, job_info):
    """Polls the tts job status until completion or failure."""
    job_id = job_info.get('JobId')
    try:
        resp = tts.describe_text_translation_job(JobId=job_id)
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


def download(file_path, bucket_name, job_info):
    """Downloads the tts results from S3."""
    info(f"Downloading tts results. {job_info} ")


@cmd.cli.command('tts')
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
        job_name = f"tts__{subtitle_prefix_id}__{secondstamp()}"
        info(f"Starting tts job for {subtitle_prefix}.")
        job_info = start_tts_job(subtitle_prefix, bucket_name, job_name)
        if not job_info:
            error(f"Failed to start tts job for {subtitle_prefix}.")
            continue
        info("TTS job started.")
        t0 = time.time()
        done_job = wait_job_done(subtitle_prefix, job_info)
        t1 = time.time()
        minutes = (t1 - t0) / 60.0
        info(f"TTS job completed in {minutes} minutes.")
        status = "ERROR"
        if done_job:
            status = "DONE"
            download(subtitle_prefix, bucket_name, job_info)
        info(f"TTS job completed. status[{status}] dir[{subtitle_prefix}].")

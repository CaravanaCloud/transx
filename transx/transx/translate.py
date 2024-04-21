import click
import time
from pprint import pformat
from .files import *
from .utils import *
from . import cmd, terms, sync


translate = boto3.client('translate')


def transcribe_key(file_path, job_name):
    key = file_key(file_path)
    return f"{key}/transcribe/{job_name}/"


def start_translate_job(the_dir, bucket_name, job_name):
    """Starts a translate job for the specified dir."""
    job_info = {
        'FileDir': the_dir,
    }
    pretty_job_info = pformat(job_info)
    info(f"Starting translate job.\n{pretty_job_info}")
    input_uri = s3_url_abs(bucket_name, dir_key(the_dir))
    output_uri = s3_url_abs(bucket_name,  "translate", job_name)
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
        translate.start_text_translation_job(
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
        return job_info
    except ClientError as e:
        error(f"Failed to start translate job for {dir}: {e}")
        return None


def wait_job_done(file_path, job_name):
    """Polls the translate job status until completion or failure."""
    while True:
        try:
            # response = transcribe.get_translate_job(jTranslateJobName=job_name)
            # job = response['jTranslateJob']
            status = 'COMPLETED'
            info(f"Current status of job {job_name}: {status}")
            if status in ['COMPLETED', 'FAILED']:
                job_pp = pformat({}, indent=2)
                info(job_pp)
                write_sibling(file_path, ".transcribe.txt", job_pp)
                return {}
            time.sleep(60)
        except ClientError as e:
            error(f"Error fetching job status for {job_name}: {e}")
            return None


def download(file_path, bucket_name, job_info):
    """Downloads the translate results from S3."""
    info("Download translate results.")


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
    synced_dirs = sync_res.get('dirs')
    info(f"Found {len(synced_dirs)} synced dirs to transcribe.")
    for dir in synced_dirs:
        dir_name = dir.name
        job_name = f"transcribe_{dir_name}_{minutestamp()}"
        info(f"Starting translate job for {dir_name}.")
        job_info = start_translate_job(dir, bucket_name, job_name)
        if not job_info:
            error(f"Failed to start translate job for {dir_name}.")
            continue
        info("jTranslate job started.")
        done_job = wait_job_done(dir, job_name)
        status = "ERROR"
        if done_job:
            status = "DONE"
            download(dir, bucket_name, job_info)
        info(f"Transcribe job completed. status[{status}] dir[{dir_name}].")

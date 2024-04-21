import click
import time
from pprint import pformat
from .utils import *
from . import cmd, terms, sync
from .logs import *
from tenacity import retry, wait_exponential, stop_after_attempt

transcribe = boto3.client('transcribe')


def start_transcribe_job(directory, file_path, bucket_name, job_name):
    """Starts a transcribe job for the specified file."""
    file_name = file_path.name
    file_dir = file_path.parent.name
    media_format = file_path.suffix[1:] if file_path.suffix else None
    output_key = transcribe_key(job_name)

    if not (bucket_name and output_key):
        error(f"Missing bucket[{bucket_name}] name or key[{output_key}] for {file_name}")
        return None
    subs = {'Formats': ['vtt', 'srt']}
    media_key = file_key(directory, file_path)
    media_uri = s3_url_abs(bucket_name, media_key)
    media = {'MediaFileUri': media_uri}
    job_info = {
        'JobName': job_name,
        'FileDir': file_dir,
        'FileName': file_name,
        'TranscriptionJobName': job_name,
        'Media': media,
        'MediaFormat': media_format,
        'OutputBucketName': bucket_name,
        'OutputKey': output_key,
        'IdentifyMultipleLanguages': True,
        'Subtitles': subs
    }
    pretty_job_info = pformat(job_info)
    info(f"Starting transcribe job.\n{pretty_job_info}")
    try:
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media=media,
            MediaFormat=media_format,
            OutputBucketName=bucket_name,
            OutputKey=output_key,
            IdentifyMultipleLanguages=True,
            Subtitles=subs
        )
        return job_info
    except ClientError as e:
        error(f"Failed to start transcribe job for {file_name}: {e}")
        return None


@retry(wait=wait_exponential(multiplier=2, min=30, max=60 * 60), stop=stop_after_attempt(30))
def wait_job_done(file_path, job_name):
    """Polls the transcribe job status until completion or failure."""
    try:
        response = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        job = response['TranscriptionJob']
        status = job['TranscriptionJobStatus']
        info(f"Current status of job {job_name}: {status}")
        if status in ['COMPLETED', 'FAILED']:
            job_pp = pformat(job, indent=2)
            info(job_pp)
            write_sibling(file_path, ".transcribe.txt", job_pp)
            return job
        raise Exception(f"Job {job_name} not done yet.")
    except ClientError as e:
        error(f"Error fetching job status for {job_name}: {e}")
        return None


def fix_terms(file_name, job_info):
    file_path = Path(file_name)
    exists = file_path.exists()
    if not exists:
        error(f"File not found: {file_name}")
        return
    lang_code = "xx_YY"
    if job_info:
        langs = job_info.get('LanguageCodes')
        if langs and len(langs):
            first = langs[0]
            lang_code = first.get('LanguageCode')
            return lang_code
    out_path = file_path.name.replace(".transcribe.", f".{lang_code}.")
    info(f"Fixing terms in [{file_name}] in [{lang_code}] to [{out_path}]")
    terms.fix_terms(file_path, lang_code, out_path)


def download(file_path, bucket_name, job_info):
    """Downloads the transcribe results from S3."""
    job_name = job_info.get('TranscriptionJobName')
    info(f"Downloading transcribes for {job_name} [{type(job_info)}]\n{pformat(job_info)}")
    file_dir = file_path.parent
    subs_dir = file_dir / "subs"
    if not subs_dir.exists():
        subs_dir.mkdir()
    subs = job_info.get("Subtitles", {})
    info(f"Subtitles [{type(subs)}]: {subs}")
    sub_uris = subs.get("SubtitleFileUris", [])
    info(f"Downloading [{len(sub_uris)}] subtitles from {job_name}")
    for uri in sub_uris:
        uri_split = uri.split("/")
        object_prefix = "/".join(uri_split[4:-1])
        object_key = uri_split[-1]
        object_stem = object_key.split(".")[0]
        object_ext = object_key.split(".")[-1]
        out_ext = ".transcribe." + object_ext
        out_key = object_stem + out_ext
        dl_file_out = subs_dir / out_key
        get_object(bucket_name, object_prefix, object_key, dl_file_out)
        fix_terms(dl_file_out, job_info)
        info(f"Downloaded [{uri}] to [{dl_file_out}]")


@cmd.cli.command('transcribe')
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
    synced_medias = sync_res.get('files')
    info(f"Found {len(synced_medias)} synced medias to transcribe.")
    for media_data in synced_medias:
        media = media_data.get("file")
        if not media:
            error("Missing media file.")
            continue
        file_name = media.name
        job_name = f"transcribe__{file_name}__{secondstamp()}"
        info(f"Starting transcribe job for {file_name}.")
        job_info = start_transcribe_job(directory, media, bucket_name, job_name)
        if not job_info:
            error(f"Failed to start transcribe job for {file_name}.")
            continue
        info("Transcription job started.")
        done_job = wait_job_done(media, job_name)
        status = "ERROR"
        if done_job:
            status = "DONE"
            download(media, bucket_name, done_job)
        info(f"Transcribe job completed. status[{status}] file[{file_name}].")

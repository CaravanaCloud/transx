import click
import time
from pprint import pformat
from .files import *
from .utils import *
from . import cmd, terms, sync
transcribe = boto3.client('transcribe')


def transcribe_key(file_path, job_name):
    key = file_key(file_path)
    return f"{key}/transcribe/{job_name}/"


def start_transcription_job(file_path, bucket_name, job_name):
    """Starts a transcription job for the specified file."""
    file_name = file_path.name
    file_dir = file_path.parent.name
    media_format = file_path.suffix[1:] if file_path.suffix else None
    output_key = transcribe_key(file_path, job_name)

    if not (bucket_name and output_key):
        error(f"Missing bucket[{bucket_name}] name or key[{output_key}] for {file_name}")
        return None
    subs = {'Formats': ['vtt', 'srt']}
    media_key = file_key(file_path)
    media_uri = s3_url(bucket_name, media_key)
    media = {'MediaFileUri': media_uri}
    job_info = {
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
    info(f"Starting transcription job.\n{pretty_job_info}")
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
        error(f"Failed to start transcription job for {file_name}: {e}")
        return None


def wait_job_done(file_path, job_name):
    """Polls the transcription job status until completion or failure."""
    while True:
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
            time.sleep(60)
        except ClientError as e:
            error(f"Error fetching job status for {job_name}: {e}")
            return None


def fix_terms(file_name, job_info):
    file_path = Path(file_name)
    exists = file_path.exists()
    if not exists:
        return
    # replace .translate.Xxx extension with .Xxx
    lang_code = "en-US"
    if job_info:
        langs = job_info.get('LanguageCodes')
        if langs and len(langs):
            first = langs[0]
            lang_code = first.get('LanguageCode')
            return lang_code
    out_path = file_path.with_name(file_path.name.replace(".transcribe.", f".{lang_code}."))
    terms.fix_terms(file_path, lang_code, out_path)


def download(file_path, bucket_name, job_info):
    """Downloads the transcription results from S3."""
    job_name = job_info.get('TranscriptionJobName')
    info(f"Downloading transcriptions for {job_name}")
    file_name = file_path.name
    file_dir = file_path.parent
    bucket = bucket_name

    output_prefix = transcribe_key(file_path, job_name)

    transc_key = job_name
    transc_file = file_name + ".transcribe.json"
    transc_out = os.path.join(file_dir, transc_file)
    get_object(bucket, output_prefix, transc_key, transc_out)
    fix_terms(transc_out, job_info)

    vtt_key = job_name + ".vtt"
    vtt_file = file_name + ".transcribe.vtt"
    vtt_out = os.path.join(file_dir, vtt_file)
    get_object(bucket, output_prefix, vtt_key, vtt_out)
    fix_terms(vtt_out, job_info)

    srt_key = job_name + ".srt"
    srt_file = file_name + ".transcribe.srt"
    srt_out = os.path.join(file_dir, srt_file)
    get_object(bucket, output_prefix, srt_key, srt_out)
    fix_terms(srt_out, job_info)


@cmd.cli.command('transcribe')
@click.option('--directory', default=None, help='Directory to search in')
@click.option('--bucket_name', default=None, help='Bucket name')
def command(directory, bucket_name):
    """Transcribes all audio files in the specified directory matching the glob pattern."""
    bucket_name = Config.resolve(Config.S3_BUCKET_NAME, bucket_name)
    directory = Config.resolve(Config.TRANSX_PATH, directory)
    sync_res = sync.run(directory, bucket_name) # TODO: Return synced files instead of re-scanning?
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
        job_name = f"transcribe_{file_name}_{minutestamp()}"
        info(f"Starting transcription job for {file_name}.")
        job_info = start_transcription_job(media, bucket_name, job_name)
        if not job_info:
            error(f"Failed to start transcription job for {file_name}.")
            continue
        info("Transcription job started.")
        done_job = wait_job_done(media, job_name)
        status = "ERROR"
        if done_job:
            status = "DONE"
            download(media, bucket_name, job_info)
        info(f"Transcribe job completed. status[{status}] file[{file_name}].")

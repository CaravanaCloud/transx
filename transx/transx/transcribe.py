import click
import boto3
import json
import logging
import time
from pathlib import Path
from botocore.exceptions import ClientError
from .config import Config
from .utils import *

# Set up logging
logging.basicConfig(level=logging.INFO)

# Create a Transcribe client
transcribe_client = boto3.client('transcribe')

def start_transcription_job(file_path, job_name):
    """Starts a transcription job for the specified audio file."""
    # read json from file_path as metadata
    with open(file_path) as f:
        metadata = json.load(f)
        video_path = str(metadata['file'])
        media_format = metadata['format']
        bucket_name = metadata.get('bucket', None)
        key = metadata.get('key', None)
        output_key =  f"{key}/transcribe/{job_name}"
        subs = { 'Formats': ['vtt','srt'] }
        if bucket_name and key:
            video_uri = f"s3://{bucket_name}/{key}"
        else :
            logging.error(f"Failed to start transcription job for {file_path}: bucket and key not found")
            raise Exception("bucket and key not found")
        media = {'MediaFileUri': video_uri}
        job_info = {
                'TranscriptionJobName': job_name,
                'Media': media,
                'MediaFormat': media_format,
                'OutputBucketName': bucket_name,
                'OutputKey': output_key,
                'IdentifyMultipleLanguages': True,
                'Subtitles': subs
            }
        logging.info(f"Starting transcription job {job_info}")
        try:
            transcribe_client.start_transcription_job(
                TranscriptionJobName=job_name,
                Media=media,
                MediaFormat=media_format,
                OutputBucketName=bucket_name,
                OutputKey=output_key,
                IdentifyMultipleLanguages=True,
                Subtitles=subs
            )
        except ClientError as e:
            logging.error(f"Failed to start transcription job for {file_path}: {e}")
            raise

def check_job_status(job_name):
    """Polls the transcription job status until completion or failure."""
    while True:
        try:
            response = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            status = response['TranscriptionJob']['TranscriptionJobStatus']
            logging.info(f"Current status of job {job_name}: {status}")
            if status in ['COMPLETED', 'FAILED']:
                return status
            time.sleep(60)  # Poll every minute
        except ClientError as e:
            logging.error(f"Error fetching job status for {job_name}: {e}")
            raise

def write_transcription_metadata(file_path, status):
    """Writes the transcription job status to a JSON metadata file."""
    # read json from file_path as metadata
    with open(file_path) as f:
        metadata = json.load(f)
        metadata['transcribe_status']
        metadata['transcribe_status'] = status
    # write json to file_path
    with open(file_path, 'w') as f:
        json.dump(metadata, f)

@click.command()
@click.option('--directory', default=None, help='Directory to search in')
def transcribe(directory):
    """Transcribes all audio files in the specified directory matching the glob pattern."""
    directory = Config.resolve(Config.TRANSX_PATH, directory)
    glob_pattern = "**/*.transx.json"
    path = Path(directory)
    files = list(path.rglob(glob_pattern))
    logging.info(f"Found {len(files)} files to transcribe.")
    for file_path in files:
        job_name = f"transcribe_{file_path.stem}_{minstamp()}"
        logging.info(f"Starting transcription job for {file_path}")
        start_transcription_job(file_path, job_name)
        status = check_job_status(job_name)
        write_transcription_metadata(file_path, status)
        logging.info(f"Completed transcription job for {file_path} with status: {status}")

if __name__ == '__main__':
    transcribe()

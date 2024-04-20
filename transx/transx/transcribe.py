import os
import click
import boto3
import json
import logging
import time
import asyncio

from pathlib import Path
from botocore.exceptions import ClientError
from .config import Config
from .utils import *
from .logs import *


s3 = boto3.client('s3')
transcribe = boto3.client('transcribe')

def start_transcription_job(file_path, job_name):
    """Starts a transcription job for the specified file."""
    # read json from file_path as metadata
    with open(file_path) as f:
        metadata = json.load(f)
        file_name = str(metadata['file'])
        file_dir = os.path.dirname(file_path)
        media_format = metadata['format']
        bucket_name = metadata.get('bucket', None)
        key = metadata.get('key', None)
        output_key =  f"{key}/transcribe/{job_name}/{key}"
        subs = { 'Formats': ['vtt','srt'] }
        if bucket_name and key:
            video_uri = f"s3://{bucket_name}/{key}"
        else:
            error(f"Failed to start transcription job for {file_path}: bucket and key not found")
            raise Exception("bucket and key not found")
        media = {'MediaFileUri': video_uri}
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
        info(f"Starting transcription job {job_info}")
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
            error(f"Failed to start transcription job for {file_path}: {e}")
            return None

def check_job_status(job_name):
    """Polls the transcription job status until completion or failure."""
    while True:
        try:
            response = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            status = response['TranscriptionJob']['TranscriptionJobStatus']
            info(f"Current status of job {job_name}: {status}")
            if status in ['COMPLETED', 'FAILED']:
                return status
            time.sleep(60)
        except ClientError as e:
            error(f"Error fetching job status for {job_name}: {e}")
            raise

def write_transcription_metadata(file_path, status):
    """Writes the transcription job status to a JSON metadata file."""
    # read json from file_path as metadata
    with open(file_path) as f:
        metadata = json.load(f)
        print("TODO: write transcription result metadata")
    # write json to file_path
    with open(file_path, 'w') as f:
        json.dump(metadata, f)


def get_object(bucket, prefix, file_name, output_file = None):
    """Downloads the transcription results from S3."""
    file_key = prefix + "/" + file_name
    try:
        response = s3.get_object(Bucket=bucket, Key=file_key)
        if not output_file:
            output_file = file_name
        info(f"Downloading [{file_key}] as [{output_file}]")
        with open(output_file, 'wb') as f:
            f.write(response['Body'].read())
        info(f"Downloaded transcription for {file_name} to {output_file}")
    except ClientError as e:
        error(f"Failed to download transcription for {file_name}: {e}")

def download(job_info):
    """Downloads the transcription results from S3."""
    job_name = job_info.get('TranscriptionJobName')
    info(f"Downloading transcription for {job_name}")
    debug(f"Job info: {job_info}")
    debug("==========================================")
    file_name = job_info.get('FileName')
    bucket = job_info['OutputBucketName']
    prefix = file_name + "/transcribe/" + job_name
    file_dir = job_info['FileDir']
    transcribe_file = os.path.join(file_dir, file_name + ".transcribe.json")
    vtt_file = os.path.join(file_dir, file_name + ".vtt")
    srt_file = os.path.join(file_dir, file_name + ".srt")
    get_object(bucket, prefix, file_name, transcribe_file)
    get_object(bucket, prefix, vtt_file)
    get_object(bucket, prefix, srt_file)

@click.command()
@click.option('--directory', default=None, help='Directory to search in')
def run(directory):
    """Transcribes all audio files in the specified directory matching the glob pattern."""
    directory = Config.resolve(Config.TRANSX_PATH, directory)
    glob_pattern = "**/*.transx.json"
    path = Path(directory)
    files = list(path.rglob(glob_pattern))
    info(f"Found {len(files)} files to transcribe.")
    for file_path in files:
        job_name = f"transcribe_{file_path.stem}_{minstamp()}"
        info(f"Starting transcription job for {file_path}")
        job_info = start_transcription_job(file_path, job_name)
        info("Transcription job started.")
        status = check_job_status(job_name)
        write_transcription_metadata(file_path, status)
        info(f"Completed transcription job for {file_path} with status: {status}")
        download(job_info)

if __name__ == '__main__':
    run()

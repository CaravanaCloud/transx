import os
import click
import boto3
import json
import logging
import time

from botocore.exceptions import ClientError
from pathlib import Path

from .config import Config

from .utils import *
from .logs import *
from .files import *


s3 = boto3.client('s3')
transcribe = boto3.client('transcribe')

def start_transcription_job(metadata, job_name):
    """Starts a transcription job for the specified file."""
    file_name = str(metadata['file'])
    file_dir = str(metadata['dir'])
    media_format = metadata['format']
    bucket_name = metadata.get('bucket', None)
    key = metadata.get('key', None)
    output_key =  f"{key}/transcribe/{job_name}/{key}"
    subs = { 'Formats': ['vtt','srt'] }
    if not (bucket_name and key):
        error(f"Missing bucket name or key for {file_name}")
        return None
    video_uri = f"s3://{bucket_name}/{key}"
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
        error(f"Failed to start transcription job for {file_name}: {e}")
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

def write_transcription_metadata(meta, status):
    """Writes the transcription job status to a JSON metadata file."""
    file_name = meta['file']
    file_dir = meta['dir']
    file_abs = os.path.join(file_dir, file_name + ".transx.json")
    file_path = Path(file_abs)
    info(f"Writing transcription status to {file_path}")
    # read json from file_path as metadata and update the transcribe_status
    with open(file_path, "r") as f:
        metadata = json.load(f)
    metadata["transcribe_status"] = status
    with open(file_path, "w") as f:
        json.dump(metadata, f)


def get_object(bucket, prefix, file_name, output_file = None):
    """Downloads the transcription results from S3."""
    file_key = prefix + "/" + file_name
    s3_url = f"s3://{bucket}/{file_key}"
    try:
        response = s3.get_object(Bucket=bucket, Key=file_key)
        if not output_file:
            output_file = file_name
        info(f"Downloading [{s3_url}] as [{output_file}]")
        with open(output_file, 'wb') as f:
            f.write(response['Body'].read())
        info(f"Downloaded transcription for {file_name} to {output_file}")
    except ClientError as e:
        error(f"Failed to download transcription for {s3_url}: {e}")

def download(job_info):
    """Downloads the transcription results from S3."""
    job_name = job_info.get('TranscriptionJobName')
    info(f"Downloading transcriptions for {job_name}")
    debug(f"Job info: {job_info}")
    debug("==========================================")
    file_name = job_info.get('FileName')
    bucket = job_info['OutputBucketName']
    prefix = file_name + "/transcribe/" + job_name
    file_dir = job_info['FileDir']
    transcribe_out = os.path.join(file_dir, file_name + ".transcribe.json")
    vtt_file = file_name + ".vtt"
    vtt_out = os.path.join(file_dir, vtt_file)    
    srt_file = file_name + ".srt"
    srt_out = os.path.join(file_dir, srt_file)
    get_object(bucket, prefix, file_name, transcribe_out)
    get_object(bucket, prefix, vtt_file, vtt_out)
    get_object(bucket, prefix, srt_file, srt_out)

@click.command()
@click.option('--directory', default=None, help='Directory to search in')
def run(directory):
    """Transcribes all audio files in the specified directory matching the glob pattern."""
    metas = find_metadata()
    info(f"Found {len(metas)} files to transcribe.")
    for meta in metas:
        file_name = meta['file']
        job_name = f"transcribe_{file_name}_{minstamp()}"
        info(f"Starting transcription job for {file_name}")
        job_info = start_transcription_job(meta, job_name)
        info("Transcription job started.")
        status = check_job_status(job_name)
        write_transcription_metadata(meta, status)
        info(f"Completed transcription job for {file_name} with status: {status}")
        download(job_info)

if __name__ == '__main__':
    run()

import click
from pprint import pformat
from .utils import *
from .logs import *
from .files import *
from .config import Config
from . import cmd
import vimeo

vimeo_cli = None


def vimeo_client():
    if vimeo_cli:
        return vimeo_cli
    _client_id = resolve(Config.VIMEO_CLIENT_ID)
    _access_token = resolve(Config.VIMEO_ACCESS_TOKEN)
    _client_secret = resolve(Config.VIMEO_CLIENT_SECRET)
    _vimeo = vimeo.VimeoClient(
        token=_access_token,
        key=_client_id,
        secret=_client_secret
    )
    return _vimeo


def create_if_not_exists(folder_name):
    vimeo_cli = vimeo_client()
    ## Check if folder exists
    # as described in https://developer.vimeo.com/api/guides/folders
    # ???


def vimeo_upload(file_path, folder_name, video_name):
    try:
        create_if_not_exists(folder_name)
        # Upload the video
        video_uri = vimeo_client().upload(file_path, data={
            'name': video_name,
            'description': video_name
        })

        if video_uri:
            # Get the video URL
            video_url = f"https://vimeo.com{video_uri}"
            print(f"Video uploaded successfully! Video URL: {video_url}")
            return video_url
        else:
            return "Failed to upload the video. No video URI returned."

    except vimeo.exceptions.VideoUploadFailure as e:
        return f"Video upload failed: {e}"
    except Exception as e:
        return f"An error occurred: {e}"


def is_synced(file_path):
    if not os.path.isfile(file_path):
        print(f"The file does not exist: {file_path}")
        return False

    file_size = os.path.getsize(file_path)



    return False


def vimeo_sync(video):
    folder_name = video.parent.name
    video_name = video.name
    is_synced = is_synced(video)
    if not is_synced:
        vimeo_upload(video, folder_name, video_name)
        info(f"Video {str(video)} uploaded.")
    info("Video synced.")
    return video


def run(directory):
    videos = find_videos(directory)
    for video in videos:
        info(f"Processing video {video}")
        vimeo_sync(video)
    info(f"Processed {len(videos)} videos:")
    return {}

@cmd.cli.command('vimeo')
@click.option('--directory', default=None, help='Directory to search in')
def command(directory, bucket_name):
    result = run(directory)
    info(pformat(result))


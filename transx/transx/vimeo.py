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


def get_folder(data_folder_name):
    v = vimeo_client()
    user_id = resolve(Config.VIMEO_USER_ID)
    request_url = f'/users/{user_id}/projects'
    response = v.get(request_url)
    if response.status_code == 200:
        projects = response.json().get('data')
        for project in projects:
            if project.get('name') == data_folder_name:
                return project
        return None
    else:
        print("Failed to get projects:", response.json())
        return None


def vimeo_upload(file_path):
    try:
        #
        # Upload the video
        info(f"Uploading {file_path} to Vimeo")
        video_name = file_path.name
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
            info("Failed to upload the video. No video URI returned.")
            return None

    except vimeo.exceptions.VideoUploadFailure as e:
        return f"Video upload failed: {e}"
    except Exception as e:
        return f"An error occurred: {e}"


def is_synced(file_path, project_id):
    if not os.path.isfile(file_path):
        print(f"The file does not exist: {file_path}")
        return False
    video_name = file_path.name
    # check if there is a video with same name
    v = vimeo_client()
    user_id = resolve(Config.VIMEO_USER_ID)
    request_url = f'/users/{user_id}/projects/{project_id}/items'
    response = v.get(request_url)
    if response.status_code == 200:
        videos = response.json().get('data')
        for video in videos:
            if video.get('name') == video_name:
                video_uri = video.get('uri')
                info(f"Video {video_name} found with uri[{video_uri}].")
                return True
        return False
    else:
        info("Failed to get videos:", response.json())
    return False


def vimeo_move(vimeo_url, data_folder):
    v = vimeo_client()
    user_id = resolve(Config.VIMEO_USER_ID)
    if not data_folder:
        info("No data_folder provided.")
        return False
    data_folder_uri = data_folder.get("uri")
    data_folder_name = data_folder.get("name")
    data_folder_id = data_folder_uri.split("/")[-1]
    video_id = vimeo_url.split("/")[-1]
    request_url = f'/users/{user_id}/projects/{data_folder_id}/videos/{video_id}'
    response = v.put(request_url, data={})
    if response.status_code == 204:
        info(f"Video moved to data_folder[{data_folder_name}]")
        return True
    else:
        info(f"Failed to move video to data folder {response}")
        return False


def create_folder(data_folder_name, parent_folder_uri=None):
    v = vimeo_client()

    user_id = resolve(Config.VIMEO_USER_ID)
    request_url = f'/users/{user_id}/projects'
    body = {
        'name': data_folder_name
    }
    if parent_folder_uri:
        body['parent_folder_uri'] = parent_folder_uri
    response = v.post(request_url, data=body)
    if response.status_code == 201:
        folder_uri = response.json().get('uri')
        info("Folder created:", response.json())
        return folder_uri
    else:
        info("Failed to create folder:", response.json())
        return None


def vimeo_sync(video):
    info("Video not synced.")
    user_folder_name = user_name()
    info(f"Checking vimeo user folder [{user_folder_name}]")
    user_folder = get_folder(user_folder_name)
    user_folder_uri = user_folder.get("uri") if user_folder else None
    if not user_folder:
        info(f"Creating vimeo user folder [{user_folder_name}]")
        user_folder_uri = create_folder(user_folder_name)
        user_folder = get_folder(user_folder_name)
        info(f"Folder [{user_folder.get("name")}] created.")

    data_folder_name = video.parent.name
    info(f"Checking vimeo data folder [{data_folder_name}] in user [{user_folder_uri}]")
    data_folder = get_folder(data_folder_name)
    data_folder_uri = user_folder.get("uri") if user_folder else None
    if not data_folder:
        info(f"Creating vimeo data_folder [{data_folder_name}]")
        data_folder_uri = create_folder(data_folder_name, user_folder_uri)
        data_folder = get_folder(data_folder_name)
        info(f"Folder [{data_folder_uri}] created.")

    is_sync = is_synced(video, data_folder_uri)
    if not is_sync:
        info(f"Uploading {str(video)}")
        vimeo_url = vimeo_upload(video)
        info(f"Moving url[{vimeo_url}] to data_folder[{data_folder_name}]")
        vimeo_move(vimeo_url, data_folder)
        info(f"TODO: Sync subs")

    info(f"Video {str(video)} syncing done.")
    return {}

def run(directory):
    videos = find_videos(directory)
    for video in videos:
        info(f"Processing video {video}")
        vimeo_sync(video)
    info(f"Processed {len(videos)} videos:")
    return {}


@cmd.cli.command('vimeo')
@click.option('--directory', default=None, help='Directory to search in')
def command(directory):
    result = run(directory)
    info(pformat(result))

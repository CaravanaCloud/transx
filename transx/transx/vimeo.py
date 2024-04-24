import click
from pprint import pformat
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


def vimeo_upload(file_path, folder_uri):
    try:
        #
        # Upload the video
        info(f"Uploading {file_path} to Vimeo")
        video_name = file_path.name
        body = {
            'name': video_name,
            'description': video_name
        }
        if folder_uri:
            body['folder_uri'] = folder_uri
        video_uri = vimeo_client().upload(file_path, data=body)
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


def is_synced(file_path, project_url):
    if not os.path.isfile(file_path):
        warning(f"The file does not exist: {file_path}")
        return False
    video_name = file_path.name
    info(f"Checking if video file [{video_name}] is synced in [{project_url}].")
    # check if there is a video with same name
    v = vimeo_client()
    request_url = f'{project_url}/items'
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


def find_subs(file_path):
    subs_dir = file_path.parent / "subtitles"
    if not subs_dir.exists():
        info(f"Subtitles dir not found in {subs_dir}")
        return []
    subs = []
    for sub_file in subs_dir.iterdir():
        file_name = file_path.name
        if file_name in sub_file.name:
            subs.append(sub_file)
    return subs


def vimeo_upload_sub(vimeo_url, sub):
    try:
        #
        # Upload the video
        info(f"Uploading {sub} to video {vimeo_url}")
        sub_name = sub.name
        body = {
            'name': sub_name,
            'description': sub_name
        }
        sub_uri = vimeo_client().upload(sub, data=body)
        if sub_uri:
            # Get the video URL
            sub_url = f"https://vimeo.com{sub_uri}"
            print(f"Subtitle uploaded successfully! Subtitle URL: {sub_url}")
            return sub_url
        else:
            info("Failed to upload the subtitle. No subtitle URI returned.")
            return None

    except vimeo.exceptions.VideoUploadFailure as e:
        return f"Subtitle upload failed: {e}"
    except Exception as e:
        return f"An error occurred: {e}"


def vimeo_assoc_sub(vimeo_url, sub_uri, lang_code):
    v = vimeo_client()
    video_id = vimeo_url.split('/')[-1]

    # Prepare the payload for the subtitle track
    data = {
        'type': 'subtitles',
        'language': lang_code,
        'name': lang_code+' subtitles',
        'file_url': sub_uri,
        'active': True
    }

    # Construct the endpoint URL for adding the text track
    api_endpoint = f'/videos/{video_id}/texttracks'

    # Send a POST request to add the subtitle track
    response = v.post(api_endpoint, data=data, field='texttrack')

    # Check the response
    if response.status() == 201:
        print("Subtitle successfully associated with the video.")
        return response.json()
    else:
        print("Failed to associate subtitle with the video.")
        return None


def vimeo_upload_subs(video, vimeo_url):
    info("Uploading subtitles")
    subs = find_subs(video)
    for sub in subs:
        sub_name = sub.name
        lang_code = sub_name.split(".")[0]
        info(f"Uploading subtitle [{lang_code}] {sub_name}")
        sub_uri = vimeo_upload_sub(vimeo_url, sub)
        if sub_uri:
            info(f"Subtitle {sub_name} uploaded tp {sub_uri}.")
            vimeo_assoc_sub(vimeo_url, sub_uri, lang_code)
        else:
            info(f"Failed to upload subtitle {sub_name}")
    return None


def vimeo_sync(video):
    info("Video not synced.")
    # load user folder
    user_folder_name = user_name()
    info(f"Checking vimeo user folder [{user_folder_name}]")
    user_folder = get_folder(user_folder_name)
    user_folder_uri = user_folder.get("uri") if user_folder else None
    if not user_folder:
        info(f"Creating vimeo user folder [{user_folder_name}]")
        user_folder_uri = create_folder(user_folder_name)
        user_folder = get_folder(user_folder_name)
        info(f"Folder [{user_folder.get("name")}] created.")
    # load data folder
    data_folder_name = video.parent.name
    info(f"Checking vimeo data folder [{data_folder_name}] in user [{user_folder_uri}]")
    data_folder = get_folder(data_folder_name)
    data_folder_uri = user_folder.get("uri") if user_folder else None
    if not data_folder:
        info(f"Creating vimeo data_folder [{data_folder_name}]")
        data_folder_uri = create_folder(data_folder_name, user_folder_uri)
        data_folder = get_folder(data_folder_name)
        info(f"Folder [{data_folder_uri}] created.")
    # check if video is synced
    is_sync = is_synced(video, data_folder_uri)
    if not is_sync:
        info(f"Uploading {str(video)}")
        vimeo_url = vimeo_upload(video, data_folder_uri)
        # info(f"Moving url[{vimeo_url}] to data_folder[{data_folder_name}]")
        # vimeo_move(vimeo_url, data_folder)
        info(f"TODO: Sync subs")
        vimeo_upload_subs(video, vimeo_url)

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

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
    _client_id = Config.VIMEO_CLIENT_ID.resolve()
    _access_token = Config.VIMEO_ACCESS_TOKEN.resolve()
    _client_secret = Config.VIMEO_CLIENT_SECRET.resolve()
    _vimeo_cli = vimeo.VimeoClient(
        token=_access_token,
        key=_client_id,
        secret=_client_secret
    )
    return _vimeo_cli


def vimeo_user_id():
    user_id = Config.VIMEO_USER_ID.resolve()
    if not user_id:
        warning("Vimeo User ID not found.")
        return None
    return user_id


def get_folder(data_folder_name):
    v = vimeo_client()
    user_id = vimeo_user_id()
    request_url = f'/users/{user_id}/projects'
    debug(f"Get folder [{user_id}]/{data_folder_name}")
    response = v.get(request_url)
    if response.status_code == 200:
        projects = response.json().get('data')
        for project in projects:
            if project.get('name') == data_folder_name:
                info(f"Folder [{data_folder_name}] found for user [{user_id}]")
                return project
        info(f"Folder [{data_folder_name}] not found for user [{user_id}]")
        return None
    else:
        warning("Failed to get projects:", response.json())
        return None


def vimeo_upload(file_path, folder_uri):
    try:
        #
        # Upload the video
        info(f"Uploading {file_path.name} to [{folder_uri}]")
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
            info(f"Video uploaded successfully! Video URL: {video_url}")
            return video_url
        else:
            info("Failed to upload the video. No video URI returned.")
            return None

    except vimeo.exceptions.VideoUploadFailure as e:
        return f"Video upload failed: {e}"
    except Exception as e:
        return f"An error occurred: {e}"


def get_video(file_path, project_url):
    if not os.path.isfile(file_path):
        warning(f"The file does not exist: {file_path}")
        return None
    video_name = file_path.name
    info(f"Checking if video file [{video_name}] is synced in [{project_url}].")
    # check if there is a video with same name
    v = vimeo_client()
    request_url = f'{project_url}/items'
    response = v.get(request_url)
    if response.status_code == 200:
        data = response.json().get('data')
        videos = list(filter(lambda x: x.get('type') == 'video', data))
        info(f"Found [{len(videos)}] videos in project [{project_url}].")
        for v in videos:
            video_el = v.get("video")
            v_name = video_el.get('name')
            matches = v_name == video_name
            debug(f"== Matching [{v_name}]x[{video_name}] => {matches}")
            if matches:
                debug(f"{pformat(video_el)}")
                debug(f"Video {video_name} found with uri[{video_el.get("uri")}].")
                return video_el
        return None
    else:
        info("Failed to get videos:", response.json())
    return None


def vimeo_move(vimeo_url, data_folder):
    v = vimeo_client()
    user_id = Config.VIMEO_USER_ID.resolve()
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

    user_id = Config.VIMEO_USER_ID.resolve()
    request_url = f'/users/{user_id}/projects'
    body = {
        'name': data_folder_name
    }
    if parent_folder_uri:
        body['parent_folder_uri'] = parent_folder_uri
    response = v.post(request_url, data=body)
    if response.status_code == 201:
        folder_uri = response.json().get('uri')
        info(f"Folder [{data_folder_name}] created at [{folder_uri}]", response.json())
        return folder_uri
    else:
        info("Failed to create folder:", response.json())
        return None


import re

lang_re = re.compile(r'^[a-z]{2}(-[A-Z]{2})?$')


def is_sub_file(file_path, sub_file):
    video_name = file_path.name
    sub_name = sub_file.name
    file_split = sub_name.split(".")
    sub_ext = file_split[-1]
    if sub_ext != "vtt":
        debug(f"Skipping non-vtt sub [{sub_name}]")
        return False
    if len(file_split) < 2:
        return False
    lang_code = file_split[-2]
    is_lang = lang_re.match(lang_code)
    if not is_lang:
        return False
    video_name_base = video_name.split(".")[0]
    sub_name_base = sub_name
    matches = video_name_base in sub_name_base
    debug(f"Checking if [{video_name_base}]x[{sub_name_base}] => {matches}")
    return matches


def find_subs(file_path):
    subtitles_dir = file_path.parent / "subtitles"
    subs_dir = file_path.parent / "subs"
    dirs = [subtitles_dir, subs_dir]
    subs = []
    for adir in dirs:
        if not subs_dir.exists():
            info(f"Subtitles dir not found in {subs_dir}")
            continue
        for sub_file in adir.iterdir():
            if is_sub_file(file_path, sub_file):
                subs.append(sub_file)
    file_names = list(map(lambda s: s.name, subs))
    info(f"Found [{len(subs)}] subtitle files for file[{file_path.name}]:[{file_names}].")
    return subs


def vimeo_upload_sub(video, vimeo_url, sub, data_folder_uri, lang_code):
    # try:
    #
    # Upload the video
    info(f"Uploading {sub} to video {vimeo_url}")
    video_data = get_video(video, data_folder_uri)
    video_uri = video_data.get("uri")
    metadata = video_data.get("metadata", {})
    connections = metadata.get("connections", {})
    texttracks = connections.get("texttracks", {})
    tracks_uri = texttracks.get("uri")
    if not tracks_uri:
        warning(f"URI not found for texttracks of {video_uri}")
    v = vimeo_client()
    info(f"Creating text tracks resource [{tracks_uri}]")
    body = {
      "type": f"{"subtitles"}",
      "language": f"{lang_code}",
      "name": f"{sub.name}"
    }
    res = v.post(tracks_uri, data=body)
    if res.status_code == 201:
        data = res.json() #.get('data', {})
        link = data.get("link")
        info(f"Subtitle creation success [{link}]")
        put_res = v.put(link, sub)
        if put_res.status_code == 200:
            info("Subtitle PUT success")
            put_data = put_res.json().get('data')
            sub_uri = put_data.get("uri")
            patch_res = v.patch(sub_uri, { "active": "true" })
            if patch_res.status_code == 200:
                info("Subtitle PATCH success")
            else:
                warning("Subtitle PATCH failed")
        else:
            warning("Subtitle PUT failed")
        return {}
    else:
        warning("Subtitle creation failed ")
        warning(res)
        return None


def vimeo_assoc_sub(vimeo_url, sub_uri, lang_code):
    v = vimeo_client()
    video_id = vimeo_url.split('/')[-1]

    # Prepare the payload for the subtitle track
    data = {
        'type': 'subtitles',
        'language': lang_code,
        'name': lang_code,
    }

    # Construct the endpoint URL for adding the text track
    api_endpoint = f'/videos/{video_id}/texttracks'

    # Send a POST request to add the subtitle track
    response = v.post(api_endpoint, data=data)

    # Check the response
    if response.status_code == 201:
        info("Subtitle successfully associated with the video.")
        return response.json()
    else:
        warning("Failed to associate subtitle with the video.")
        return None


def list_subs(vimeo_url):
    video_id = vimeo_url.split('/')[-1]
    v = vimeo_client()

    # Get text tracks for each video
    tracks_response = v.get(f'/videos/{video_id}/texttracks')
    tracks = tracks_response.json()['data']
    info(f"Found [{len(tracks)}] text tracks for video [{vimeo_url}]")
    subs = []
    for track in tracks:
        track_lang = track.get("language")
        info("==== track ====")
        info(pformat(track))
        subs.append(track_lang)
    return subs


def is_synced_sub(video, vimeo_url, data_folder_uri, sub, lang_code):
    subs = list_subs(vimeo_url)
    result = lang_code in subs
    info(f"Sub found for [{lang_code}] at [{vimeo_url}]: [{result}]")
    return result


def vimeo_upload_subs(video, vimeo_url, data_folder_uri):
    subs = find_subs(video)
    info(f"Uploading [{len(subs)}] subs for [{video.name}]")
    for sub in subs:
        sub_name = sub.name
        lang_code = sub_name.split(".")[0]

        if is_synced_sub(video, vimeo_url, data_folder_uri, sub, lang_code):
            info("Sub already in sync, skipping")
            continue

        info(f"Uploading subtitle [{lang_code}] {sub_name}")
        sub_uri = vimeo_upload_sub(video, vimeo_url, sub, data_folder_uri, lang_code)
        if sub_uri:
            info(f"Subtitle {sub_name} uploaded tp {sub_uri}.")
            vimeo_assoc_sub(vimeo_url, sub_uri, lang_code)
        else:
            info(f"Failed to upload subtitle {sub_name}")
    return None


def vimeo_sync(video, user_folder):
    # load data folder
    data_folder_name = video.parent.name
    user_folder_uri = user_folder.get("uri")
    debug(f"Checking vimeo data folder [{data_folder_name}] in user [{user_folder_uri}]")
    data_folder = get_folder(data_folder_name)
    if not data_folder:
        debug(f"Creating vimeo data folder [{data_folder_name}]")
        create_folder(data_folder_name, user_folder_uri)
        data_folder = get_folder(data_folder_name)
        debug(f"Data Folder [{data_folder.get("uri")}] created.")
    info(f"Data folder [{data_folder_name} found at [{data_folder.get("uri")}]")
    data_folder_uri = data_folder.get("uri")
    video_data = get_video(video, data_folder_uri)
    vimeo_url = video_data.get("uri") if video_data else None
    info(f"vimeo url for [{video.name}]@[{data_folder_uri}] = [{vimeo_url}]")
    if not vimeo_url:
        info(f"Video {str(video.name)} is not synced in [{data_folder_uri}]. uploading...")
        vimeo_url = vimeo_upload(video, data_folder_uri)
    info(f"Uploading subs of [{video}] to vimeo[{vimeo_url}] folder[{data_folder_uri}]")
    vimeo_upload_subs(video, vimeo_url, data_folder_uri)

    info(f"Video {str(video)} syncing done.")
    return {}


def run(directory):
    uid = vimeo_user_id()
    if not uid:
        error("Could not find vimeo user")
        return None
    # load user folder
    username = user_name()
    user_folder_name = username
    debug(f"Checking vimeo user folder [{user_folder_name}]")
    user_folder = get_folder(user_folder_name)
    if not user_folder:
        debug(f"Creating vimeo user folder [{user_folder_name}]")
        create_folder(user_folder_name)
        user_folder = get_folder(user_folder_name)
        debug(f"Folder [{user_folder.get("name") if user_folder else "USER_FOLDER_FAILED"}] created.")
    info(f"user folder for [{username}] found [{user_folder.get("uri")}]")
    videos = find_videos(directory)
    info(f"Syncing [{len(videos)}] video files to vimeo")
    for video in videos:
        debug(f"Processing video file {video}")
        vimeo_sync(video, user_folder)
    info(f"Processed {len(videos)} videos.")
    return {}


@cmd.cli.command('vimeo')
@click.option('--directory', default=None, help='Directory to search in')
def command(directory):
    result = run(directory)
    info(pformat(result))

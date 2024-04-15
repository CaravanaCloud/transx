import os
import vimeo
import fnmatch
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Fetch Vimeo API credentials from environment variables
client_id = os.getenv('VIMEO_CLIENT_ID')
client_secret = os.getenv('VIMEO_CLIENT_SECRET')
access_token = os.getenv('VIMEO_ACCESS_TOKEN')

# Initialize Vimeo client
client = vimeo.VimeoClient(
    token=access_token,
    key=client_id,
    secret=client_secret
)

def find_files(directory, pattern):
    """ Recursively finds all files matching the pattern. """
    logging.info(f"Scanning directory {directory} for files matching {pattern}")
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename

def find_or_create_folder(folder_name):
    """ Find if folder exists on Vimeo, create if not. """
    logging.info(f"Checking for existing folder '{folder_name}' on Vimeo.")
    response = client.get('/me/projects', params={"query": folder_name, "per_page": 100})
    if response.status_code == 200:
        projects = response.json()['data']
        for project in projects:
            if project['name'] == folder_name:
                logging.info(f"Folder '{folder_name}' found on Vimeo.")
                return project['uri']
    logging.info(f"Folder '{folder_name}' not found. Creating new folder.")
    response = client.post('/me/projects', data={"name": folder_name})
    if response.status_code == 201:
        logging.info(f"Folder '{folder_name}' created successfully.")
        return response.json()['uri']
    else:
        logging.error(f"Failed to create folder: {response.json().get('error', 'No error message available')}")
        raise Exception("Failed to create folder")

def upload_video(video_path, folder_uri):
    """ Uploads a video to Vimeo and returns the video URI. """
    logging.info(f"Uploading video {video_path} to Vimeo.")
    try:
        video_uri = client.upload(video_path, data={
            'name': os.path.basename(video_path),
            'description': 'Uploaded automatically via API'
        })
        logging.info(f"Video {video_path} uploaded successfully to {video_uri}")

        # Correct API endpoint to add video to a project/folder
        # Assuming folder_uri is correct and video_uri needs proper formatting
        if video_uri.startswith('/videos/'):
            video_id = video_uri.split('/')[-1]
            add_video_to_folder_response = client.put(f'{folder_uri}/videos/{video_id}')
            if add_video_to_folder_response.status_code == 204:
                logging.info(f"Video {video_uri} added to folder {folder_uri}")
            else:
                logging.error(f"Failed to add video {video_uri} to folder {folder_uri}: {add_video_to_folder_response.status_code}")
        else:
            logging.error(f"Unexpected video URI format: {video_uri}")
            return None
        return video_uri
    except Exception as e:
        logging.error(f"Failed to upload video {video_path}: {str(e)}")
        return None

def attach_subtitles(video_uri, subtitle_path):
    """ Attaches subtitle files to the video. """
    logging.info(f"Attaching subtitles from {subtitle_path} to video {video_uri}.")
    with open(subtitle_path, 'rb') as f:
        response = client.upload_texttrack(
            video_uri,
            data={
                'type': 'subtitles',
                'language': 'en',
                'name': os.path.basename(subtitle_path)
            },
            file_data=f.read(),
            filename=os.path.basename(subtitle_path)
        )
    if response.status_code == 201:
        logging.info(f"Subtitles {subtitle_path} attached successfully to {video_uri}.")
    else:
        logging.error(f"Failed to attach subtitles {subtitle_path} to video {video_uri}: {response.json().get('error', 'No error message available')}")
        raise Exception("Failed to attach subtitles")

def process_videos():
    directory = os.getenv('TRANSX_PATH', os.getcwd())
    video_files = list(find_files(directory, '*.mp4'))
    for video_path in video_files:
        folder_name = os.path.basename(os.path.dirname(video_path))
        folder_uri = find_or_create_folder(folder_name)
        video_uri = upload_video(video_path, folder_uri)
        base_name = os.path.splitext(video_path)[0]
        subtitle_paths = list(find_files(os.path.dirname(video_path), f'{base_name}.srt')) + list(find_files(os.path.dirname(video_path), f'{base_name}.vtt'))
        for subtitle_path in subtitle_paths:
            attach_subtitles(video_uri, subtitle_path)

def main():
    process_videos()

if __name__ == '__main__':
    main()

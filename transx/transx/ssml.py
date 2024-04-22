import click
from pprint import pformat
from .logs import *
from .utils import *
from . import cmd, files
import webvtt
from pyssml.PySSML import PySSML
from pathlib import Path
import xml.dom.minidom


def to_ssml(vtt_file_path):
    # convert vtt to ssml
    # ???????
    # write to file
    vtt_file = Path(vtt_file_path)
    ssml_file = vtt_file.with_suffix('.ssml')

    # Initialize PySSML object
    ssml = PySSML()

    # Read VTT file and generate SSML content with timing
    for caption in webvtt.read(vtt_file):
        start_time = caption.start_in_seconds
        end_time = caption.end_in_seconds
        duration = end_time - start_time
        ssml.say(caption.text)
        ssml.pause(str(int(duration * 1000)) + 'ms')  # Add a break based on the duration of the caption

    ssml_string = ssml.ssml()
    dom = xml.dom.minidom.parseString(ssml_string)
    pretty_ssml = dom.toprettyxml(indent="  ")
    # Write SSML to file
    with open(ssml_file, 'w') as f:
        f.write(pretty_ssml)

    return ssml_file


def run(directory):
    vtts = files.find_vtt(directory)
    info(f"Converting {len(vtts)} VTT files to SSML.")
    for vtt in vtts:
        to_ssml(vtt)
    return vtts


@cmd.cli.command('ssml')
@click.option('--directory', default=None, help='Directory to search in')
@click.option('--bucket_name', default=None, help='Bucket name')
def command(directory, bucket_name):
    directory = resolve(Config.TRANSX_PATH, directory)
    result = run(directory)
    info(pformat(result))

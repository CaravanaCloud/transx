from .cmd import cli
# fundamentals
from . import about, sync, config, clean, logscmd
# features
from . import transcribe, translate
# developer preview
from . import ssml, vimeo

_commands = [
    about.command,
    config.command,
    sync.command,
    transcribe.command,
    translate.command,
    clean.command,
    ssml.command,
    vimeo.command,
    logscmd.command
]


def main():
    config.init()
    for command in _commands:
        cli.add_command(command)
    cli(obj={})


if __name__ == "__main__":
    main()

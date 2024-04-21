from .cmd import cli
from . import about, sync, transcribe, translate, config

_commands = [
    about.command,
    config.command,
    sync.command,
    transcribe.command,
    translate.command,
]


def main():
    config.init()
    for command in _commands:
        cli.add_command(command)
    cli(obj={})


if __name__ == "__main__":
    main()

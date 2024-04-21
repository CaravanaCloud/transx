from .cmd import cli
from . import about
from . import sync

_commands = [
    about.command,
    sync.command
]


def main():
    for command in _commands:
        cli.add_command(command)
    cli(obj={})


if __name__ == "__main__":
    main()

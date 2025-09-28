# Callbacks
from typing import Annotated

from typer import Exit, Option


def show_version_and_exit(show_version: bool) -> None:
    if show_version:
        from pyciv7 import __version__

        print(f"pyciv7 {__version__}")
        raise Exit()


# Global options
VersionOpt = Annotated[
    bool,
    Option(
        ...,
        "--version",
        is_eager=True,
        callback=show_version_and_exit,
        help="Show the version and exit.",
    ),
]


# Parameter groups
def global_options(show_version: VersionOpt = False) -> None: ...

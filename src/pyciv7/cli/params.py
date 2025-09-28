# Callbacks
from pathlib import Path
from typing import Annotated, Optional

from typer import Exit, Option

from pyciv7.settings import Settings


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


# Civ 7 installation options
def get_settings_help(field: str) -> str:
    description = Settings.model_fields[field].description or ""
    return (
        "\n".join(description.splitlines()[:-1])
        if "**Environment override**" in description
        else description
    )


Civ7InstallationDirOpt = Annotated[
    Optional[Path],
    Option(
        ...,
        "--civ7-installation-dir",
        file_okay=False,
        exists=True,
        envvar="CIV7_INSTALLATION_DIR",
        rich_help_panel="Civ 7 Installation Options",
        help=get_settings_help("civ7_installation_dir"),
    ),
]

Civ7SettingsDir = Annotated[
    Optional[Path],
    Option(
        ...,
        "--civ7-settings-dir",
        file_okay=False,
        exists=True,
        envvar="CIV7_SETTINGS_DIR",
        rich_help_panel="Civ 7 Installation Options",
        help=get_settings_help("civ7_settings_dir"),
    ),
]
Civ7ReleaseBinOpt = Annotated[
    Optional[Path],
    Option(
        ...,
        "--civ7-release-bin",
        dir_okay=False,
        exists=True,
        envvar="CIV7_RELEASE_BIN",
        rich_help_panel="Civ 7 Installation Options",
        help=get_settings_help("civ7_release_bin"),
    ),
]


# Parameter groups
def global_options(show_version: VersionOpt = False) -> None: ...


def civ7_installation_options(
    civ7_installation_dir: Civ7InstallationDirOpt = None,
    civ7_settings_dir: Civ7SettingsDir = None,
    civ7_release_bin: Civ7ReleaseBinOpt = None,
) -> None: ...

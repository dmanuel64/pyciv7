from pathlib import Path
from typing import Annotated, Optional
from webbrowser import get
from pydantic_xml import ParsingError
from typer import Argument, BadParameter, Option
from typer_di import Depends, TyperDI

from pyciv7 import runner
from pyciv7.cli.params import (
    civ7_installation_options,
    global_options,
    get_settings_help,
)
from pyciv7.modinfo import Mod

app = TyperDI(callback=global_options)


def validate_ext(path: Path, ext: str) -> Path:
    if path.suffix != ext:
        raise BadParameter(f"File must have a '{ext}' extension.")
    return path


# Build arguments
PyModinfoArg = Annotated[
    Path,
    Argument(
        ...,
        dir_okay=False,
        exists=True,
        callback=lambda p: validate_ext(p, ".pymodinfo"),
        help="Path to the .pymodinfo file. The parent directory of .modinfo is assumed as the base path for the mod.",
    ),
]
TargetArg = Annotated[
    Optional[Path],
    Argument(
        ...,
        dir_okay=False,
        metavar="[FILE]",
        callback=lambda p: validate_ext(p, ".modinfo"),
        help="Path to save the built .modinfo file. By default, this will be the same name as the input .pymodinfo file, but with a .modinfo extension.",
    ),
]

# Build options
RunOpt = Annotated[
    Optional[bool],
    Option(
        ...,
        "--run-default / --run-debug",
        "-r / -d",
        rich_help_panel="Build & Run Options",
        help="Load the mod and run Civ 7 after building it.",
    ),
]
LinkOpt = Annotated[
    bool,
    Option(
        ...,
        "--link",
        "-l",
        rich_help_panel="Build & Run Options",
        help="Create a symlink to the mod in the Civ 7 Mods folder.",
    ),
]
# transcrypt_sub_dir: Path = Field(default=Path("transcrypt"))
# """
# Subdirectory name used to store Transcrypt outputs relative to a mod's root directory.

# **Environment override**: `TRANSCRYPT_SUB_DIR`
# """
# sql_sub_dir: Path = Field(default=Path("sql"))
# """
# Subdirectory name used to store SQL outputs relative to a mod's root directory.

# **Environment override**: `SQL_SUB_DIR`
# """
TranscryptSubDirOpt = Annotated[
    Optional[Path],
    Option(
        ...,
        "--transcrypt-sub-dir",
        file_okay=False,
        rich_help_panel="Build & Run Options",
        envvar="TRANSCRYPT_SUB_DIR",
        help=get_settings_help("transcrypt_sub_dir"),
    ),
]
SQLSubDirOpt = Annotated[
    Optional[Path],
    Option(
        ...,
        "--sql-sub-dir",
        file_okay=False,
        rich_help_panel="Build & Run Options",
        envvar="SQL_SUB_DIR",
        help=get_settings_help("sql_sub_dir"),
    ),
]


@app.command()
def build(
    pymodinfo: PyModinfoArg,
    target: TargetArg = None,
    link: LinkOpt = False,
    run_debug: RunOpt = None,
    _sql_sub_dir: SQLSubDirOpt = None,
    _transcrypt_sub_dir: TranscryptSubDirOpt = None,
    _global_options: None = Depends(global_options),
    _civ7_installation_options: None = Depends(civ7_installation_options),
) -> None:
    """Build a mod from a .modinfo file."""
    target = target or pymodinfo.with_suffix(".modinfo")
    try:
        mod = Mod.from_xml(pymodinfo.read_text())
    except ParsingError as e:
        raise BadParameter(
            f"An XML parsing error occurred: {e}", param_hint="modinfo"
        ) from e
    runner.build(mod, path=target.parent, link=link)
    if run_debug is not None:
        runner.run(mod, debug=run_debug)

from pathlib import Path
from typing import Annotated
from pydantic_xml import ParsingError
from typer import Argument, BadParameter, Option
from typer_di import Depends, TyperDI

from pyciv7 import runner
from pyciv7.cli.params import global_options
from pyciv7.modinfo import Mod

app = TyperDI(callback=global_options)

# Build arguments
ModinfoArg = Annotated[
    Path,
    Argument(
        ...,
        dir_okay=False,
        exists=True,
        help="Path to the .modinfo file. The parent directory of .modinfo is assumed as the base path for the mod.",
    ),
]

# Build options
RunOpt = Annotated[
    bool,
    Option(
        ...,
        "--run",
        "-r",
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
RunDebugOpt = Annotated[
    bool,
    Option(
        ...,
        "--run-debug",
        "-d",
        rich_help_panel="Build & Run Options",
        help="Load the mod and run Civ 7 using a debug AppConfig.txt after building it.",
    ),
]


@app.command()
def build(
    modinfo: ModinfoArg,
    link: LinkOpt = False,
    run: RunOpt = False,
    run_debug: RunDebugOpt = False,
    _global_options: None = Depends(global_options),
) -> None:
    """Build a mod from a .modinfo file."""
    try:
        mod = Mod.from_xml(modinfo.read_text())
    except ParsingError as e:
        raise BadParameter(
            f"An XML parsing error occurred: {e}", param_hint="modinfo"
        ) from e
    runner.build(mod, path=modinfo.parent, link=link)
    if run or run_debug:
        runner.run(mod, debug=run_debug)

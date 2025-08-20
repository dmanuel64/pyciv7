"""
Module pertaining to building Civilization 7 mods and running them in debug mode.
"""

from contextlib import contextmanager, nullcontext
from copy import deepcopy
from pathlib import Path
import subprocess
from typing import Any, Generator
import uuid

from rich import print
from rich.status import Status

from pyciv7.modinfo import DatabaseItem, Mod, SQLStatement, ScriptItem
from pyciv7.settings import Settings


@contextmanager
def debug_settings_enabled() -> Generator[None, None, None]:
    """
    Runs the game in debug mode with the app options suggested in the `Getting Started` guide
    enabled. The settings are reverted upon exiting the context manager.

    Returns:
        A context manager with the debug app options enabled.
    """
    app_options = Settings().civ7_settings_dir / "AppOptions.txt"
    old_options = app_options.read_text()
    new_options = []
    for line in old_options.splitlines():
        if "CopyDatabasesToDisk" in line:
            line = "CopyDatabasesToDisk 1"
        elif "EnableTuner" in line:
            line = "EnableTuner 1"
        elif "EnableDebugPanels" in line:
            line = "EnableDebugPanels 1"
        elif "UIDebugger" in line:
            line = "UIDebugger 1"
        elif "UIFileWatcher" in line:
            line = "UIFileWatcher 1"
        new_options.append(line)
    app_options.write_text("\n".join(new_options))
    yield
    app_options.write_text(old_options)


def build(
    mod: Mod,
    path: Path = Settings().civ7_settings_dir / "Mods",
    exists_ok: bool = False,
):
    """
    Builds a new Civilization 7 mod from Python bindings. The root directory of the mod will be
    named as the `id` of the `Mod`.

    Parameters:
        mod: The `Mod` to build.
        path: Directory of where the mod should be stored under. Normally, this is the `Mods` subdirectory under the Civilization 7 settings directory (default.)
        exists_ok: `True` if it is okay to overwrite the directory even if it already exists. This is needed for rebuilds.
    """
    with Status(f'Building .modinfo for "{mod.id}"...'):
        mod = deepcopy(mod)
        # Get mod directory
        path /= mod.id
        try:
            path.mkdir(parents=True, exist_ok=exists_ok)
        except FileExistsError as e:
            raise FileExistsError(
                f'Mod "{mod.id}" already exists. Use "exists_ok=True" to rebuild it.'
            ) from e
        # Create directory for transcrypt
        transcript_dir = path / "transcrypt"
        transcript_dir.mkdir(exist_ok=True)
        # Handle Python scripts and ORM expressions
        action_groups = mod.action_groups or []
        for action_group in action_groups:
            for action in action_group.actions:
                for item in action.items:
                    if isinstance(item, ScriptItem):
                        script_path = Path(item.path)
                        if script_path.suffix.lower() == ".py":
                            # Transcribe Python to JavaScript
                            try:
                                subprocess.run(
                                    [
                                        "transcrypt",
                                        "--build",
                                        "--outdir",
                                        transcript_dir,
                                        script_path,
                                    ],
                                    check=True,
                                )
                            except subprocess.CalledProcessError as e:
                                raise ValueError(
                                    f'Failed to transcribe "{script_path.name}" to JavaScript'
                                ) from e
                            item.path = transcript_dir / script_path.with_suffix(".js")
                            if item.hook:
                                if item.hook == "shell":
                                    item.hook = (
                                        path
                                        / "modules"
                                        / "ui"
                                        / "shell"
                                        / "main-menu"
                                        / "main-menu.js"
                                    )
                                    item.hook.parent.mkdir(parents=True, exist_ok=True)
                                # Hook script to existing script
                                item.hook = Path(item.hook)
                                relative_path = item.hook.relative_to(path)
                                script_content = Path(
                                    Settings().civ7_installation_dir / relative_path
                                ).read_text()
                    elif isinstance(item, DatabaseItem):
                        if isinstance(item, SQLStatement):
                            # Convert ORM to SQL
                            statement = str(
                                item.compile(compile_kwargs={"literal_binds": True})
                            )
                            sql_file = (
                                path / str(uuid.uuid4()).replace("-", "")
                            ).with_suffix(".sql")
                            sql_file.write_text(statement)
                            item.path = sql_file


def run(mod: Mod, debug: bool = True, **build_kwargs: Any):
    """
    Builds the `Mod`, then runs the Civilization 7 executable.

    Parameters:
        mod: `Mod` to build.
        debug: `True` if the game should be ran in debug mode.
        build_kwargs: Keyword arguments to pass to `build`.
    """
    ctx = debug_settings_enabled() if debug else nullcontext()
    with ctx:
        build(mod, **build_kwargs)
        try:
            if debug:
                print("Running Civilization 7 in debug mode")
            else:
                print("Running Civilization 7 in release mode")
            subprocess.run(Settings().civ7_release_bin)
        except FileNotFoundError as e:
            raise FileNotFoundError(
                "Cannot the Civilization VII's release binary. Manually set this path via"
                "CIV7_RELEASE_BIN"
            ) from e

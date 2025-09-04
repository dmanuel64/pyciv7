"""
Module pertaining to building Civilization 7 mods and running them in debug mode.
"""

import subprocess
from contextlib import contextmanager, nullcontext
from pathlib import Path
from typing import Any, Callable, Generator, Optional
import warnings

from rich import print
from rich.status import Status

from pyciv7.errors import ModExistsError
from pyciv7.modinfo import Mod
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
    path: Optional[Path] = None,
    overwrite: bool = False,
    settings_factory: Callable[[], Settings] = lambda: Settings(),
) -> None:
    """
    Builds a new Civilization 7 mod from Python bindings. The root directory of the mod will be
    named as the `id` of the `Mod`.

    Parameters:
        mod: The `Mod` to build.
        path: Directory of where the mod should be stored under. Normally, this is the `Mods` subdirectory under the Civilization 7 settings directory (default.)
        overwrite: `True` if it is okay to overwrite the directory even if it already exists. This is needed for rebuilds.
        settings: Common `Settings` for pyciv7.

    Deprecated:
        path: This parameter will be removed in v2.0.0. Use `mod.mod_path` instead.
    """
    settings = settings_factory()
    if path:
        warnings.warn(
            'The "path" argument is deprecated. Use "mod.mod_dir" instead.',
            DeprecationWarning,
            stacklevel=2,
        )
        mod.mod_dir = path
    if not mod.mod_dir:
        mod.mod_dir = settings.civ7_settings_dir / "Mods" / mod.id
    mod_dir = Path(mod.mod_dir)
    if (mod_dir / ".modinfo").exists() and not overwrite:
        raise ModExistsError(
            f'Mod "{mod.id}" already exists. Use "overwrite=True" to overwrite/rebuild it.'
        )
    with Status(f'Building .modinfo for "{mod.id}"...'):
        # Create .modinfo file
        (mod_dir / ".modinfo").write_text(
            mod.to_xml(encoding="unicode", exclude_none=True)  # type: ignore
        )


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

"""
Build and run Civilization 7 mods.

This module provides utilities for creating, running, and debugging Civilization 7
mods from Python. It includes helpers for building mods into their correct directory
structure, running the Civilization 7 executable, and enabling debug app options
temporarily for development.
"""

import os
import shutil
import subprocess
from contextlib import contextmanager, nullcontext
from pathlib import Path
from typing import Any, Callable, Generator, Optional, Union, overload
from warnings import deprecated

from rich import print
from rich.status import Status

from pyciv7.errors import (
    JavaScriptCompatibilityError,
    ModExistsError,
    ModNotFoundError,
    RelativePathRequired,
    SQLCompatibilityError,
)
from pyciv7.modinfo import DatabaseItemsAction, ItemsAction, Mod
from pyciv7.modinfo_extensions import PythonGameScripts
from pyciv7.settings import Settings
from pyciv7.utils import StrPath


@contextmanager
def debug_settings_enabled() -> Generator[None, None, None]:
    """
    Temporarily enables Civilization 7's debug app options.

    This context manager updates `AppOptions.txt` with the debug settings recommended
    in the *Getting Started* guide. Once the context is exited, the original settings
    are restored automatically.

    Yields:
        Control to the caller with debug settings enabled.
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


@overload
def build(
    mod: Mod,
    *,
    path: Optional[Path] = None,
    overwrite: bool = False,
    link: bool = False,
) -> None: ...


@overload
@deprecated(
    "`settings_factory` is deprecated; configure `Settings` directly with environment variables.",
)
def build(
    mod: Mod,
    *,
    path: Optional[Path] = None,
    overwrite: bool = False,
    settings_factory: Optional[Callable[[], Settings]],
    link: bool = False,
) -> None: ...


def build(
    mod: Mod,
    path: Optional[Path] = None,
    overwrite: bool = False,
    settings_factory: Optional[Callable[[], Settings]] = None,
    link: bool = False,
) -> None:
    """
    Builds a new Civilization 7 mod from Python bindings.

    Args:
        mod: The `Mod` to build.
        path: Directory where the mod should be stored.
            Normally this is the `Mods` subdirectory under the Civilization 7 settings
            directory
        overwrite: Whether to overwrite the directory if it already exists.
            This must be `True` for rebuilds
        settings_factory: *Deprecated*: Factory for creating common settings for pyciv7.
        link: Whether to create a symlink to the mod in the Civ 7 Mods folder.

    Raises:
        ModExistsError: If the mod already exists and `overwrite` is `False`.

    Deprecated:
        - `settings_factory`: This parameter will be removed in v2.0.0. Configure `Settings`
        directly with environment variables.
    """
    settings = Settings()
    if settings_factory:
        settings = settings_factory()
    default_mod_dir = settings.civ7_settings_dir / "Mods" / mod.id
    mod_dir = Path(path or default_mod_dir)
    if (mod_dir / ".modinfo").exists() and not overwrite:
        raise ModExistsError(
            f'Mod "{mod.id}" already exists. Use "overwrite=True" to overwrite/rebuild it.'
        )
    with Status(f'Building .modinfo for "{mod.id}"...'):
        # Resolve compatibility issues for actions
        # TODO: this doesn't take into account for any other fields such as conditions
        common_items_dir = os.path.commonpath(
            i
            for ag in mod.action_groups or []
            for a in ag.actions or []
            for i in a.items
            if isinstance(i, (str, Path))
        )
        for action_group in mod.action_groups or []:
            actions = action_group.actions or []
            for idx, action in enumerate(actions):
                try:
                    action.check_modinfo_compatibility()
                except SQLCompatibilityError:
                    if isinstance(action, DatabaseItemsAction):
                        # Convert SQL statements to .sql files
                        actions[idx] = action.to_saved_sql(mod_dir)  # type: ignore
                    else:
                        raise
                except JavaScriptCompatibilityError:
                    if isinstance(action, PythonGameScripts):
                        # Convert Python scripts to JavaScript
                        actions[idx] = action.to_ui_scripts(mod_dir)
                    else:
                        raise
                except RelativePathRequired:
                    if isinstance(action, ItemsAction):
                        # Convert the path to a relative POSIX path
                        actions[idx] = action.to_relative_posix(
                            mod_dir, common_items_dir
                        )  # type: ignore
        mod.check_modinfo_compatibility()
        # Create .modinfo file
        (mod_dir / ".modinfo").write_text(
            mod.to_xml(encoding="unicode", exclude_none=True)  # type: ignore
        )
        if link and mod_dir != default_mod_dir and not default_mod_dir.exists():
            # Create a symlink in the Mods directory
            mod_dir.symlink_to(default_mod_dir, target_is_directory=True)


def run(mod: Optional[Mod] = None, debug: bool = True, **build_kwargs: Any):
    """
    Builds the `Mod`, and runs the Civilization 7 executable.

    Args:
        mod: `Mod` to build.
        debug: Whether to run the game in debug mode.
        build_kwargs: Additional keyword arguments forwarded to `build`.

    Raises:
        FileNotFoundError: If the Civilization 7 release binary cannot be found.

    Example:
        ```python
        from pyciv7 import run, Mod

        my_mod = Mod(id="example_mod", name="Example Mod")
        run(my_mod, debug=True)
        # Civ 7 will open in a separate window with the mod loaded in debug mode
        ```
    """
    ctx = debug_settings_enabled() if debug else nullcontext()
    with ctx:
        if mod:
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


def remove(mod: Union[Mod, StrPath]) -> None:
    """
    Removes a built Civilization 7 mod.

    Args:
        mod: The `Mod` to remove.

    Raises:
        ModNotFoundError: If the mod does not exist.
    """
    if isinstance(mod, Mod):
        return remove(Settings().civ7_settings_dir / "Mods" / (mod.mod_dir or ""))
    mod_dir = Path(mod)
    if not (mod_dir / ".modinfo").exists():
        raise ModNotFoundError(f'Mod does not exist at "{mod_dir}".')
    shutil.rmtree(mod_dir)

"""
Common settings for `pyciv7`.

This module provides centralized configuration for `pyciv7`, including the
installation directory, settings directory, and release binary path of
Civilization 7. Defaults are automatically inferred based on the operating
system and common Steam installation locations, but may also be overridden
via environment variables or a `.env` file.
"""

import os
from pathlib import Path
import platform
from typing import Annotated, Optional
from pydantic import AfterValidator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_default_settings_dir() -> Path:
    """
    Guess the default Civilization 7 settings directory for the current OS.

    - On Windows, attempts to use `%LOCALAPPDATA%` or `%APPDATA%` (falling back to
    `USERPROFILE/AppData/Local`) and appends `Firaxis Games/Sid Meier's Civilization VII`.
    - On macOS, uses `~/Library/Application Support/Civilization VII/`.
    - On Linux, uses `~/My Games/Sid Meier's Civilization VII/`.

    Returns:
        The resolved default settings directory.

    Raises:
        FileNotFoundError: If a common location cannot be inferred for the current platform,
            suggesting manual override via the `CIV7_SETTINGS_DIR` environment variable.
    """
    system = platform.system()
    if system == "Windows":
        try:
            base = Path(
                os.getenv("LOCALAPPDATA")
                or os.getenv("APPDATA")
                or os.path.join(os.environ["USERPROFILE"], "AppData", "Local")
            )
        except KeyError:
            pass
        else:
            return base / "Firaxis Games" / "Sid Meier's Civilization VII"
    elif system == "Darwin":
        return Path.home() / "Library/Application Support/Civilization VII/"
    elif system == "Linux":
        return Path.home() / "My Games/Sid Meier's Civilization VII/"
    raise FileNotFoundError(
        "Cannot determine the common location of Civilization VII's "
        f"installation on {system}. Manually set this path via "
        "CIV7_SETTINGS_DIR"
    )


def get_windows_steam_root() -> Optional[Path]:
    """
    Resolve the Steam root directory on Windows via the registry.

    Reads `HKLM\\SOFTWARE\\WOW6432Node\\Valve\\Steam` and returns the
    `InstallPath` value if present.

    Returns:
        The Steam root directory if found, otherwise `None`.
    """
    import winreg

    key_path = r"SOFTWARE\WOW6432Node\Valve\Steam"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            return Path(winreg.QueryValueEx(key, "InstallPath")[0])
    except FileNotFoundError:
        return None


def guess_posix_steam_root(is_darwin: bool) -> Optional[Path]:
    """
    Heuristically locate the Steam root on macOS or Linux.

    - On macOS: `~/Library/Application Support/Steam`
    - On Linux (checked in order):
        - `~/.steam/steam`
        - `~/.local/share/Steam`
        - `~/.var/app/com.valvesoftware.Steam/.local/share/Steam` (Flatpak)

    Args:
        is_darwin: `True` to search macOS locations, `False` for Linux.

    Returns:
        The most plausible Steam root directory if one exists,
            otherwise `None`.
    """
    if is_darwin:
        return Path.home() / "Library/Application Support/Steam"
    else:
        paths = [
            Path.home() / ".steam/steam",
            Path.home() / ".local/share/Steam",
            Path.home()
            / ".var/app/com.valvesoftware.Steam/.local/share/Steam",  # Flatpak
        ]
        for path in paths:
            if path.exists():
                return path
        return None


def get_civ7_steam_installation_dir() -> Path:
    """
    Resolve the Civilization 7 Steam installation directory.

    On Windows, this uses the registry to find the Steam root. On macOS/Linux, it checks common
    Steam paths. The result is appended with `steamapps/common/Sid Meier's Civilization VII`.

    Returns:
        Path: The Steam installation directory for Civilization 7.

    Raises:
        FileNotFoundError: If the Steam root cannot be determined for the current platform. You
            can override by setting `CIV7_INSTALLATION_DIR` to the desired directory
    """
    system = platform.system()
    if system == "Windows":
        steam_root = get_windows_steam_root()
    else:
        steam_root = guess_posix_steam_root(system == "Darwin")
    if not steam_root:
        raise FileNotFoundError(
            "Cannot determine the common steam location of Civilization VII's "
            f"settings on {system}. Manually set this path via CIV7_INSTALLATION_DIR"
        )
    return steam_root / "steamapps/common/Sid Meier's Civilization VII"


def get_civ7_steam_release_bin() -> Path:
    """
    Resolve the path to the Civilization 7 release binary.

    - On Windows, returns:
    `<install>/Base/Binaries/Win64/Civ7_Win64_DX12_FinalRelease.exe`
    - On macOS/Linux, returns:
    `<install>/Base/Binaries/<system>/Civ7_Win64_Vulkan_FinalRelease`

    Returns:
        Full path to the platform-appropriate release binary.
    """
    binaries_dir = get_civ7_steam_installation_dir() / "Base" / "Binaries"
    system = platform.system()
    if system == "Windows":
        return binaries_dir / "Win64" / "Civ7_Win64_DX12_FinalRelease.exe"
    else:
        # TODO: Verify this path on macOS and Linux
        return binaries_dir / system / "Civ7_Win64_Vulkan_FinalRelease"


ResolvedPath = Annotated[
    Path, AfterValidator(lambda p: Path(os.path.expandvars(p)).resolve())
]


class Settings(BaseSettings):
    """
    Common settings for `pyciv7`.

    This Pydantic settings model provides unified access to the key paths used by `pyciv7`.
    Defaults are inferred from the operating system and common Steam locations, but every field
    can be overridden via environment variables or a local `.env` file.
    """

    model_config = {
        "env_file": Path(__file__).parent.parent.parent / ".env",
        "env_file_encoding": "utf-8",
        "use_attribute_docstrings": True,
    }

    civ7_installation_dir: ResolvedPath = Field(
        default_factory=get_civ7_steam_installation_dir
    )
    """
    The root installation directory of Civilization 7.

    **Environment override**: `CIV7_INSTALLATION_DIR`
    """
    civ7_settings_dir: ResolvedPath = Field(default_factory=get_default_settings_dir)
    """
    The Civilization 7 app settings directory (i.e., where `AppOptions.txt` lives)

    **Environment override**: `CIV7_SETTINGS_DIR`
    """
    civ7_release_bin: ResolvedPath = Field(default_factory=get_civ7_steam_release_bin)
    """
    Full path to the Civilization 7 release executable (platform-specific).

    **Environment override**: `CIV7_RELEASE_BIN`
    """
    transcrypt_sub_dir: Path = Field(default=Path("transcrypt"))
    """
    Subdirectory name used to store Transcrypt outputs relative to a mod's root directory.

    **Environment override**: `TRANSCRYPT_SUB_DIR`
    """
    sql_sub_dir: Path = Field(default=Path("sql"))
    """
    Subdirectory name used to store SQL outputs relative to a mod's root directory.

    **Environment override**: `SQL_SUB_DIR`
    """

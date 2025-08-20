import os
import pytest

from pyciv7.settings import Settings


@pytest.fixture(scope="session", autouse=True)
def settings(tmp_path_factory) -> Settings:
    civ7_dir = tmp_path_factory.mktemp("civ7_files")
    installation_dir = civ7_dir / "installation"
    settings_dir = civ7_dir / "settings"
    installation_dir.mkdir()
    settings_dir.mkdir()
    release_bin = installation_dir / "Base" / "Binaries" / "System" / "Civ7.exe"
    release_bin.parent.mkdir(parents=True)
    release_bin.touch()
    os.environ["CIV7_INSTALLATION_DIR"] = str(installation_dir)
    os.environ["CIV7_SETTINGS_DIR"] = str(settings_dir)
    os.environ["CIV7_RELEASE_BIN"] = "baz"
    return Settings()

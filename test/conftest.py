import os

import pytest

from pyciv7.modinfo import (
    ActionGroup,
    AgeInUse,
    Criteria,
    Mod,
    Properties,
    UpdateDatabase,
)
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


@pytest.fixture
def fxs_new_policies_sample(tmp_path) -> Mod:
    mod_dir = tmp_path / "fxs-new-policies"
    antiquity_traditions = mod_dir / "data" / "antiquity-traditions.xml"
    antiquity_traditions.parent.mkdir(parents=True)
    antiquity_traditions.touch()
    mod = Mod(
        id="fxs-new-policies",
        version="1",
        properties=Properties(
            name="Antiquity Policies",
            description="Adds new policies to the Antiquity Age",
            authors="Firaxis",
            affects_saved_games=True,
        ),
        action_criteria=[
            Criteria(
                id="antiquity-age-current",
                conditions=[AgeInUse(age="AGE_ANTIQUITY")],
            )
        ],
        action_groups=[
            ActionGroup(
                id="antiquity-game",
                scope="game",
                criteria="antiquity-age-current",
                actions=[UpdateDatabase(items=["data/antiquity-traditions.xml"])],
            )
        ],
    )
    mod.mod_dir = mod_dir
    return mod

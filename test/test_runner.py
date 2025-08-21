import pytest
from sqlalchemy import text
from pyciv7 import runner
from pyciv7.modinfo import (
    ActionGroup,
    AgeInUse,
    Criteria,
    Mod,
    Properties,
    UpdateDatabase,
)


@pytest.fixture
def modinfo_sample() -> Mod:
    return Mod(
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


def test_build_modinfo_sample(tmp_path, modinfo_sample):
    path = tmp_path / "fxs-new-policies"
    runner.build(modinfo_sample, path=path)
    assert (path / ".modinfo").read_text()


def test_build_modinfo_sample_with_sql_expression(tmp_path, modinfo_sample):
    path = tmp_path / "fxs-new-policies"
    query = text("SELECT * FROM Policies")
    modinfo_sample.action_groups[0].actions[0].items = [query]
    runner.build(modinfo_sample, path=path)
    assert (path / ".modinfo").read_text()
    assert len(list((path / "sql_statements").glob("*"))) == 1

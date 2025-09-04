from xml.dom import minidom

import pytest

from pyciv7.modinfo import *


def test_missing_properties_print_recommendations(capsys):
    props = Properties()
    out = capsys.readouterr().out
    # Three recommendations should appear
    assert "recommended the .modinfo Properties includes a name" in out
    assert "includes a description" in out
    assert "includes an author(s)" in out
    # Reassignment should also trigger recommendations for the specific field
    props.name = None
    out = capsys.readouterr().out
    assert "recommended the .modinfo Properties includes a name" in out
    assert "includes a description" not in out
    assert "includes an author(s)" not in out


def test_print_mod_recommendations(capsys):
    bad_id = "Ä" + "a" * (RECOMMENDED_MAX_ID_LENGTH) + "_ WITHSPACE"
    Mod(id=bad_id, version="1.0")
    out = capsys.readouterr().out
    assert "less than" in out
    assert "solely of ASCII" in out
    assert "lowercase" in out
    assert 'define a "Properties" element' in out


def test_properties_bool_serializer():
    props = Properties(
        affects_saved_games=True,
        show_in_browser=False,
        enabled_by_default=True,
    )
    xml: str = props.to_xml(encoding="unicode")  # type: ignore
    # True -> 0; False -> 1
    assert "<AffectsSavedGames>1</AffectsSavedGames>" in xml
    assert "<ShowInBrowser>0</ShowInBrowser>" in xml
    assert "<EnabledByDefault>1</EnabledByDefault>" in xml


def test_configuration_value_contains_serializes_list_to_commas():
    conf = ConfigurationValueContains(
        group="G", configuration_id="K", value=["a", "b", "c"]
    )
    xml: str = conf.to_xml(encoding="unicode")  # type: ignore
    assert "<Value>a,b,c</Value>" in xml


def test_sample_modinfo_to_xml_matches(fxs_new_policies_sample):
    def to_xml_lines(xml_str: str) -> List[str]:
        return [
            line.strip().replace("\\", "/")
            for line in minidom.parseString(xml_str).toprettyxml().splitlines()
            if line.strip()
        ]

    expected = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<Mod id="fxs-new-policies" version="1" xmlns="ModInfo">'
        "	<Properties>"
        "		<Name>Antiquity Policies</Name>"
        "		<Description>Adds new policies to the Antiquity Age</Description>"
        "		<Authors>Firaxis</Authors>"
        "		<AffectsSavedGames>1</AffectsSavedGames>"
        "	</Properties>"
        "	<ActionCriteria>"
        '		<Criteria id="antiquity-age-current">'
        "			<AgeInUse>AGE_ANTIQUITY</AgeInUse>"
        "		</Criteria>"
        "	</ActionCriteria>"
        "	<ActionGroups>"
        '		<ActionGroup id="antiquity-game" scope="game" criteria="antiquity-age-current">'
        "			<Actions>"
        "				<UpdateDatabase>"
        "					<Item>data/antiquity-traditions.xml</Item>"
        "				</UpdateDatabase>"
        "			</Actions>"
        "		</ActionGroup>"
        "	</ActionGroups>"
        "</Mod>"
    )
    expected = to_xml_lines(expected)
    actual = to_xml_lines(fxs_new_policies_sample.to_xml(encoding="unicode", exclude_none=True))  # type: ignore
    assert actual == expected

from abc import ABC
from typing import Final, List, Literal, Optional, TypeVar, Union

from rich import print
from pydantic import BaseModel, Field, field_serializer, field_validator

RECOMMENDED_MAX_ID_LENGTH: Final[int] = 64


def to_camel(s: str) -> str:
    return "".join(part.capitalize() for part in s.split("_"))


class Mod(BaseModel):
    model_config = {"validate_assignment": True}
    id: str
    """
    The `id` is an identifier used to distinguish mods. It must be unique to distinguish it from
    other mods.

    It's recommended that the id be composed solely of ASCII characters and be less than 64
    characters. It's also recommended to use solely lower case letters, and to use dashes
    instead of underscores or spaces.

    It's also good practice to adopt a developer prefix (an informal identifier for yourself, 
    something like `fxs`, `suk`, `lime`) for all your mods. So instead of giving your mod the
    id `my-cool-mod`, you'd give it the id `fxs-my-cool-mod` to ensure your mod id is completely
    unique.
    """
    version: str
    """
    The version number for the mod.
    """
    xmlns: Literal["ModInfo"] = "ModInfo"
    """
    The XML namespace. This should always be set to `ModInfo`.
    """

    @field_validator("id")
    def check_id_recommendations(cls, value: str) -> str:
        if len(value) >= RECOMMENDED_MAX_ID_LENGTH:
            print(
                "[yellow]It is recommended that the .modinfo ID is less than "
                f"{RECOMMENDED_MAX_ID_LENGTH} characters"
            )
        if not value.isascii():
            print(
                "[yellow]It is recommended that the .modinfo ID is composed solely of ASCII "
                "characters"
            )
        if not value.islower() or "_" in value or value.split():
            print(
                "[yellow]It is recommended that the .modinfo ID is composed solely of lowercase "
                "characters, and dashes instead of underscores or spaces"
            )
        return value


class Properties(BaseModel):
    name: Optional[str] = None
    """
    The name of the mod. If this element is left empty, the mod will not show up in the Add-Ons
    screen, though the game can still load it.
    """
    description: Optional[str] = None
    """
    A brief description of what the mod does. It will be displayed in the Add-Ons screen.
    """
    authors: Optional[str] = None
    """
    The name of the author(s).
    """
    affects_saved_games: Optional[bool] = None
    """
    Determines whether the mod affects existing saved games. Mods that affect the Gameplay
    database should have this set to `False`. `True` is usually for mods that *ONLY* affect
    the game's UI and/or Localization database.
    """
    package: Optional[str] = None
    """
    This field is not currently used by the game's UI. It would allow for mods with the same
    package value to be grouped together.
    """
    package_sort_index: Optional[int] = None
    """
    This field is not currently used by the game's UI. It would determines the order in which mods
    are shown in the browser.
    """
    show_in_browser: Optional[bool] = None
    """
    Determines whether the mod should be shown on the Add-Ons screen. If this element is excluded,
    it defaults to `False`.
    """
    enabled_by_default: Optional[bool] = None
    """
    Determines if the mod is enabled by default if it has not been enabled/disabled in the game
    previously. If this element is excluded, it defaults to `False`.
    """

    @field_validator("name")
    def check_minimum_name_recommendation(cls, value: str) -> str:
        if not value:
            print("[yellow]It is recommended the .modinfo Properties includes a name.")
        return value

    @field_validator("description")
    def check_minimum_description_recommendation(cls, value: str) -> str:
        if not value:
            print(
                "[yellow]It is recommended the .modinfo Properties includes a description."
            )
        return value

    @field_validator("authors")
    def check_minimum_authors_recommendation(cls, value: str) -> str:
        if not value:
            print(
                "[yellow]It is recommended the .modinfo Properties includes an author(s)."
            )
        return value

    @field_serializer("affects_saved_games", "show_in_browser", "enabled_by_default")
    def serialize_bool_to_success(self, value: bool) -> int:
        return int(not value)


class ChildMod(BaseModel):
    """
    `Mod` element of a `Dependencies` or `References` element.
    """

    model_config = {"title": "Mod"}

    id: str
    """
    The id of the mod that this mod will reference. This should match the mod id in the `Mod` root
    element of that mod's `.modinfo` file
    """
    title: str
    """
    The name of the mod that this mod will reference on. This should match the `Name` in the
    `Properties` element of that mod's `.modinfo` file
    """


class AlwaysMet(BaseModel):
    """
    As the name states, this criterion is always met. `ActionGroups` that you always want active,
    should be assigned a `Criteria` with this criterion.
    """


class NeverMet(BaseModel):
    """
    As the name states, this criterion is never met.
    """


Age = Union[Literal["AGE_ANTIQUITY", "AGE_EXPLORATION", "AGE_MODERN"], str]


class AgeInUse(BaseModel):
    """
    This criterion is met when the game age matches the provided age. This should be one of
    `AGE_ANTIQUITY`, `AGE_EXPLORATION`, `AGE_MODERN`. Mods may add new Ages that can be used
    here as well.
    """

    age: Age


class AgeWasUsed(BaseModel):
    """
    This criterion checks whether the provided age was previously played. It does not account for
    the current age. So if the provided value is `AGE_EXPLORATION` and you are currently playing in
    the Exploration Age, the criterion will not be met.

    Additionally, Advanced Starts do not count towards this criterion. An Exploration Era Advanced
    Start will **NOT** trigger an `AgeWasUsed` condition set to `AGE_ANTIQUITY`.
    """

    age: Age


class AgeEverInUse(BaseModel):
    """
    A combination of `AgeInUse` and `AgeWasUsed`. Checks whether the provided Age matches either
    the current Age, or a previously played Age.
    """

    age: Age


class ConfigurationValueMatches(BaseModel):
    """
    Checks if a game configuration parameter matches the provided values.
    """

    group: str
    """
    The `ConfigurationGroup` of the desired parameter.
    """
    configuration_id: str
    """
    The `ConfigurationKey` of the desired parameter.
    """
    value: str
    """
    The value you want to check for.
    """


class ConfigurationValueContains(BaseModel):
    """
    Almost identical to `ConfigurationValueMatches`, but it instead takes a list for the `Value`
    field. The criterion is met if the parameter matches any of the provided values
    """

    group: str
    """
    The `ConfigurationGroup` of the desired parameter.
    """
    configuration_id: str
    """
    The `ConfigurationKey` of the desired parameter.
    """
    value: List[str]
    """
    Any of the values you want to check for.
    """


class MapInUse(BaseModel):
    """
    Checks whether the current map type matches the provided value. The value provided should
    match the `File` column of the `Maps` table in the frontend database.
    """

    path: str


class RuleSetInUse(BaseModel):
    """
    Checks if the given ruleset is in use. By default the only ruleset available is
    `RULESET_STANDARD`, but more may be added by mods or DLC. You can reference the
    `Rulesets` table in the frontend/shell database for valid rulesets.
    """

    ruleset: Union[Literal["RULESET_STANDARD"], str]


class GameModeInUse(BaseModel):
    """
    Checks whether the game mode matches the provided value.
    """

    game_mode: Literal["WorldBuilder", "SinglePlayer", "HotSeat", "MultiPlayer"]


class LeaderPlayable(BaseModel):
    """
    Checks whether provided leader is a valid configuration option (can you set up a game with
    this leader as a player?)
    """

    leader: str


class CivilizationPlayable(BaseModel):
    """
    Checks whether provided civilization is a valid configuration option (can you set up a game
    with this civilization as a player?).

    This is affected by Game Age, `CIVILIZATION_HAN` would not be a valid option in an
    Exploration Age game.
    """

    civilization: str


class ModInUse(BaseModel):
    """
    This criterion is met when a mod with an id matching the provided value is active. The
    meaning of 'mod' here is broad. This can be user created mods, or official Firaxis DLC
    such as `shawnee-tecumseh`.

    It can optionally also take a `Version` property. In which case it will check to see if the
    mod version **MATCHES EXACTLY** before being met. It must be exact (Version 1 will not match
    version 1.0)
    """

    value: str
    version: Optional[str] = None


Condition = Union[
    AlwaysMet,
    NeverMet,
    AgeInUse,
    AgeWasUsed,
    AgeEverInUse,
    ConfigurationValueMatches,
    ConfigurationValueContains,
    MapInUse,
    RuleSetInUse,
    GameModeInUse,
    LeaderPlayable,
    CivilizationPlayable,
    ModInUse,
]


class Criteria(BaseModel):
    id: str
    """
    Each criteria must have an `id` property. The id must be unique on a per mod basis.
    """
    any: Optional[Literal[True]] = None
    """
    By default, all conditions in a `Criteria` element must be met for an `Action` with that
    criteria to activate. But if `any`=`True` is added, it will instead be met if any of the
    conditions are met.
    """
    conditions: List[Condition] = Field(min_length=1)


class ModInfo(BaseModel):
    model_config = {"alias_generator": to_camel}
    """
    A `.modinfo` tells the game what files to load and what to do with them. It tells the game
    how a mod relates to other mods and to DLC. It stores all the basic info about the mod
    (such as the name, author, and so on)
    """

    mod: Mod
    """
    The root element in a `.modinfo`
    """
    properties: Properties = Properties()
    """
    The Properties element contains much of the additional information about the mod. It
    consists of the following child elements. All these elements are technically optional,
    but at minimum, you should include `Name`, `Description`, and `Author`.
    """
    dependencies: List[ChildMod] = []
    """
    The `Dependencies` element consists of a list of `ModChild` elements. Additionally, those
    mods will be loaded before this mod.

    A mod can have as many or as few dependencies as it needs. Additionally, all mods have the
    following modules as dependencies by default:
    - `core`
    - `base-standard`
    - `age-antiquity`
    - `age-exploration`
    - `age-modern`
    """
    references: List[ChildMod] = []
    """
    The References element consists of a list of `ModChild` elements. Additionally, those
    mods will be loaded before this mod.
    """
    action_criteria: List[Criteria] = []
    """
    The `ActionCriteria` element consists of `Criteria` child elements.

    `Criteria` are a set of conditions that need to be met for a mod to execute an `ActionGroup`.
    """

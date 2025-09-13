"""
Module containing Pydantic XML models for building a `.modinfo` XML file.
"""

from collections.abc import Mapping
from pathlib import Path
import shutil
from typing import Any, Final, List, Literal, Optional, Union
from uuid import uuid4
from warnings import deprecated

from pydantic import (
    Field,
    SerializeAsAny,
    field_serializer,
    field_validator,
)
from pydantic_core import PydanticCustomError
from pydantic_xml import BaseXmlModel, attr, element, wrapped
from rich import print
from sqlalchemy.sql.elements import CompilerElement

from pyciv7.errors import (
    ModDirSerializationError,
    RelativePathRequired,
    SQLCompatibilityError,
)
from pyciv7.settings import Settings
from pyciv7.utils import StrPath

RECOMMENDED_MAX_ID_LENGTH: Final[int] = 64
"""
Recommended maximum length for a `.modinfo` ID as specified in the *Getting Started* guide.
"""


class ModinfoModel(BaseXmlModel):

    def check_modinfo_compatibility(self) -> None:
        """
        Checks if the model is compatible with Civilization 7's `.modinfo` files.

        Raises:
            ModinfoCompatibilityError: If the model is not compatible.
        """


class Properties(ModinfoModel, tag="Properties"):
    model_config = {
        "validate_assignment": True,
        "validate_default": True,
    }
    name: Optional[str] = element(default=None, tag="Name")
    """
    The name of the mod. If this element is left empty, the mod will not show up in the Add-Ons
    screen, though the game can still load it.
    """
    description: Optional[str] = element(default=None, tag="Description")
    """
    A brief description of what the mod does. It will be displayed in the Add-Ons screen.
    """
    authors: Optional[str] = element(default=None, tag="Authors")
    """
    The name of the author(s).
    """
    affects_saved_games: Optional[bool] = element(default=None, tag="AffectsSavedGames")
    """
    Determines whether the mod affects existing saved games. Mods that affect the Gameplay
    database should have this set to `False`. `True` is usually for mods that *ONLY* affect
    the game's UI and/or Localization database.
    """
    package: Optional[str] = element(default=None, tag="Package")
    """
    This field is not currently used by the game's UI. It would allow for mods with the same
    package value to be grouped together.
    """
    package_sort_index: Optional[int] = element(default=None, tag="PackageSortIndex")
    """
    This field is not currently used by the game's UI. It would determines the order in which mods
    are shown in the browser.
    """
    show_in_browser: Optional[bool] = element(default=None, tag="ShowInBrowser")
    """
    Determines whether the mod should be shown on the Add-Ons screen. If this element is excluded,
    it defaults to `False`.
    """
    enabled_by_default: Optional[bool] = element(default=None, tag="EnabledByDefault")
    """
    Determines if the mod is enabled by default if it has not been enabled/disabled in the game
    previously. If this element is excluded, it defaults to `False`.
    """

    @field_validator("name")
    def check_minimum_name_recommendation(cls, value: Optional[str]) -> Optional[str]:
        if not value:
            print("[yellow]It is recommended the .modinfo Properties includes a name.")
        return value

    @field_validator("description")
    def check_minimum_description_recommendation(
        cls, value: Optional[str]
    ) -> Optional[str]:
        if not value:
            print(
                "[yellow]It is recommended the .modinfo Properties includes a description."
            )
        return value

    @field_validator("authors")
    def check_minimum_authors_recommendation(
        cls, value: Optional[str]
    ) -> Optional[str]:
        if not value:
            print(
                "[yellow]It is recommended the .modinfo Properties includes an author(s)."
            )
        return value

    @field_serializer("affects_saved_games", "show_in_browser", "enabled_by_default")
    def serialize_bool_to_int(self, value: Optional[bool]) -> Optional[int]:
        if value is not None:
            return int(value)


class ChildMod(ModinfoModel, tag="Mod"):
    """
    `Mod` element of a `Dependencies` or `References` element.
    """

    id: str = attr()
    """
    The id of the mod that this mod will reference. This should match the mod id in the `Mod` root
    element of that mod's `.modinfo` file
    """
    title: str = attr()
    """
    The name of the mod that this mod will reference on. This should match the `Name` in the
    `Properties` element of that mod's `.modinfo` file
    """


class AlwaysMet(ModinfoModel, tag="AlwaysMet"):
    """
    As the name states, this criterion is always met. `ActionGroups` that you always want active,
    should be assigned a `Criteria` with this criterion.
    """


class NeverMet(ModinfoModel, tag="NeverMet"):
    """
    As the name states, this criterion is never met.
    """


Age = Union[Literal["AGE_ANTIQUITY", "AGE_EXPLORATION", "AGE_MODERN"], str]


class AgeInUse(ModinfoModel, tag="AgeInUse"):
    """
    This criterion is met when the game age matches the provided age. This should be one of
    `AGE_ANTIQUITY`, `AGE_EXPLORATION`, `AGE_MODERN`. Mods may add new Ages that can be used
    here as well.
    """

    age: Age


class AgeWasUsed(ModinfoModel, tag="AgeWasUsed"):
    """
    This criterion checks whether the provided age was previously played. It does not account for
    the current age. So if the provided value is `AGE_EXPLORATION` and you are currently playing in
    the Exploration Age, the criterion will not be met.

    Additionally, Advanced Starts do not count towards this criterion. An Exploration Era Advanced
    Start will **NOT** trigger an `AgeWasUsed` condition set to `AGE_ANTIQUITY`.
    """

    age: Age


class AgeEverInUse(ModinfoModel, tag="AgeEverInUse"):
    """
    A combination of `AgeInUse` and `AgeWasUsed`. Checks whether the provided Age matches either
    the current Age, or a previously played Age.
    """

    age: Age


class ConfigurationValueMatches(ModinfoModel, tag="ConfigurationValueMatches"):
    """
    Checks if a game configuration parameter matches the provided values.
    """

    group: str = element(tag="Group")
    """
    The `ConfigurationGroup` of the desired parameter.
    """
    configuration_id: str = element(tag="ConfigurationID")
    """
    The `ConfigurationKey` of the desired parameter.
    """
    value: str = element(tag="Value")
    """
    The value you want to check for.
    """


class ConfigurationValueContains(ModinfoModel, tag="ConfigurationValueContains"):
    """
    Almost identical to `ConfigurationValueMatches`, but it instead takes a list for the `Value`
    field. The criterion is met if the parameter matches any of the provided values
    """

    group: str = element(tag="Group")
    """
    The `ConfigurationGroup` of the desired parameter.
    """
    configuration_id: str = element(tag="ConfigurationID")
    """
    The `ConfigurationKey` of the desired parameter.
    """
    value: List[str] = element(tag="Value", tokens=True)
    """
    Any of the values you want to check for.
    """

    @field_serializer("value")
    def to_comma_delimited(self, value: List[str]) -> List[str]:
        return [",".join(value)]


class MapInUse(ModinfoModel, tag="MapInUse"):
    """
    Checks whether the current map type matches the provided value. The value provided should
    match the `File` column of the `Maps` table in the frontend database.
    """

    path: str


class RuleSetInUse(ModinfoModel, tag="RuleSetInUse"):
    """
    Checks if the given ruleset is in use. By default the only ruleset available is
    `RULESET_STANDARD`, but more may be added by mods or DLC. You can reference the
    `Rulesets` table in the frontend/shell database for valid rulesets.
    """

    ruleset: Union[Literal["RULESET_STANDARD"], str]


class GameModeInUse(ModinfoModel, tag="GameModeInUse"):
    """
    Checks whether the game mode matches the provided value.
    """

    game_mode: Literal["WorldBuilder", "SinglePlayer", "HotSeat", "MultiPlayer"]


class LeaderPlayable(ModinfoModel, tag="LeaderPlayable"):
    """
    Checks whether provided leader is a valid configuration option (can you set up a game with
    this leader as a player?)
    """

    leader: str


class CivilizationPlayable(ModinfoModel, tag="CivilizationPlayable"):
    """
    Checks whether provided civilization is a valid configuration option (can you set up a game
    with this civilization as a player?).

    This is affected by Game Age, `CIVILIZATION_HAN` would not be a valid option in an
    Exploration Age game.
    """

    civilization: str


class ModInUse(ModinfoModel, tag="ModInUse"):
    """
    This criterion is met when a mod with an id matching the provided value is active. The
    meaning of 'mod' here is broad. This can be user created mods, or official Firaxis DLC
    such as `shawnee-tecumseh`.

    It can optionally also take a `Version` property. In which case it will check to see if the
    mod version **MATCHES EXACTLY** before being met. It must be exact (Version 1 will not match
    version 1.0)
    """

    value: str = element(tag="Value")
    version: Optional[str] = element(tag="Version", default=None)


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
"""
A condition that can be used in a `Criteria`.
"""


class Criteria(ModinfoModel, tag="Criteria"):
    id: str = attr()
    """
    Each criteria must have an `id` property. The id must be unique on a per mod basis.
    """
    any: Optional[Literal[True]] = attr(default=None)
    """
    By default, all conditions in a `Criteria` element must be met for an `Action` with that
    criteria to activate. But if `any`=`True` is added, it will instead be met if any of the
    conditions are met.
    """
    conditions: List[Condition]


SQLStatement = CompilerElement
"""
A SQLModel ORM statement or SQLAlchemy `text` that can be compiled to a SQL string.
"""
SQLStatementOrPath = Union[StrPath, SQLStatement]
"""
Either a `SQLStatement`, or a path to a `.sql` file.
"""


def validate_item_ext(path: StrPath, *exts: str) -> Path:
    """
    Validates that the provided path has one of the provided extensions.

    Parameters:
        path: The file to validate.
        exts: The allowed extensions, including the leading dot. Case insensitive.
    """
    if isinstance(path, str):
        return validate_item_ext(Path(path), *exts)
    else:
        if path.suffix.lower() not in [ext.lower() for ext in exts]:
            raise PydanticCustomError(
                "invalid_extension",
                "Item must have one of: {allowed}",
                {"allowed": ", ".join(exts)},
            )
        return path


class ItemsAction(ModinfoModel):
    items: List[StrPath] = wrapped("Item")
    mod_dir: Optional[StrPath] = Field(default=None, exclude=True, deprecated=True)
    copy_to_mod_dir: bool = Field(default=True, exclude=True)

    def check_modinfo_compatibility(self) -> None:
        for item in self.items:
            path = Path(item)
            if path.is_absolute() or path != path.as_posix():
                raise RelativePathRequired("Items must be relative POSIX paths")

    def to_relative_posix(
        self, mod_dir: StrPath, common_items_dir: StrPath
    ) -> "ItemsAction":
        # TODO: serializer should not have side-effects (i.e. using shell and creating dirs/files)
        mod_dir = Path(mod_dir).resolve()
        common_items_dir = Path(common_items_dir).resolve()
        new_items = []

        for raw in self.items:
            src = Path(raw).resolve()

            # Normalize to a path relative to mod_dir
            rel = src.relative_to(common_items_dir)
            dest = mod_dir / rel

            if self.copy_to_mod_dir:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dest)
            new_items.append(rel.as_posix())
        return self.model_copy(update={"items": new_items})


class DatabaseItemsAction(ItemsAction):
    model_config = {"arbitrary_types_allowed": True}
    items: List[Union[StrPath, SQLStatement]] = wrapped("Item")

    def check_modinfo_compatibility(self) -> None:
        if any(isinstance(item, SQLStatement) for item in self.items):
            raise SQLCompatibilityError(
                "Inline SQL cannot be used directly in a .modinfo file. Use to_saved_sql() "
                "to convert SQL statements to .sql files.",
            )
        super().check_modinfo_compatibility()

    def to_saved_sql(self, mod_dir: StrPath) -> "DatabaseItemsAction":
        # TODO: serializer should not have side-effects (i.e. using shell and creating dirs/files)
        sql_dir = Path(mod_dir) / Settings().sql_sub_dir
        sql_dir.mkdir(exist_ok=True, parents=True)
        new_items = []
        for item in self.items:
            if isinstance(item, SQLStatement):
                # Compile SQL statement and write to SQL file
                sql_file = (sql_dir / str(uuid4())).with_suffix(".sql")
                sql_file.write_text(
                    str(item.compile(compile_kwargs={"literal_binds": True}))
                )
                # Reassign item to new SQL file
                item = sql_file
            new_items.append(item)
        return self.model_copy(update={"items": new_items})


class ScriptItemsAction(ItemsAction):

    @field_validator("items")
    def validate_items(cls, items: List[StrPath]) -> List[StrPath]:
        return [validate_item_ext(item, ".js") for item in items]


class UpdateDatabase(DatabaseItemsAction, tag="UpdateDatabase"):
    """
    Updates either the frontend/shell or gameplay database with the provided `.xml`,
    SQLModel ORM statement, or `.sql` items, depending on the scope of the `ActionGroup`.
    """


class UpdateText(DatabaseItemsAction, tag="UpdateText"):
    """
    Updates the Localization database with the provided `.xml`, SQLModel ORM statement, or, `.sql`
    items.
    """


class UpdateIcons(DatabaseItemsAction, tag="UpdateIcons"):
    """
    Updates the `Icons` database with the provided `.xml`, SQLModel ORM statement, or `.sql` items.
    """


class UpdateColors(DatabaseItemsAction, tag="UpdateColors"):
    """
    Updates the `Colors` database with the provided `.xml`, SQLModel ORM statement, or `.sql`
    items.
    """


class UpdateArt(ItemsAction, tag="UpdateArt"):
    """
    Updates art files. This action type won't be useful for modders until art tools are released.
    """


class ImportFiles(ItemsAction, tag="ImportFiles"):
    """
    Imports files into the game's file system. This can be used to import custom 2D assets such
    as `.png` files. It can also be used to replace files, provided the file being imported has
    the same name and path (relative to the `.modinfo` file).
    """


class UIScripts(ScriptItemsAction, tag="UIScripts"):
    """
    Loads the provided `.js` files as new UI scripts.
    """


class UIShortcuts(ItemsAction, tag="UIShortcuts"):
    """
    Loads the provided `.html` files into the game's debug menu for loading.
    `pyciv7.runner.run(..., debug=True)` must be set to access the panel. Alternatively,
    `EnableDebugPanels` can be set to `1` in `AppOptions.txt` to access the panel.
    """

    @field_validator("items")
    def validate_items(cls, items: List[StrPath]) -> List[StrPath]:
        return [validate_item_ext(item, ".html") for item in items]


class UpdateVisualRemaps(DatabaseItemsAction, tag="UpdateVisualRemaps"):
    """
    Updates the Visual Remap database with the provided `.xml`, SQLModel ORM statement, or `.sql`
    items. The Visual Remaps can be used to relink the visuals of gameplay entries onto other
    assets.
    """


class MapGenScripts(ScriptItemsAction, tag="MapGenScripts"):
    """
    Adds a new `.js` gameplay script that is loaded during map generation, then unloaded after.
    """


class ScenarioScripts(ScriptItemsAction, tag="ScenarioScripts"):
    """
    Adds a new `.js` gameplay script.
    """


Action = SerializeAsAny[
    Union[
        UpdateDatabase,
        UpdateText,
        UpdateIcons,
        UpdateColors,
        UpdateArt,
        ImportFiles,
        UIScripts,
        UIShortcuts,
        UpdateVisualRemaps,
        MapGenScripts,
        ScenarioScripts,
    ]
]
"""
An action that can be used in an `ActionGroup`.
"""


class ActionGroup(ModinfoModel, tag="ActionGroup"):
    """
    An `ActionGroup` consists of `Action` child elements, which in turn consists of an array of
    different child elements representing different types of actions. Those child elements should
    have further `Item` file elements that contain a path (relative to the `.modinfo` file) to the
    file to be loaded by the action
    """

    id: str = attr()
    """
    The id of the `ActionGroup`. This must be unique on a per mod basis.
    """
    scope: Literal["game", "shell"] = attr()
    """
    Whether the `ActionGroup` targets the frontend or gameplay scope.
    """
    criteria: str = attr()
    """
    The criteria that must be met for this `ActionGroup` to trigger. Set the value to the id of a
    `Criteria` defined in `ActionCriteria`
    """
    actions: List[Action] = wrapped("Actions")
    """
    The set of actions that will be executed when the criteria is met.
    """
    load_order: Optional[int] = wrapped("Properties/LoadOrder", default=None, ge=0)
    """
    The order in which this `ActionGroup` will be loaded, relative to other `ActionGroup`s.
    """


class Mod(ModinfoModel, tag="Mod"):
    """
    Root element for a `.modinfo` file. A `.modinfo` tells the game what files to load and what
    to do with them. It tells the game how a mod relates to other mods and to DLC. It stores all
    the basic info about the mod (such as the name, author, and so on.)
    """

    model_config = {
        "validate_assignment": True,
        "validate_default": True,
    }
    id: str = attr()
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
    version: str = attr()
    """
    The version number for the mod.
    """
    xmlns: Literal["ModInfo"] = attr(default="ModInfo")
    """
    The XML namespace. This should always be set to `ModInfo`.
    """
    properties: Optional[Properties] = element(default=None)
    """
    The Properties element contains much of the additional information about the mod. It
    consists of the following child elements. All these elements are technically optional,
    but at minimum, you should include `Name`, `Description`, and `Author`.
    """
    dependencies: Optional[List[ChildMod]] = wrapped("Dependencies", default=None)
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
    references: Optional[List[ChildMod]] = wrapped("References", default=None)
    """
    The References element consists of a list of `ModChild` elements. Additionally, those
    mods will be loaded before this mod.
    """
    action_criteria: Optional[List[Criteria]] = wrapped("ActionCriteria", default=None)
    """
    The `ActionCriteria` element consists of `Criteria` child elements.

    `Criteria` are a set of conditions that need to be met for a mod to execute an `ActionGroup`.
    """
    action_groups: Optional[List[ActionGroup]] = wrapped("ActionGroups", default=None)
    """
    The `ActionGroups` element consists of `ActionGroup` child elements.
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
        if not value.islower() or "_" in value or len(value.split(maxsplit=1)) > 1:
            print(
                "[yellow]It is recommended that the .modinfo ID is composed solely of lowercase "
                "characters, and dashes instead of underscores or spaces"
            )
        return value

    @field_validator("properties")
    def check_properties_recommendations(cls, value: Optional[str]) -> Optional[str]:
        if not value:
            print('[yellow]It is recommended you define a "Properties" element')
        return value

    @property
    @deprecated(
        '"mod_dir" is deprecated and unused. Set directly in runner.build(mod_dir=...) instead.'
    )
    def mod_dir(self) -> Optional[StrPath]:
        """
        The mod directory, if it can be inferred from one of the actions.
        """
        pass

    @mod_dir.setter
    @deprecated(
        '"mod_dir" is deprecated and unused. Set directly in runner.build(mod_dir=...) instead.'
    )
    def mod_dir(self, mod_dir: StrPath) -> None:
        pass

    def check_modinfo_compatibility(self) -> None:
        visited: set[int] = set()

        def walk(value: Any) -> None:
            nonlocal visited
            # ModinfoModel node
            if isinstance(value, ModinfoModel):
                oid = id(value)
                if oid not in visited:
                    visited.add(oid)
                    # walk all fields (includes defaults)
                    for name in value.__class__.model_fields:  # pydantic v2 API
                        child = getattr(value, name, None)
                        walk(child)
                    # collect incompatibles after descending
                    value.check_modinfo_compatibility()
            # containers
            elif isinstance(value, Mapping):
                for v in value.values():
                    walk(v)
            elif isinstance(value, (list, tuple, set, frozenset)):
                for v in value:
                    walk(v)

        walk(self)

from pathlib import Path
import subprocess
from typing import Final, List, Literal, Optional, Tuple, Union
from uuid import uuid4
from pydantic import Field, field_validator
from pydantic_core import PydanticCustomError
from pyciv7.errors import TranspileError
from pyciv7.modinfo import (
    ActionGroup,
    AlwaysMet,
    Criteria,
    ImportFiles,
    StrPath,
    transpile,
    validate_item_ext,
)
from pyciv7.settings import Settings

ShellHook = Literal[
    "modules/core/ui/shell/root-shell.js",
    "modules/core/ui/shell/additional-content/screen-additional-content.js",
    "modules/core/ui/shell/age-transition/age-transition-civ-card.js",
    "modules/core/ui/shell/age-transition/age-transition-civ-select.js",
    "modules/core/ui/shell/age-transition/civilization-info-tooltip.js",
    "modules/core/ui/shell/collection/collection-content.js",
    "modules/core/ui/shell/create-game/create-game-sp.js",
    "modules/core/ui/shell/create-panels/advanced-options-panel.js",
    "modules/core/ui/shell/create-panels/age-civ-select-model.chunk.js",
    "modules/core/ui/shell/create-panels/age-select-panel.js",
    "modules/core/ui/shell/create-panels/civ-select-bonus.js",
    "modules/core/ui/shell/create-panels/civ-select-panel.js",
    "modules/core/ui/shell/create-panels/create-game-model.js",
    "modules/core/ui/shell/create-panels/game-creation-panel-base.chunk.js",
    "modules/core/ui/shell/create-panels/game-creation-promo-manager.chunk.js",
    "modules/core/ui/shell/create-panels/game-setup-panel.js",
    "modules/core/ui/shell/create-panels/leader-select-model.chunk.js",
    "modules/core/ui/shell/create-panels/leader-select-panel.js",
    "modules/core/ui/shell/create-panels/learn-more.js",
    "modules/core/ui/shell/create-panels/memento-editor.js",
    "modules/core/ui/shell/create-panels/memento-slot.js",
    "modules/core/ui/shell/credits/screen-credits.js",
    "modules/core/ui/shell/events/screen-events.js",
    "modules/core/ui/shell/extras/screen-extras.js",
    "modules/core/ui/shell/gift-notifications/giftbox-popup.js",
    "modules/core/ui/shell/leader-select/leader-select-model-manager.chunk.js",
    "modules/core/ui/shell/live-event-logic/live-event-logic.chunk.js",
    "modules/core/ui/shell/main-menu/main-menu.js",
    "modules/core/ui/shell/mods-content/mods-content.js",
    "modules/core/ui/shell/mp-browser/mp-browser-chooser-item.js",
    "modules/core/ui/shell/mp-browser/mp-browser-new.js",
    "modules/core/ui/shell/mp-create-game/mp-create-game.js",
    "modules/core/ui/shell/mp-game-mode/mp-game-mode.js",
    "modules/core/ui/shell/mp-landing/mp-landing-new.js",
    "modules/core/ui/shell/mp-legal/mp-legal.js",
    "modules/core/ui/shell/mp-link-account/mp-link-account.js",
    "modules/core/ui/shell/mp-primary-account-select/mp-primary-account-select.js",
    "modules/core/ui/shell/mp-shell-logic/mp-shell-logic.chunk.js",
    "modules/core/ui/shell/mp-staging/model-mp-friends.chunk.js",
    "modules/core/ui/shell/mp-staging/model-mp-staging-new.chunk.js",
    "modules/core/ui/shell/mp-staging/mp-friends-options.js",
    "modules/core/ui/shell/mp-staging/mp-friends.js",
    "modules/core/ui/shell/mp-staging/mp-game-rules.js",
    "modules/core/ui/shell/mp-staging/mp-player-options.js",
    "modules/core/ui/shell/mp-staging/mp-report.js",
    "modules/core/ui/shell/mp-staging/mp-search.js",
    "modules/core/ui/shell/mp-staging/mp-staging-dropdown.js",
    "modules/core/ui/shell/mp-staging/mp-staging-leader-dropdown.js",
    "modules/core/ui/shell/mp-staging/mp-staging-new.js",
    "modules/core/ui/shell/mp-staging/mp-staging-player-info-card.js",
    "modules/core/ui/shell/mp-staging/mp-staging-playerinfocard-dropdown.js",
    "modules/core/ui/shell/mp-staging/mp-staging-team-dropdown.js",
    "modules/core/ui/shell/odr-download/odr-download.js",
    "modules/core/ui/shell/oob-experience/oob-experience-mgr.js",
    "modules/core/ui/shell/popup/popup.js",
    "modules/core/ui/shell/screen-movie/screen-movie.js",
    "modules/core/ui/shell/shell-components/icon-dropdown.js",
    "modules/core/ui/shell/store-launcher/2k-code-redemption.chunk.js",
    "modules/core/ui/shell/store-launcher/2k-code-redemption.js",
    "modules/core/ui/shell/store-launcher/screen-dlc-viewer.js",
    "modules/core/ui/shell/store-launcher/screen-store-launcher.js",
    "modules/core/ui/shell/sync-conflict/sync-conflict.js",
    "modules/core/ui/shell/leader-select/leader-button/leader-button.js",
    "modules/core/ui/shell/civ-select/civ-button/civ-button.js",
]
Hook = Union[ShellHook, StrPath]

DEFAULT_SHELL_HOOK: Final[ShellHook] = "modules/core/ui/shell/main-menu/main-menu.js"


class ImportHookedPythonScripts(ImportFiles):
    hook: Hook = Field(DEFAULT_SHELL_HOOK, exclude=True)
    expose: bool = Field(False, exclude=True)

    @field_validator("items")
    def validate_items(cls, items: List[StrPath]) -> List[StrPath]:
        return [validate_item_ext(item, ".py") for item in items]

    @field_validator("hook")
    def validate_hook(cls, hook: Hook) -> Hook:
        settings = Settings()
        if not (settings.civ7_installation_dir / "Base" / hook).exists():
            raise PydanticCustomError(
                "hook_file_does_not_exist",
                "{module} is not a valid base module script to hook the Python scripts to",
                context={"module": hook},
            )
        return hook

    def transpile(self, transcrypt_dir: StrPath) -> None:
        transpile(self.items, transcrypt_dir)

    def get_hook_condition_and_action(
        self,
        transcrypt_dir: StrPath,
    ) -> Optional[Tuple[Criteria, ActionGroup]]:
        # Create a unique criteria group to always import the hook
        criteria_id = f"{uuid4()}-pyciv7-hook-condition"
        # Create a unique action group to use the criteria group
        action_group_id = f"{uuid4()}-pyciv7-hook-action-group"
        scope = scope or "shell" if cls.hook == "shell" else "game"
        criteria = Criteria(id=criteria_id, conditions=[AlwaysMet()])
        action_group = ActionGroup(
            id=action_group_id,
            scope=scope,
            criteria=criteria_id,
            actions=[ImportFiles(items=[])],
        )
        return (criteria, action_group)

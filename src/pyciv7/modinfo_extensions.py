"""
Pydantic models and utilities that provide extended `.modinfo` functionality beyond the standard
Civilization 7 modding guide.
"""

import subprocess
from pathlib import Path
from typing import List, Literal

from pydantic import Field, field_validator
from rich.status import Status

from pyciv7.errors import (
    ModDirSerializationError,
    ModinfoCompatibilityError,
    JavaScriptCompatibilityError,
    TranspileError,
)
from pyciv7.modinfo import ModinfoModel, UIScripts, validate_item_ext
from pyciv7.settings import Settings
from pyciv7.utils import StrPath


class IncompatibleModinfoModel(ModinfoModel):
    def check_modinfo_compatibility(self) -> None:
        raise ModinfoCompatibilityError(
            f'"{self.__class__.__name__}" is not compatible with Civilization 7\'s .modinfo files.'
        )


class PythonGameScripts(IncompatibleModinfoModel, UIScripts):
    """
    Loads the provided `.py` files as new gameplay scripts.

    This model accepts a list of Python files and, at serialization time,
    transpiles them into JavaScript using Transcrypt. The resulting `.js` files
    are written to the mod's Transcrypt output directory and then returned as a
    standard `UIScripts` payload.
    """

    backend: Literal["transcrypt"] = Field(default="transcrypt", exclude=True)
    """
    The backend to use for convert Python to JavaScript.
    """

    @field_validator("items")
    def validate_items(cls, items: List[StrPath]) -> List[StrPath]:
        return [validate_item_ext(item, ".py") for item in items]

    def check_modinfo_compatibility(self) -> None:
        raise JavaScriptCompatibilityError(
            "PythonGameScripts cannot be used directly in a .modinfo file. Use to_ui_scripts() "
            "to convert the Python files to JavaScript and return a UIScripts instance.",
        )

    def to_ui_scripts(self, mod_dir: StrPath) -> UIScripts:
        if self.backend == "transcrypt":
            return self.transpile(mod_dir)
        raise NotImplementedError(f"Unsupported backend: {self.backend}")

    def transpile(self, mod_dir: StrPath) -> UIScripts:
        """
        Transpile Python sources to JavaScript using Transcrypt and return a return a serialized
        `UIScripts` instance utilizing the transpiled scripts.

        Creates the Transcrypt output directory under:
        `<mod_dir>/<Settings().transcrypt_sub_dir>/`. For each item: transpile it (unless the
        corresponding `.js` already exists), and replace the item path with the resulting `.js`.

        Returns:
            A serialized `UIScripts`.

        Raises:
            ModDirSerializationError: If `mod_dir` is not set.
            TranspileError: If the `transcrypt` CLI exits with a non-zero status.
        """
        transcrypt_dir = Path(mod_dir) / Settings().transcrypt_sub_dir
        transcrypt_dir.mkdir(exist_ok=True, parents=True)
        new_items = []
        for item in self.items:
            item = Path(item)
            transpiled_file = transcrypt_dir / item.with_suffix(".js").name
            if not transpiled_file.exists():
                # Use transcrypt to transpile Python to JavaScript
                with Status(f"Transpiling {item.name}..."):
                    try:
                        subprocess.run(
                            [
                                "transcrypt",
                                "--build",
                                item,
                                "--outdir",
                                transcrypt_dir,
                            ],
                            text=True,
                            capture_output=True,
                            check=True,
                        )
                    except subprocess.CalledProcessError as e:
                        raise TranspileError(f"Failed to transpile {item.name}: {e.stdout}") from e
                # Reassign item to new transpiled JavaScript
                item = transpiled_file
            new_items.append(item)
        return UIScripts(items=new_items, mod_dir=self.mod_dir)

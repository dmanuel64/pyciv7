import subprocess
from pathlib import Path
from typing import Any, Dict, List

from pydantic import field_validator, model_serializer
from rich.status import Status

from pyciv7.errors import ModDirSerializationError, TranspileError
from pyciv7.modinfo import UIScripts, validate_item_ext
from pyciv7.settings import Settings
from pyciv7.utils import StrPath


class PythonGameScripts(UIScripts):

    @field_validator("items")
    def validate_items(cls, items: List[StrPath]) -> List[StrPath]:
        return [validate_item_ext(item, ".py") for item in items]

    @model_serializer()
    def transpile(self) -> Dict[str, Any]:
        if not self.mod_dir:
            raise ModDirSerializationError('"mod_dir" must be set prior to serialization.')
        transcrypt_dir = Path(self.mod_dir) / Settings().transcrypt_sub_dir
        transcrypt_dir.mkdir(exist_ok=True, parents=True)
        new_items = []
        for item in self.items:
            item = Path(item)
            if item.suffix.lower() == ".py":
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
                            raise TranspileError(
                                f"Failed to transpile {item.name}"
                            ) from e
                    # Reassign item to new transpiled JavaScript
                    item = transpiled_file
            new_items.append(item)
        return UIScripts(items=new_items, mod_dir=self.mod_dir).model_dump()

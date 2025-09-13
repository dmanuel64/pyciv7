# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pyciv7",
#     "pydantic-settings",
#     "python-dotenv",
#     "rich",
#     "sqlmodel",
# ]
#
# [tool.uv.sources]
# pyciv7 = { path = "../", editable = true }
# ///

import os
from pathlib import Path
import sqlite3
import sys
from typing import Type

from dotenv import load_dotenv
from pydantic import BaseModel
from rich import print
from rich.status import Status
from rich.progress import track

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pyciv7.databases


def quote_ident(name: str) -> str:
    # Quote with double-quotes and escape embedded quotes by doubling them.
    return '"' + name.replace('"', '""') + '"'


def quote_ident_path(name: str) -> str:
    # If names can include a dot (schema.table), quote each part:
    return ".".join(quote_ident(part) for part in name.split("."))


def main() -> None:
    load_dotenv(Path(__file__).parent.parent / ".env")
    try:
        civ7_settings_dir = Path(
            os.path.expandvars(os.environ["CIV7_SETTINGS_DIR"])
        ).expanduser()
    except KeyError as e:
        raise KeyError(
            'You must specify "CIV7_SETTINGS_DIR" as an environment variable or in '
            '".env" in the repository\'s root'
        ) from e
    with Status("Looking for SQLite databases..."):
        sqlite_files = list(civ7_settings_dir.rglob("*.sqlite"))
    print(f"Found {len(sqlite_files)} SQLite databases")
    for sqlite_file in track(
        sqlite_files, description="Searching through databases...", transient=True
    ):
        # Connect to the database
        conn = sqlite3.connect(sqlite_file)
        cursor = conn.cursor()
        # Get a list of all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for (table,) in track(
            tables, description=f"Inspecting {sqlite_file.name}...", transient=True
        ):
            try:
                model: Type[BaseModel] = getattr(pyciv7.databases, table)
            except AttributeError:
                print(
                    f'[yellow]Table not implemented for {sqlite_file.name}: "{table}"'
                )
            else:
                # Get binding fields
                fields = set(model.model_fields)
                # Get all columns for the table
                safe = quote_ident_path(table)
                cursor.execute(f"PRAGMA table_info({safe});")
                columns = set(cursor.fetchall())
                # Check for missing/extra columns
                for missing_column in columns.difference(fields):
                    print(
                        f"[yellow]Table {table} is implemented, but is missing column "
                        f'"{missing_column}" in the bindings'
                    )
                for extra_column in fields.difference(columns):
                    print(
                        f"[red]Column does not exist in the {table} table, but is present in the "
                        f'bindings: "{extra_column}"'
                    )


if __name__ == "__main__":
    main()

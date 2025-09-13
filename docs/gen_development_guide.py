"""
Generate the code documentation pages and navigation.
"""

from typing import Final
import mkdocs_gen_files

from pathlib import Path

CONTRIBUTING_PATH: Final[Path] = Path(__file__).parent.parent / "CONTRIBUTING.md"

# Create Development Guide
with mkdocs_gen_files.open("contributing/development-guide.md", "w") as nav_file:
    lines = [*CONTRIBUTING_PATH.read_text().splitlines()]
    nav_file.write("\n".join(lines))

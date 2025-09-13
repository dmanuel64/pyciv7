"""
Utility types for `pyciv7`.

This module defines common type aliases and helpers used throughout the codebase.
"""

from pathlib import Path
from typing import Union


StrPath = Union[str, Path]
"""
Type alias for filesystem paths.

Represents either a `str` or a `pathlib.Path` instance.
"""

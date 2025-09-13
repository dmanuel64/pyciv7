from typing import Any

from pyciv7.errors import TranscryptEnvironmentError

Window = Any


def get_window() -> Window:
    """
    Get the global `window` object in a Transcrypt environment.

    Returns:
        The global `window` object if available
    """
    try:
        from org.transcrypt.stubs.browser import (  # pyright: ignore[reportMissingImports]
            window,
        )

        return window
    except ImportError:
        raise TranscryptEnvironmentError(
            "This function can only be used in a Transcrypt environment."
        )

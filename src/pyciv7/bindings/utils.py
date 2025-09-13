from typing import Any, Callable, Final, final

from pyciv7.bindings.common import get_window


def exec_js(js_code: str) -> Any:
    """Execute raw JavaScript code in the game environment."""
    return get_window().eval(js_code)

@final
class Console:
    """A simple console wrapper to log messages to the browser console."""
    
    @staticmethod
    def log(*args: Any) -> None:
        get_window().console.log(*args)

    @staticmethod
    def warn(*args: Any) -> None:
        get_window().console.warn(*args)

    @staticmethod
    def error(*args: Any) -> None:
        get_window().console.error(*args)

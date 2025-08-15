from contextlib import contextmanager, nullcontext
from typing import ContextManager, Generator

from pyciv7.settings import Settings

@contextmanager
def debug_settings_enabled() -> Generator[None, None, None]:
    yield

def run(debug: bool = True):
    settings = Settings()
    ctx = debug_settings_enabled() if debug else nullcontext()
    with ctx:
        pass
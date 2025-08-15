from pyciv7.settings import Settings
from pyciv7.modinfo import *


def hello() -> str:
    return "Hello from pyciv7!"


if __name__ == "__main__":
    print(ModInfo(mod=Mod(id="my-mod", version="1.0.0")))

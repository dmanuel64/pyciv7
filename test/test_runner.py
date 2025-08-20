import pytest

from pyciv7 import runner
from pyciv7.modinfo import (
    ActionGroup,
    AlwaysMet,
    Criteria,
    DatabaseItem,
    Mod,
    Properties,
    ScriptItem,
    UpdateDatabase,
    MapGenScripts,
)


def test_build_python_scripts(tmp_path):
    py_script = tmp_path / "test.py"
    py_script.write_text('print("Hello, world")')
    mod = Mod(
        id="python-integrated-mod",
        version="1",
        action_criteria=[
            Criteria(
                id="always",
                conditions=[AlwaysMet()],
            )
        ],
        action_groups=[
            ActionGroup(
                id="hello-world",
                scope="game",
                criteria="always",
                actions=[MapGenScripts(items=[ScriptItem(path=py_script)])],
            )
        ],
    )
    runner.build(mod, tmp_path)

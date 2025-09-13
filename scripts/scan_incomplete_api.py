# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pyciv7",
# ]
#
# [tool.uv.sources]
# pyciv7 = { path = "../", editable = true }
# ///

from pyciv7 import Mod, run
from pyciv7.modinfo import ActionGroup, AlwaysMet, Criteria, Properties
from pyciv7.modinfo_extensions import PythonGameScripts

mod = Mod(
    id="ytm-pyciv7-api-scanner",
    version="1",
    properties=Properties(
        name="pyciv7 API Scanner",
        description="Scans for incomplete API bindings for pyciv7.",
        authors="youngtacomanny",
        affects_saved_games=False,
    ),
    action_criteria=[Criteria(id="always", conditions=[AlwaysMet()])],
    action_groups=[
        ActionGroup(
            id="antiquity-game",
            scope="game",
            criteria="always",
            actions=[PythonGameScripts(items=["dir_globals.py"])],
        )
    ],
)

run(mod)

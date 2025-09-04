import pytest
from sqlalchemy import text
from pyciv7 import runner
from pyciv7.modinfo_extensions import PythonGameScripts
from pyciv7.settings import Settings


def test_build_fxs_new_policies_sample(fxs_new_policies_sample):
    runner.build(fxs_new_policies_sample)
    assert (fxs_new_policies_sample.mod_dir / ".modinfo").read_text()


def test_build_fxs_new_policies_sample_with_sql_expression(fxs_new_policies_sample):
    query = text("SELECT * FROM Policies")
    fxs_new_policies_sample.action_groups[0].actions[0].items = [query]
    runner.build(fxs_new_policies_sample)
    assert (fxs_new_policies_sample.mod_dir / ".modinfo").read_text()
    assert len(list((fxs_new_policies_sample.mod_dir / "sql").glob("*"))) == 1


# TODO: need to mock transcrypt subprocess.run
@pytest.mark.skip(reason="Transcrypt needs to be mocked for pipeline")
def test_build_fxs_new_policies_sample_with_python_script(fxs_new_policies_sample):
    python_script = fxs_new_policies_sample.mod_dir / "test.py"
    python_script.write_text("print('Hello, world')")
    fxs_new_policies_sample.action_groups[0].actions[0] = PythonGameScripts(
        items=["test.py"]
    )
    runner.build(fxs_new_policies_sample)
    assert (fxs_new_policies_sample.mod_dir / ".modinfo").read_text()
    assert (
        fxs_new_policies_sample.mod_dir / Settings().transcrypt_sub_dir / "test.js"
    ).exists()

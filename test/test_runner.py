from sqlalchemy import text
from pyciv7 import runner
from pyciv7.settings import Settings


def test_build_fxs_new_policies_sample(fxs_new_policies_sample):
    runner.build(fxs_new_policies_sample)
    assert (fxs_new_policies_sample.mod_dir / ".modinfo").read_text()


def test_build_fxs_new_policies_sample_with_sql_expression(
    tmp_path, fxs_new_policies_sample
):
    path = tmp_path / "fxs-new-policies"
    query = text("SELECT * FROM Policies")
    fxs_new_policies_sample.action_groups[0].actions[0].items = [query]
    runner.build(fxs_new_policies_sample, path=path)
    assert (path / ".modinfo").read_text()
    assert len(list((path / "sql").glob("*"))) == 1

# TODO: need to mock transcrypt subprocess.run
def test_build_fxs_new_policies_sample_with_python_script(
    tmp_path, fxs_new_policies_sample
):
    orig_num_action_criteria = len(fxs_new_policies_sample.action_criteria)
    orig_num_action_groups = len(fxs_new_policies_sample.action_groups)
    path = tmp_path / "fxs-new-policies"
    python_script = tmp_path / "test.py"
    python_script.write_text("print('Hello, world')")
    hooked_script = HookedScripts(items=[python_script], hook=DEFAULT_SHELL_HOOK)
    new_mod = runner.build(fxs_new_policies_sample, path=path, hooked_scripts=[hooked_script])
    assert (path / ".modinfo").read_text()
    assert (
        len(new_mod.action_criteria or []) == orig_num_action_criteria + 1
    ), "There should be only one more ActionCriteria for the hook"
    assert (
        len(new_mod.action_groups or []) == orig_num_action_groups + 1
    ), "There should be only one more ActionGroup for the hook"
    assert (tmp_path / Settings().transcrypt_sub_dir / "test.js").exists()

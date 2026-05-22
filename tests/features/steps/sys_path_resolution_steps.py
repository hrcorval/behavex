import logging
import os
import shutil
import subprocess
import tempfile

from behave import given, then, when

root_project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

_PARENT_BEHAVEX_ENV_VARS = frozenset({
    'CONFIG', 'OUTPUT', 'TAGS', 'PARALLEL_SCHEME',
    'PARALLEL_PROCESSES', 'FEATURES_PATH', 'TEMP', 'LOGS', 'LOGGING_LEVEL',
})

_LOCAL_PKG_INIT = '''\
SHARED_VALUE = "local_pkg_loaded"
'''

_ENVIRONMENT_PY = '''\
from local_pkg import SHARED_VALUE  # top-level import: exercises coordinator sys.path


def before_all_workers(context):
    context.pkg_val = SHARED_VALUE


def before_scenario(context, scenario):
    # Runs inside each worker process — exercises worker sys.path fix.
    from local_pkg import SHARED_VALUE as v  # noqa: PLC0415
    assert v == "local_pkg_loaded", f"local_pkg not importable in worker: got {v!r}"
'''

# Plain Behave environment — no before_all_workers / after_all_workers.
# This is the exact reporter's scenario in Issue #247: the module is loaded by
# _call_bhx_hook to check for BehaveX hooks; the top-level import must not fail.
_ENVIRONMENT_PY_PLAIN = '''\
from local_pkg import SHARED_VALUE  # top-level import from local package


def before_all(context):
    pass


def before_scenario(context, scenario):
    from local_pkg import SHARED_VALUE as v  # noqa: PLC0415
    assert v == "local_pkg_loaded", f"local_pkg not importable: got {v!r}"
'''

_TEST_FEATURE = '''\
Feature: Local package import test

  @SYS_PATH_TEST
  Scenario: Local package is importable during execution
    Given a passing step from local pkg test
'''

_STEPS_PY = '''\
from behave import given


@given("a passing step from local pkg test")
def step_impl(context):
    pass
'''


def _clean_child_env():
    return {k: v for k, v in os.environ.items() if k not in _PARENT_BEHAVEX_ENV_VARS}


def _make_project_dir(context):
    if not hasattr(context, 'project_dir'):
        if os.path.isdir('/tmp'):
            base_tmp = '/tmp'
        else:
            drive, _ = os.path.splitdrive(root_project_path)
            base_tmp = drive + os.sep + 'bhx_sp_tmp'
            os.makedirs(base_tmp, exist_ok=True)
        project_dir = tempfile.mkdtemp(prefix='bhx_syspath_', dir=base_tmp)
        context.add_cleanup(shutil.rmtree, project_dir, ignore_errors=True)
        context.project_dir = project_dir
    return context.project_dir


def _create_project(context, env_content: str) -> None:
    project_dir = _make_project_dir(context)

    pkg_dir = os.path.join(project_dir, 'local_pkg')
    os.makedirs(pkg_dir, exist_ok=True)
    with open(os.path.join(pkg_dir, '__init__.py'), 'w') as f:
        f.write(_LOCAL_PKG_INIT)

    features_dir = os.path.join(project_dir, 'features')
    steps_dir = os.path.join(features_dir, 'steps')
    os.makedirs(steps_dir, exist_ok=True)

    with open(os.path.join(features_dir, 'environment.py'), 'w') as f:
        f.write(env_content)

    with open(os.path.join(features_dir, 'local_import.feature'), 'w') as f:
        f.write(_TEST_FEATURE)

    open(os.path.join(steps_dir, '__init__.py'), 'w').close()
    with open(os.path.join(steps_dir, 'steps.py'), 'w') as f:
        f.write(_STEPS_PY)


@given('a project directory with a local package and a plain environment.py that imports from it')
def given_project_with_plain_environment(context):
    _create_project(context, _ENVIRONMENT_PY_PLAIN)


@given('a project directory with a local package and an environment.py that imports from it')
def given_project_with_local_package(context):
    _create_project(context, _ENVIRONMENT_PY)


@when('I run behavex from that project directory with "{n}" parallel process')
@when('I run behavex from that project directory with "{n}" parallel processes')
def when_run_from_project_dir(context, n):
    project_dir = context.project_dir
    output_dir = os.path.join(project_dir, 'output')
    feature_path = os.path.join(project_dir, 'features', 'local_import.feature')
    cmd = [
        'behavex', feature_path,
        '-o', output_dir,
        '--parallel-processes', n,
        '--parallel-scheme', 'scenario',
    ]
    child_env = _clean_child_env()
    context.sys_path_result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=project_dir, env=child_env
    )
    logging.info(
        f"sys_path test (n={n}) rc={context.sys_path_result.returncode}\n"
        f"STDOUT:\n{context.sys_path_result.stdout}\n"
        f"STDERR:\n{context.sys_path_result.stderr}"
    )


@then('behavex should exit with code 0 and no ImportError')
def then_exit_0_no_import_error(context):
    result = context.sys_path_result
    combined = result.stdout + result.stderr
    assert 'ImportError' not in combined and 'ModuleNotFoundError' not in combined, (
        f"Import error detected in output:\n{combined}"
    )
    assert result.returncode == 0, (
        f"Expected exit code 0, got {result.returncode}\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )

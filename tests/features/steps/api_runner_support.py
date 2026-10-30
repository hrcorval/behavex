import json
import os
import subprocess
import sys
from typing import List, Optional

import behave
from config_file_steps import _clean_child_env
from execution_steps import (
    fixtures_path,
    get_unique_suffix,
    root_project_path,
    secondary_features_path,
)
from packaging.version import Version

# behave 1.2.6 reports hook errors and undefined background steps as failed
BEHAVE_ERROR_STATUS = 'error' if Version(behave.__version__) >= Version('1.2.7') else 'failed'

api_runner_features_path = os.path.join(fixtures_path, 'api_runner_features')
undefined_steps_features_path = os.path.join(api_runner_features_path, 'undefined_steps')
nested_steps_folders_path = os.path.join(api_runner_features_path, 'nested_steps_folders')
serial_suites_path = os.path.join(api_runner_features_path, 'serial_suites')


_SERIALIZE_RESULT = """
_s = result.summary
_data = {
    "run_id": result.run_id,
    "exit_code": result.exit_code,
    "passed": result.passed,
    "stopped": result.stopped,
    "output_folder": result.output_folder,
    "feature_count": len(result.features),
    "features": [
        {"name": f.name, "status": f.status, "scenario_count": len(f.scenarios)}
        for f in result.features
    ],
    "summary": _s.model_dump(),
    "failed_scenario_count": len(result.failed_scenarios),
    "failed_scenarios": [
        {
            "name": s.name,
            "status": s.status,
            "error_msg": s.error_msg,
            "has_error_step": s.error_step is not None,
        }
        for s in result.failed_scenarios
    ],
    "tagged_scenario_count": sum(1 for f in result.features for s in f.scenarios if s.tags),
}
print("__RESULT__:" + json.dumps(_data))
"""


_CAPTURE_RAISED = """
def _capture_raised(call):
    try:
        call()
    except BaseException as error:
        return {"type": type(error).__name__, "message": str(error)}
"""


def _run_script(script: str, import_runner: bool = True, timeout: int = 120,
                **run_kwargs) -> subprocess.CompletedProcess:
    prologue = f'import sys\nsys.path.insert(0, {root_project_path!r})\n'
    if import_runner:
        prologue += 'from behavex import BehaveXRunner\n'
    return subprocess.run(
        [sys.executable, '-c', prologue + script],
        capture_output=True,
        text=True,
        cwd=root_project_path,
        env=_clean_child_env(),
        timeout=timeout,
        **run_kwargs,
    )


def _parse_result(proc: subprocess.CompletedProcess) -> dict:
    for line in proc.stdout.splitlines():
        if line.startswith('__RESULT__:'):
            return json.loads(line[len('__RESULT__:'):])
    raise AssertionError(
        f'BehaveXRunner subprocess did not emit a result.\n'
        f'STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}'
    )


def _non_result_lines(proc: subprocess.CompletedProcess) -> List[str]:
    return [line for line in proc.stdout.splitlines() if not line.startswith('__RESULT__:')]


def _store_result(context, proc: subprocess.CompletedProcess) -> None:
    context.api_run_result = _parse_result(proc)
    context.api_run_output = proc.stdout


def _run_via_api(
    context,
    feature_path: str,
    tags: Optional[List[str]] = None,
    output_folder: str = '',
    no_report: bool = True,
    **extra_kwargs,
) -> None:
    """extra_kwargs values are repr'd into the script."""
    kwargs_lines = ''.join(
        f'    {k}={v!r},\n' for k, v in extra_kwargs.items()
    )
    script = f"""
import json, sys
result = BehaveXRunner(
    paths=[{repr(feature_path)}],
    tags={repr(tags or [])},
    output_folder={repr(output_folder)},
    no_report={no_report},
{kwargs_lines}).run()
""" + _SERIALIZE_RESULT
    _store_result(context, _run_script(script))


# stop_before_workers/environment.py sets hook_entered, then waits for stop_called
_STOP_WHILE_BEFORE_ALL_WORKERS_RUNS = """
hook_entered = threading.Event()
stop_called = threading.Event()

def _stop_once_hook_entered(runner):
    hook_entered.wait(timeout=60)
    runner.stop()
    stop_called.set()
"""


_SERIALIZE_PROGRESS = """
_data = {
    "exit_code": result.exit_code,
    "passed": result.passed,
    "stopped": result.stopped,
    "final_statuses": {s.name: s.status for f in result.features for s in f.scenarios},
    "summary": result.summary.model_dump(),
    "summary_total": result.summary.total,
    "event_count": len(_events),
    "events": _events,
}
print("__RESULT__:" + json.dumps(_data))
"""


_PROGRESS_CALLBACK = """
_events = []

def _on_progress(event):
    _events.append({
        "scenario_name": event.scenario_name,
        "feature_name": event.feature_name,
        "status": event.status,
        "completed_count": event.completed_count,
        "total": event.total,
    })
"""


def _refused_input_kwargs(input_name):
    missing = os.path.join(secondary_features_path, 'missing_{}'.format(get_unique_suffix()))
    return {
        'a path that does not exist': {'paths': [missing + '.feature']},
        'a glob that matches no file': {'paths': [missing + '_*.feature']},
        'a missing rerun_failures file': {'rerun_failures': missing + '.txt'},
        'no paths and no features folder': {},
    }[input_name]


_RUN_MODES = {
    'in a single process': {},
    'as a dry run': {'dry_run': True},
    'in parallel by feature': {'parallel_processes': 2, 'parallel_scheme': 'feature'},
    'in parallel by scenario': {'parallel_processes': 2, 'parallel_scheme': 'scenario'},
}

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
from typing import List, Optional

import behave
from behave import given, then, when
from config_file_steps import _clean_child_env, _make_config_dir, _write_config_file
from execution_steps import execute_command, get_random_number
from packaging.version import Version

# behave 1.2.6 reports hook errors and undefined background steps as failed
BEHAVE_ERROR_STATUS = 'error' if Version(behave.__version__) >= Version('1.2.7') else 'failed'

root_project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
secondary_features_path = os.path.join(root_project_path, 'tests', 'features', 'secondary_features')
api_runner_features_path = os.path.join(root_project_path, 'tests', 'features', 'api_runner_features')

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


def _run_script(script: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, '-c', script],
        capture_output=True,
        text=True,
        cwd=root_project_path,
        env=_clean_child_env(),
        timeout=120,
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
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
result = BehaveXRunner(
    paths=[{repr(feature_path)}],
    tags={repr(tags or [])},
    output_folder={repr(output_folder)},
    no_report={no_report},
{kwargs_lines}).run()
""" + _SERIALIZE_RESULT
    _store_result(context, _run_script(script))


# ─────────────────────────────────────────────────────────────────────────────
# When steps
# ─────────────────────────────────────────────────────────────────────────────

@when('I run BehaveXRunner with passing tests')
def when_api_run_passing(context):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    _run_via_api(context, feature_path)


@when('I run BehaveXRunner with failing tests')
def when_api_run_failing(context):
    feature_path = os.path.join(secondary_features_path, 'failing_tests.feature')
    _run_via_api(context, feature_path)


@when('I run BehaveXRunner with passing tests filtered by tag "{tag}"')
def when_api_run_with_tag(context, tag):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    _run_via_api(context, feature_path, tags=[tag])


@when('I run BehaveXRunner with passing tests and a configured output folder')
def when_api_run_with_output_folder(context):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    output_folder = os.path.join('output', f'api_runner_{get_random_number(6)}')
    context.configured_output_folder = output_folder
    context.add_cleanup(shutil.rmtree, output_folder, ignore_errors=True)
    _run_via_api(context, feature_path, output_folder=output_folder, no_report=False)


@when('I run BehaveXRunner with passing tests using "{parallel_processes}" parallel processes and "{parallel_scheme}" parallel scheme')
def when_api_run_parallel(context, parallel_processes, parallel_scheme):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    _run_via_api(
        context,
        feature_path,
        parallel_processes=int(parallel_processes),
        parallel_scheme=parallel_scheme,
    )


@when('I run BehaveXRunner with passing tests, no_report enabled, and a configured output folder')
def when_api_run_no_report(context):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    output_folder = os.path.join('output', f'api_runner_no_report_{get_random_number(6)}')
    context.configured_output_folder = output_folder
    _run_via_api(context, feature_path, output_folder=output_folder, no_report=True)


@when('I run BehaveXRunner with passing tests filtered by tags "{tag_a}" and "{tag_b}"')
def when_api_run_with_two_tags(context, tag_a, tag_b):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    _run_via_api(context, feature_path, tags=[tag_a, tag_b])


@when('I run BehaveXRunner with dry_run enabled')
def when_api_run_dry_run(context):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    _run_via_api(context, feature_path, dry_run=True)


@when('I run BehaveXRunner with failing tests and a configured output folder')
def when_api_run_failing_with_output_folder(context):
    feature_path = os.path.join(secondary_features_path, 'failing_tests.feature')
    output_folder = os.path.join('output', f'api_runner_fail_{get_random_number(6)}')
    context.configured_output_folder = output_folder
    context.add_cleanup(shutil.rmtree, output_folder, ignore_errors=True)
    _run_via_api(context, feature_path, output_folder=output_folder, no_report=False)


# ─────────────────────────────────────────────────────────────────────────────
# Then steps
# ─────────────────────────────────────────────────────────────────────────────

@then('the RunResult exit_code should be "{expected}"')
def then_exit_code(context, expected):
    actual = context.api_run_result['exit_code']
    assert actual == int(expected), (
        f'Expected exit_code={expected}, got {actual}.\n'
        f'BehaveXRunner output:\n{context.api_run_output}'
    )


@then('the RunResult passed should be "{expected}"')
def then_passed(context, expected):
    actual = context.api_run_result['passed']
    expected_bool = expected.lower() == 'true'
    assert actual == expected_bool, (
        f'Expected passed={expected_bool}, got {actual}.\n'
        f'BehaveXRunner output:\n{context.api_run_output}'
    )


@then('the RunResult stopped should be "{expected}"')
def then_stopped(context, expected):
    actual = context.api_run_result['stopped']
    assert actual == (expected == 'True'), (
        f'Expected stopped={expected}, got {actual}.\n'
        f'BehaveXRunner output:\n{context.api_run_output}'
    )


@then('I should see "{text}" in the BehaveXRunner output')
def then_output_contains(context, text):
    assert text in context.api_run_output, (
        f'Expected to find "{text}" in BehaveXRunner output.\n'
        f'Full output:\n{context.api_run_output}'
    )


@then('the RunResult output_folder is the absolute path of the configured output folder')
def then_output_folder_matches(context):
    then_output_folder_is_absolute(context, context.configured_output_folder)


@then('the RunResult output_folder is the absolute path of "{folder}"')
def then_output_folder_is_absolute(context, folder):
    actual = context.api_run_result['output_folder']
    expected = os.path.join(root_project_path, folder)
    assert actual == expected, (
        f'Expected output_folder={repr(expected)}, got {repr(actual)}.\n'
        f'BehaveXRunner output:\n{context.api_run_output}'
    )


@then('the configured output folder should not exist on the filesystem')
def then_output_folder_absent(context):
    folder = context.configured_output_folder
    assert not os.path.exists(folder), (
        f'Expected output folder to NOT exist with no_report=True, but found: {folder}'
    )


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic optional-extras isolation steps
# Simulate "pydantic not installed" by blocking it in sys.modules inside a
# subprocess, so the real venv is never touched.
# ─────────────────────────────────────────────────────────────────────────────

_BLOCK_PYDANTIC_SCRIPT = """
import sys
# Block pydantic before any behavex import so the ImportError path is exercised
sys.modules['pydantic'] = None
{body}
"""


def _run_without_pydantic(script_body: str) -> subprocess.CompletedProcess:
    """Run a Python snippet in a subprocess with pydantic blocked via sys.modules."""
    script = _BLOCK_PYDANTIC_SCRIPT.format(body=script_body)
    return subprocess.run(
        [sys.executable, '-c', script],
        capture_output=True,
        text=True,
        cwd=root_project_path,
        env=_clean_child_env(),
        timeout=60,
    )


@when('I run the behavex CLI without pydantic available')
def when_cli_without_pydantic(context):
    proc = _run_without_pydantic(f"""
import sys
sys.path.insert(0, {repr(root_project_path)})
from behavex.runner import main
sys.argv = ['behavex', '--help']
try:
    main()
except SystemExit as e:
    print(f'EXIT:{{e.code}}')
""")
    context.cli_proc = proc


@then('the CLI exits successfully')
def then_cli_exits_ok(context):
    proc = context.cli_proc
    output = proc.stdout + proc.stderr
    assert 'ImportError' not in output and 'pydantic' not in output.lower(), (
        f'CLI raised a pydantic-related error:\n{output}'
    )
    assert proc.returncode == 0 and 'EXIT:0' in proc.stdout.splitlines(), (
        f'CLI did not exit cleanly:\n{output}'
    )


@then('pydantic was not required')
def then_pydantic_not_required(context):
    output = context.cli_proc.stdout + context.cli_proc.stderr
    assert 'pydantic' not in output.lower(), (
        f'Unexpected pydantic reference in CLI output:\n{output}'
    )


@when('I import BehaveXRunner without pydantic available')
def when_import_runner_without_pydantic(context):
    proc = _run_without_pydantic(f"""
import sys
sys.path.insert(0, {repr(root_project_path)})
try:
    from behavex.api import BehaveXRunner
    print('NO_ERROR')
except ImportError as e:
    print(f'IMPORT_ERROR:{{e}}')
""")
    context.import_proc = proc


@then('an ImportError is raised mentioning "{expected_text}"')
def then_import_error_raised(context, expected_text):
    output = context.import_proc.stdout
    assert 'IMPORT_ERROR:' in output, (
        f'Expected an ImportError but none was raised.\nOutput:\n{output}'
    )
    error_msg = output.split('IMPORT_ERROR:', 1)[1].strip()
    assert expected_text in error_msg, (
        f'ImportError message does not mention "{expected_text}".\nGot: {error_msg}'
    )


# ─────────────────────────────────────────────────────────────────────────────
# Model assertion steps
# ─────────────────────────────────────────────────────────────────────────────

@then('the RunResult has at least "{expected}" feature')
@then('the RunResult has at least "{expected}" features')
def then_feature_count_at_least(context, expected):
    actual = context.api_run_result['feature_count']
    assert actual >= int(expected), (
        f'Expected at least {expected} feature(s), got {actual}.'
    )


@then('the RunResult has "{expected}" features')
def then_feature_count_exact(context, expected):
    actual = context.api_run_result['feature_count']
    assert actual == int(expected), (
        f'Expected exactly {expected} feature(s), got {actual}.'
    )


@then('the RunResult first feature name is "{expected}"')
def then_first_feature_name(context, expected):
    features = context.api_run_result['features']
    assert features, 'RunResult has no features.'
    actual = features[0]['name']
    assert actual == expected, (
        f'Expected first feature name "{expected}", got "{actual}".'
    )


@then('the RunResult first feature status is "{expected}"')
def then_first_feature_status(context, expected):
    features = context.api_run_result['features']
    assert features, 'RunResult has no features.'
    actual = features[0]['status']
    assert actual == expected, (
        f'Expected first feature status "{expected}", got "{actual}".'
    )


@then('the RunResult summary total is greater than "{expected}"')
def then_summary_total_gt(context, expected):
    actual = context.api_run_result['summary']['total']
    assert actual > int(expected), (
        f'Expected summary.total > {expected}, got {actual}.'
    )


@then('the RunResult summary total is "{expected}"')
def then_summary_total(context, expected):
    actual = context.api_run_result['summary']['total']
    assert actual == int(expected), (
        f'Expected summary.total={expected}, got {actual}.'
    )


@then('the RunResult summary passed is "{expected}"')
def then_summary_passed(context, expected):
    actual = context.api_run_result['summary']['passed']
    assert actual == int(expected), (
        f'Expected summary.passed={expected}, got {actual}.'
    )


@then('the RunResult summary failed is "{expected}"')
def then_summary_failed(context, expected):
    actual = context.api_run_result['summary']['failed']
    assert actual == int(expected), (
        f'Expected summary.failed={expected}, got {actual}.'
    )


@then('the RunResult summary skipped is "{expected}"')
def then_summary_skipped(context, expected):
    actual = context.api_run_result['summary']['skipped']
    assert actual == int(expected), (
        f'Expected summary.skipped={expected}, got {actual}.'
    )


@then('the RunResult summary untested is "{expected}"')
def then_summary_untested(context, expected):
    actual = context.api_run_result['summary']['untested']
    assert actual == int(expected), (
        f'Expected summary.untested={expected}, got {actual}.'
    )


@then('the RunResult summary has no failed scenarios')
def then_summary_no_failures(context):
    actual = context.api_run_result['summary']['failed']
    assert actual == 0, f'Expected summary.failed=0, got {actual}.'


@then('the RunResult summary has no skipped scenarios')
def then_summary_no_skipped(context):
    actual = context.api_run_result['summary']['skipped']
    assert actual == 0, f'Expected summary.skipped=0, got {actual}.'


@then('the RunResult has "{expected}" failed scenario')
@then('the RunResult has "{expected}" failed scenarios')
def then_failed_scenario_count(context, expected):
    actual = context.api_run_result['failed_scenario_count']
    assert actual == int(expected), (
        f'Expected {expected} failed scenario(s), got {actual}.'
    )


@then('the RunResult first failed scenario name is "{expected}"')
def then_first_failed_scenario_name(context, expected):
    scenarios = context.api_run_result['failed_scenarios']
    assert scenarios, 'RunResult has no failed scenarios.'
    actual = scenarios[0]['name']
    assert actual == expected, (
        f'Expected first failed scenario name "{expected}", got "{actual}".'
    )


@then('the RunResult run_id is a valid UUID')
def then_run_id_is_uuid(context):
    run_id = context.api_run_result['run_id']
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
    assert re.match(uuid_pattern, run_id), (
        f'Expected run_id to be a valid UUID4, got: {repr(run_id)}'
    )


@when('I run BehaveXRunner with passing tests twice')
def when_api_run_passing_twice(context):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner

runner = BehaveXRunner(paths=[{repr(feature_path)}], no_report=True)
result1 = runner.run()
result2 = runner.run()
print("__RESULT__:" + json.dumps({{
    "run_id_1": result1.run_id,
    "run_id_2": result2.run_id,
    "exit_code_1": result1.exit_code,
    "exit_code_2": result2.exit_code,
}}))
"""
    proc = _run_script(script)
    _store_result(context, proc)


@then('the two run_ids are different')
def then_run_ids_differ(context):
    id1 = context.api_run_result['run_id_1']
    id2 = context.api_run_result['run_id_2']
    assert id1 != id2, (
        f'Expected two different run_ids but both were: {repr(id1)}'
    )


@then('at least one scenario in the RunResult has tags')
def then_some_scenarios_have_tags(context):
    count = context.api_run_result['tagged_scenario_count']
    assert count > 0, (
        'Expected at least one scenario with tags in RunResult, but tagged_scenario_count=0.'
    )


@then('the RunResult first failed scenario has error details')
def then_first_failed_scenario_has_errors(context):
    scenarios = context.api_run_result['failed_scenarios']
    assert scenarios, 'RunResult has no failed scenarios.'
    scenario = scenarios[0]
    assert scenario['error_msg'], (
        f'Expected error_msg to be non-empty for failed scenario "{scenario["name"]}".'
    )
    assert scenario['has_error_step'], (
        f'Expected error_step to be set for failed scenario "{scenario["name"]}".'
    )


@then('both runs completed successfully')
def then_both_runs_passed(context):
    code1 = context.api_run_result['exit_code_1']
    code2 = context.api_run_result['exit_code_2']
    assert code1 == 0 and code2 == 0, (
        f'Expected both runs to exit with code 0, got: run1={code1}, run2={code2}.\n'
        f'Output:\n{context.api_run_output}'
    )


# ─────────────────────────────────────────────────────────────────────────────
# _build_args coverage — name, stop_on_failure, define, logging_level
# ─────────────────────────────────────────────────────────────────────────────

@when('I run BehaveXRunner with passing tests filtered by name "{name}"')
def when_api_run_with_name(context, name):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    _run_via_api(context, feature_path, name=name)


@when('I run BehaveXRunner with failing tests and stop_on_failure enabled')
def when_api_run_stop_on_failure(context):
    feature_path = os.path.join(secondary_features_path, 'failing_tests.feature')
    _run_via_api(context, feature_path, stop_on_failure=True)


@when('I run BehaveXRunner with userdata tests and define "{userdata}"')
def when_api_run_with_define(context, userdata):
    feature_path = os.path.join(secondary_features_path, 'userdata_tests.feature')
    _run_via_api(context, feature_path, tags=['@USERDATA'], define=[userdata])


@when('I run BehaveXRunner with passing tests and logging_level "{level}"')
def when_api_run_with_logging_level(context, level):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    _run_via_api(context, feature_path, logging_level=level)


# ─────────────────────────────────────────────────────────────────────────────
# on_progress callback steps
# ─────────────────────────────────────────────────────────────────────────────

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

_RAISING_ON_FIRST_CALL_PROGRESS_CALLBACK = _PROGRESS_CALLBACK + """
    if len(_events) == 1:
        raise RuntimeError("boom")
"""

_RAISING_PROGRESS_CALLBACK = """
def _on_progress(event):
    raise RuntimeError("boom")
"""

_SERIALIZE_EXIT_CODE_ONLY = """
_data = {"exit_code": result.exit_code, "event_count": 0, "events": []}
print("__RESULT__:" + json.dumps(_data))
"""


def _run_with_progress_callback(
    context,
    feature_path: str,
    callback_snippet: str = _PROGRESS_CALLBACK,
    parallel_processes: int = 1,
    parallel_scheme: str = 'scenario',
    serialize_snippet: str = _SERIALIZE_PROGRESS,
    stop_on_failure: bool = False,
    tags: Optional[List[str]] = None,
    name: Optional[str] = None,
) -> None:
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
{callback_snippet}
result = BehaveXRunner(
    paths=[{repr(feature_path)}],
    tags={repr(tags or [])},
    no_report=True,
    parallel_processes={parallel_processes},
    parallel_scheme={repr(parallel_scheme)},
    stop_on_failure={stop_on_failure},
    name={name!r},
    on_progress=_on_progress,
).run()
""" + serialize_snippet
    proc = _run_script(script)
    _store_result(context, proc)


@when('I run BehaveXRunner with passing tests and an on_progress callback')
def when_api_run_with_progress_callback(context):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    _run_with_progress_callback(context, feature_path)


@when('I run BehaveXRunner with passing tests using "{parallel_processes}" parallel processes, "{parallel_scheme}" scheme, and an on_progress callback')
def when_api_run_parallel_with_progress_callback(context, parallel_processes, parallel_scheme):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    _run_with_progress_callback(
        context,
        feature_path,
        parallel_processes=int(parallel_processes),
        parallel_scheme=parallel_scheme,
    )


@when('I run BehaveXRunner with stop_on_failure on a failure followed by passing scenarios using "{parallel_processes}" parallel processes and an on_progress callback')
def when_api_run_stop_on_failure_with_progress_callback(context, parallel_processes):
    _run_with_progress_callback(
        context,
        os.path.join(api_runner_features_path, 'stop_on_failure.feature'),
        parallel_processes=int(parallel_processes),
        stop_on_failure=True,
    )


@when('I run BehaveXRunner on @SERIAL and parallel scenarios using "{parallel_processes}" parallel processes, "{parallel_scheme}" scheme, and an on_progress callback')
def when_api_run_serial_mix_with_progress_callback(context, parallel_processes, parallel_scheme):
    _run_with_progress_callback(
        context,
        os.path.join(api_runner_features_path, 'serial_mix'),
        parallel_processes=int(parallel_processes),
        parallel_scheme=parallel_scheme,
    )


@when('I run BehaveXRunner with passing tests and an on_progress callback that always raises')
def when_api_run_with_raising_progress_callback(context):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    _run_with_progress_callback(
        context,
        feature_path,
        callback_snippet=_RAISING_PROGRESS_CALLBACK,
        serialize_snippet=_SERIALIZE_EXIT_CODE_ONLY,
    )


@when('I run BehaveXRunner with passing tests and an on_progress callback that raises on its first call')
def when_api_run_with_raising_once_progress_callback(context):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    _run_with_progress_callback(
        context,
        feature_path,
        callback_snippet=_RAISING_ON_FIRST_CALL_PROGRESS_CALLBACK,
    )


@then('the on_progress callback was called once per scenario in the RunResult summary')
def then_progress_callback_called_once_per_scenario(context):
    result = context.api_run_result
    assert result['summary_total'] > 0, (
        f'Expected at least one scenario in the summary.\n'
        f'BehaveXRunner output:\n{context.api_run_output}'
    )
    assert result['event_count'] == result['summary_total'], (
        f'Expected {result["summary_total"]} on_progress call(s), got {result["event_count"]}.\n'
        f'BehaveXRunner output:\n{context.api_run_output}'
    )


@then('each on_progress event has a non-empty scenario_name and feature_name')
def then_progress_events_have_names(context):
    events = context.api_run_result['events']
    assert events, 'No on_progress events were captured.'
    for i, event in enumerate(events):
        assert event['scenario_name'], f'Event {i} has empty scenario_name: {event}'
        assert event['feature_name'], f'Event {i} has empty feature_name: {event}'


@then('each on_progress event has a status of "{expected_status}"')
def then_progress_events_have_status(context, expected_status):
    events = context.api_run_result['events']
    assert events, 'No on_progress events were captured.'
    for i, event in enumerate(events):
        assert event['status'] == expected_status, (
            f'Event {i} has status "{event["status"]}", expected "{expected_status}": {event}'
        )


@then('the completed_count in on_progress events is strictly increasing up to the summary total')
def then_progress_completed_count_strictly_increasing(context):
    events = context.api_run_result['events']
    assert events, 'No on_progress events were captured.'
    completed_values = [e['completed_count'] for e in events]
    for i in range(1, len(completed_values)):
        assert completed_values[i] > completed_values[i - 1], (
            f'completed_count is not strictly increasing at index {i}: {completed_values}'
        )
    assert completed_values[-1] == context.api_run_result['summary_total'], (
        f'Expected the last completed_count to be {context.api_run_result["summary_total"]}: {completed_values}'
    )


@when('I run BehaveXRunner with failing tests and an on_progress callback')
def when_api_run_failing_with_progress_callback(context):
    feature_path = os.path.join(secondary_features_path, 'failing_tests.feature')
    _run_with_progress_callback(context, feature_path)


@when('I run BehaveXRunner with failing tests using "{parallel_processes}" parallel processes, "{parallel_scheme}" scheme, and an on_progress callback')
def when_api_run_failing_parallel_with_progress_callback(context, parallel_processes, parallel_scheme):
    feature_path = os.path.join(secondary_features_path, 'failing_tests.feature')
    _run_with_progress_callback(
        context,
        feature_path,
        parallel_processes=int(parallel_processes),
        parallel_scheme=parallel_scheme,
    )


@then('at least one on_progress event has behave\'s error status')
def then_at_least_one_progress_event_has_behave_error_status(context):
    then_at_least_one_progress_event_has_status(context, BEHAVE_ERROR_STATUS)


@then('at least one on_progress event has a status of "{expected_status}"')
def then_at_least_one_progress_event_has_status(context, expected_status):
    events = context.api_run_result['events']
    assert events, 'No on_progress events were captured.'
    matching = [e for e in events if e['status'] == expected_status]
    assert matching, (
        f'No on_progress event with status "{expected_status}" found.\n'
        f'Events: {events}'
    )


# ─────────────────────────────────────────────────────────────────────────────
# stop() steps
# ─────────────────────────────────────────────────────────────────────────────

@when('I call stop() on a BehaveXRunner that is not running')
def when_stop_outside_run(context):
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
runner = BehaveXRunner(paths=["tests/features"])
try:
    runner.stop()
    exception = None
except Exception as e:
    exception = str(e)
_data = {{"exit_code": 0, "exception": exception}}
print("__RESULT__:" + json.dumps(_data))
"""
    proc = _run_script(script)
    _store_result(context, proc)


@when('I run BehaveXRunner with passing tests and call stop() from a background thread')
def when_run_with_stop_non_parallel(context):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    script = f"""
import json, sys, threading
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner

runner = BehaveXRunner(paths=[{repr(feature_path)}], no_report=True)
exception = None

# stop() has no effect on a single-process run
timer = threading.Timer(0.5, runner.stop)
timer.start()
try:
    result = runner.run()
    exit_code = result.exit_code
except Exception as e:
    exit_code = 2
    exception = str(e)
finally:
    timer.cancel()

_data = {{"exit_code": exit_code, "exception": exception}}
print("__RESULT__:" + json.dumps(_data))
"""
    proc = _run_script(script)
    _store_result(context, proc)


@when('I run BehaveXRunner with passing tests in parallel and call stop() from a background thread')
def when_run_parallel_with_stop(context):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    script = f"""
import json, sys, threading
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner

runner = BehaveXRunner(
    paths=[{repr(feature_path)}],
    no_report=True,
    parallel_processes=2,
    parallel_scheme='scenario',
)
exception = None

timer = threading.Timer(0.5, runner.stop)
timer.start()
try:
    result = runner.run()
    exit_code = result.exit_code
except Exception as e:
    exit_code = 2
    exception = str(e)
finally:
    timer.cancel()

_data = {{"exit_code": exit_code, "exception": exception}}
print("__RESULT__:" + json.dumps(_data))
"""
    proc = _run_script(script)
    _store_result(context, proc)


@then('no exception was raised')
def then_no_exception(context):
    exception = context.api_run_result.get('exception')
    assert exception is None, (
        f'Expected no exception but got: {exception}\n'
        f'BehaveXRunner output:\n{context.api_run_output}'
    )


@when('I run BehaveXRunner on "{fixture}" with "{parallel_processes}" parallel processes, "{parallel_scheme}" scheme, and call stop() on progress event "{event_number}"')
def when_run_parallel_stopping_on_event(context, fixture, parallel_processes, parallel_scheme, event_number):
    feature_path = os.path.join(api_runner_features_path, fixture)
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
{_PROGRESS_CALLBACK}
_record = _on_progress

def _on_progress(event):
    _record(event)
    if len(_events) == {int(event_number)}:
        runner.stop()

runner = BehaveXRunner(
    paths=[{repr(feature_path)}],
    no_report=True,
    parallel_processes={int(parallel_processes)},
    parallel_scheme={repr(parallel_scheme)},
    on_progress=_on_progress,
)
result = runner.run()
""" + _SERIALIZE_PROGRESS
    _store_result(context, _run_script(script))


@when('I run BehaveXRunner on "{fixture}" with "{parallel_processes}" parallel processes, "{parallel_scheme}" scheme, and call stop() while before_all_workers runs')
def when_run_parallel_stopping_in_before_all_workers(context, fixture, parallel_processes, parallel_scheme):
    feature_path = os.path.join(api_runner_features_path, fixture)
    script = f"""
import json, sys, threading
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner

{_STOP_WHILE_BEFORE_ALL_WORKERS_RUNS}
runner = BehaveXRunner(
    paths=[{repr(feature_path)}],
    no_report=True,
    parallel_processes={int(parallel_processes)},
    parallel_scheme={repr(parallel_scheme)},
)
threading.Thread(target=_stop_once_hook_entered, args=(runner,), daemon=True).start()
result = runner.run()
_events = []
""" + _SERIALIZE_PROGRESS
    _store_result(context, _run_script(script))


@then('the RunResult summary total is less than "{expected}"')
def then_summary_total_lt(context, expected):
    actual = context.api_run_result['summary_total']
    assert actual < int(expected), (
        f'Expected summary.total < {expected}, got {actual}.\n'
        f'BehaveXRunner output:\n{context.api_run_output}'
    )


# ─────────────────────────────────────────────────────────────────────────────
# Repeated in-process runs, @MANUAL counting and CLI lazy imports
# ─────────────────────────────────────────────────────────────────────────────

@when('I run BehaveXRunner on passing tests in one process with tags "{tag_a}", none, "{tag_b}", none')
def when_api_run_repeated_with_tags(context, tag_a, tag_b):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
totals = [
    BehaveXRunner(paths=[{repr(feature_path)}], tags=tags, no_report=True).run().summary.total
    for tags in ([{repr(tag_a)}], [], [{repr(tag_b)}], [])
]
print("__RESULT__:" + json.dumps({{"totals": totals}}))
"""
    _store_result(context, _run_script(script))


@when('I run BehaveXRunner in one process on passing tests, then failing tests, then passing tests with "{processes}" parallel processes')
def when_api_run_repeated_with_paths(context, processes):
    passing_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    failing_path = os.path.join(secondary_features_path, 'failing_tests.feature')
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
totals = [
    BehaveXRunner(paths=[path], parallel_processes={int(processes)}, no_report=True).run().summary.total
    for path in ({repr(passing_path)}, {repr(failing_path)}, {repr(passing_path)})
]
print("__RESULT__:" + json.dumps({{"totals": totals}}))
"""
    _store_result(context, _run_script(script))


@then('the in-process run totals are "{expected}"')
def then_in_process_run_totals(context, expected):
    actual = context.api_run_result['totals']
    assert actual == [int(t) for t in expected.split(',')], (
        f'Expected run totals [{expected}], got {actual}.\n'
        f'BehaveXRunner output:\n{context.api_run_output}'
    )


@when('I run BehaveXRunner with a feature holding one automated and one @MANUAL scenario')
def when_api_run_with_manual_scenario(context):
    _run_via_api(context, os.path.join(api_runner_features_path, 'manual_tests.feature'))


@then('the RunResult summary manual is "{expected}"')
def then_summary_manual(context, expected):
    actual = context.api_run_result['summary']['manual']
    assert actual == int(expected), f'Expected summary.manual={expected}, got {actual}.'


@then('the RunResult summary counts add up to the total')
def then_summary_counts_add_up(context):
    summary = context.api_run_result['summary']
    counted = sum(summary[k] for k in ('passed', 'failed', 'error', 'skipped', 'untested', 'manual'))
    assert counted == summary['total'], f'Summary counts do not add up to the total: {summary}'


@when('I run the behavex CLI on passing tests and list the loaded modules')
def when_cli_run_listing_modules(context):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex.runner import main
sys.argv = ['behavex', {repr(feature_path)}, '--no-report']
try:
    main()
except SystemExit:
    pass
print("__RESULT__:" + json.dumps({{"modules": [m for m in ('behavex.models', 'pydantic') if m in sys.modules]}}))
"""
    _store_result(context, _run_script(script))


@then('the CLI run loaded neither "{module_a}" nor "{module_b}"')
def then_cli_loaded_neither(context, module_a, module_b):
    loaded = context.api_run_result['modules']
    assert module_a not in loaded and module_b not in loaded, (
        f'The CLI imported {loaded}.\nOutput:\n{context.api_run_output}'
    )


# ─────────────────────────────────────────────────────────────────────────────
# Autoretry progress, irregular error messages, interrupted runs, config files
# ─────────────────────────────────────────────────────────────────────────────

@when('I run BehaveXRunner on @AUTORETRY scenarios that pass on a retry or fail every attempt with an on_progress callback')
def when_api_run_autoretry_with_progress_callback(context):
    _run_with_progress_callback(context, os.path.join(api_runner_features_path, 'autoretry_flaky.feature'))


@when('I run BehaveXRunner on @AUTORETRY scenarios whose step raises an error or whose teardown fails on every attempt with an on_progress callback')
def when_api_run_autoretry_errors_with_progress_callback(context):
    _run_with_progress_callback(
        context, os.path.join(api_runner_features_path, 'teardown_error', 'autoretry_errors.feature')
    )


@when('I run BehaveXRunner with tags "{tags}" on @AUTORETRY scenarios, one excluded by the tag filter, with an on_progress callback')
def when_api_run_filtered_autoretry_with_progress_callback(context, tags):
    _run_with_progress_callback(
        context, os.path.join(api_runner_features_path, 'autoretry_filtered.feature'), tags=[tags]
    )


@when('I run BehaveXRunner with name "{name}" on an @AUTORETRY Scenario Outline with an on_progress callback')
def when_api_run_name_filtered_autoretry_outline_with_progress_callback(context, name):
    _run_with_progress_callback(
        context, os.path.join(api_runner_features_path, 'autoretry_outline_by_name.feature'), name=name
    )


@then('no on_progress event is for the scenario "{scenario_name}"')
def then_no_progress_event_for_scenario(context, scenario_name):
    events = context.api_run_result['events']
    assert all(e['scenario_name'] != scenario_name for e in events), (
        f'Unexpected on_progress event for "{scenario_name}": {events}'
    )


@when('I run BehaveXRunner with a feature whose background step is undefined')
def when_api_run_undefined_background(context):
    _run_via_api(
        context,
        os.path.join(root_project_path, 'tests', 'features', 'background_features', 'undefined_background_tests.feature'),
    )


@when('I run BehaveXRunner with a crashing test using "{parallel_processes}" parallel processes and "{parallel_scheme}" parallel scheme')
def when_api_run_crashing_parallel(context, parallel_processes, parallel_scheme):
    _run_via_api(
        context,
        os.path.join(root_project_path, 'tests', 'features', 'crashing_features', 'crashing_tests.feature'),
        parallel_processes=int(parallel_processes),
        parallel_scheme=parallel_scheme,
    )


@then('the RunResult first failed scenario has behave\'s error status and the error message "{message}"')
def then_first_failed_scenario_behave_error_status_and_message(context, message):
    then_first_failed_scenario_status_and_message(context, BEHAVE_ERROR_STATUS, message)


@then('the RunResult first failed scenario has status "{status}" and the error message "{message}"')
def then_first_failed_scenario_status_and_message(context, status, message):
    scenarios = context.api_run_result['failed_scenarios']
    assert scenarios, f'RunResult has no failed scenarios.\nOutput:\n{context.api_run_output}'
    assert (scenarios[0]['status'], scenarios[0]['error_msg']) == (status, [message]), scenarios[0]


@when('I run BehaveXRunner with passing tests while merging the results raises KeyboardInterrupt')
def when_api_run_interrupted_before_merge(context):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner, runner

def _interrupt(*args, **kwargs):
    raise KeyboardInterrupt

runner.wrap_up_process_pools = _interrupt
result = BehaveXRunner(paths=[{repr(feature_path)}], no_report=True).run()
""" + _SERIALIZE_RESULT
    _store_result(context, _run_script(script))


@when('the runner waits on a queued future that stop() cancels meanwhile')
def when_waiting_on_future_cancelled_meanwhile(context):
    script = f"""
import json, sys, threading
sys.path.insert(0, {repr(root_project_path)})
from concurrent.futures import Future
from behavex import runner

future = Future()
threading.Timer(0.3, future.cancel).start()
execution_codes = []
runner._wait_for_futures([future], execution_codes, [])
print("__RESULT__:" + json.dumps({{"execution_codes": execution_codes}}))
"""
    _store_result(context, _run_script(script))


@then('no execution code was recorded for the cancelled future')
def then_no_execution_code_recorded(context):
    assert context.api_run_result['execution_codes'] == [], context.api_run_result


@when('I run BehaveXRunner in one process with a config file setting output folder "{folder_a}", then one setting "{folder_b}"')
def when_api_run_with_two_config_files(context, folder_a, folder_b):
    base = os.path.join(root_project_path, 'output', f'api_runner_config_{get_random_number(6)}')
    context.add_cleanup(shutil.rmtree, base, ignore_errors=True)
    os.makedirs(base)
    config_paths = []
    context.expected_output_folders = []
    for folder in (folder_a, folder_b):
        output_folder = os.path.join(base, folder)
        config_path = os.path.join(base, f'{folder}.cfg')
        with open(config_path, 'w') as config_file:
            config_file.write(f'[output]\npath={output_folder}\n')
        config_paths.append(config_path)
        context.expected_output_folders.append(output_folder)
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
folders = [BehaveXRunner(paths=[{repr(feature_path)}], config=path).run().output_folder for path in {config_paths!r}]
print("__RESULT__:" + json.dumps({{"output_folders": folders}}))
"""
    _store_result(context, _run_script(script))


@then("each in-process run reported and wrote its report to its own config's output folder")
def then_each_run_used_its_config(context):
    expected = context.expected_output_folders
    assert context.api_run_result['output_folders'] == expected, (
        f'Expected output folders {expected}, got {context.api_run_result["output_folders"]}.\n'
        f'Output:\n{context.api_run_output}'
    )
    for folder in expected:
        assert os.path.isfile(os.path.join(folder, 'report.json')), f'No report.json in {folder}'



# ─────────────────────────────────────────────────────────────────────────────
# Per-run state across in-process runs and after_scenario hook errors
# ─────────────────────────────────────────────────────────────────────────────

@when('I run BehaveXRunner in one process on passing tests, then with include_paths on failing tests only')
def when_api_run_paths_then_include_paths(context):
    passing_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    failing_path = os.path.join(secondary_features_path, 'failing_tests.feature')
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
totals = [
    BehaveXRunner(paths=[{repr(passing_path)}], no_report=True).run().summary.total,
    BehaveXRunner(include_paths=[{repr(failing_path)}], no_report=True).run().summary.total,
]
print("__RESULT__:" + json.dumps({{"totals": totals}}))
"""
    _store_result(context, _run_script(script))


@when('I run BehaveXRunner in one process with rerun_failures on the failing test, then on passing tests with "{processes}" parallel processes')
def when_api_run_rerun_failures_then_parallel(context, processes):
    base = os.path.join(root_project_path, 'output', f'api_runner_rerun_{get_random_number(6)}')
    context.add_cleanup(shutil.rmtree, base, ignore_errors=True)
    os.makedirs(base)
    failures_file = os.path.join(base, 'failing_scenarios.txt')
    with open(failures_file, 'w') as failures:
        failures.write(os.path.join(secondary_features_path, 'failing_tests.feature') + ':3')
    passing_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
totals = [
    BehaveXRunner(rerun_failures={repr(failures_file)}, no_report=True).run().summary.total,
    BehaveXRunner(paths=[{repr(passing_path)}], parallel_processes={int(processes)}, no_report=True).run().summary.total,
]
print("__RESULT__:" + json.dumps({{"totals": totals}}))
"""
    _store_result(context, _run_script(script))


@when('I run BehaveXRunner on passing scenarios, one with a failing after_scenario hook, with an on_progress callback')
def when_api_run_failing_teardown_with_progress_callback(context):
    _run_with_progress_callback(
        context, os.path.join(api_runner_features_path, 'teardown_error', 'teardown_error.feature')
    )


@when('I run BehaveXRunner on passing scenarios, one with a failing cleanup and one with a failing after_tag hook, with an on_progress callback')
def when_api_run_late_teardown_errors_with_progress_callback(context):
    _run_with_progress_callback(
        context, os.path.join(api_runner_features_path, 'teardown_error', 'late_teardown_errors.feature')
    )


@then("each on_progress event status matches the scenario's final status in the RunResult")
def then_progress_status_matches_final_status(context):
    final_statuses = context.api_run_result['final_statuses']
    reported = {e['scenario_name']: e['status'] for e in context.api_run_result['events']}
    assert reported == final_statuses, (
        f'on_progress statuses {reported} differ from the final statuses {final_statuses}.\n'
        f'BehaveXRunner output:\n{context.api_run_output}'
    )


@when('I run BehaveXRunner in one process on worker hook tests, then on passing tests')
def when_api_run_worker_hooks_then_passing(context):
    worker_hooks_path = os.path.join(root_project_path, 'tests', 'features', 'worker_hooks_features')
    passing_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    suffix = get_random_number(6)
    output_folders = [os.path.join(root_project_path, 'output', f'api_runner_hooks_{suffix}_{run}') for run in (1, 2)]
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
for path, output_folder in zip(({repr(worker_hooks_path)}, {repr(passing_path)}), {repr(output_folders)}):
    BehaveXRunner(paths=[path], output_folder=output_folder).run()
print("__RESULT__:" + json.dumps({{"output_folders": {repr(output_folders)}}}))
"""
    _store_result(context, _run_script(script))


@then('the second run did not call any worker hook')
def then_second_run_called_no_worker_hook(context):
    first_folder, second_folder = context.api_run_result['output_folders']
    assert os.path.exists(os.path.join(first_folder, 'worker_hook_calls.log')), (
        f'The first run did not call its worker hooks.\nBehaveXRunner output:\n{context.api_run_output}'
    )
    assert not os.path.exists(os.path.join(second_folder, 'worker_hook_calls.log')), (
        f'The second run called the first run\'s worker hooks.\nBehaveXRunner output:\n{context.api_run_output}'
    )


# ─────────────────────────────────────────────────────────────────────────────
# Hook state across runs, slow result callbacks after stop() and invalid arguments
# ─────────────────────────────────────────────────────────────────────────────

@when('I run BehaveXRunner in one process as a dry run, then as a real run, on passing scenarios, one with a failing after_scenario hook')
def when_api_dry_run_then_real_run(context):
    feature_path = os.path.join(api_runner_features_path, 'teardown_error', 'teardown_error.feature')
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
BehaveXRunner(paths=[{repr(feature_path)}], dry_run=True, no_report=True).run()
result = BehaveXRunner(paths=[{repr(feature_path)}], no_report=True).run()
""" + _SERIALIZE_RESULT
    _store_result(context, _run_script(script))


@when('I run BehaveXRunner on "twelve_scenarios.feature" with "2" parallel processes, slow result callbacks, and call stop() on progress event "1"')
def when_run_parallel_slow_callbacks_stopping_on_first_event(context):
    feature_path = os.path.join(api_runner_features_path, 'twelve_scenarios.feature')
    script = f"""
import json, sys, time
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner, utils
{_PROGRESS_CALLBACK}
_record = _on_progress
_handle_result = utils.handle_execution_complete_callback
_results_handled = []

def _slow_handle_result(codes, json_reports, progress_bar, future):
    if future.cancelled():
        return
    time.sleep(0.5)
    _handle_result(codes, json_reports, progress_bar, future)
    _results_handled.append(future)

utils.handle_execution_complete_callback = _slow_handle_result

def _on_progress(event):
    _record(event)
    if len(_events) == 1:
        runner.stop()

runner = BehaveXRunner(paths=[{repr(feature_path)}], no_report=True, parallel_processes=2,
                       parallel_scheme='scenario', on_progress=_on_progress)
result = runner.run()
_events_at_return = len(_events)
time.sleep(2)
print("__HANDLED__:" + json.dumps({{"results_handled": len(_results_handled), "events_at_return": _events_at_return}}))
""" + _SERIALIZE_PROGRESS
    _store_result(context, _run_script(script))
    for line in context.api_run_output.splitlines():
        if line.startswith('__HANDLED__:'):
            context.api_run_result.update(json.loads(line[len('__HANDLED__:'):]))


@then('every scenario whose result was handled is in the RunResult and fired its event before run() returned')
def then_every_handled_result_reported(context):
    result = context.api_run_result
    assert result['stopped'], result
    assert result['summary_total'] == result['results_handled'] == result['events_at_return'], (
        f'{result["results_handled"]} results handled, {result["summary_total"]} in the RunResult, '
        f'{result["events_at_return"]} events before run() returned.\nOutput:\n{context.api_run_output}'
    )


@when('I run BehaveXRunner on passing tests with {argument} set to "{value}"')
def when_api_run_with_argument_value(context, argument, value):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
{_CAPTURE_RAISED}
raised = _capture_raised(lambda: BehaveXRunner(paths=[{repr(feature_path)}], no_report=True, {argument}={repr(value)}).run())
print("__RESULT__:" + json.dumps({{"raised": raised}}))
"""
    _store_result(context, _run_script(script))


def _refused_input_kwargs(input_name):
    missing = os.path.join(secondary_features_path, 'missing_{}'.format(get_random_number(6)))
    return {
        'a path that does not exist': {'paths': [missing + '.feature']},
        'a glob that matches no file': {'paths': [missing + '_*.feature']},
        'a missing rerun_failures file': {'rerun_failures': missing + '.txt'},
        'no paths and no features folder': {},
    }[input_name]


@when('I call run() with {input_name}')
def when_api_run_refused_input(context, input_name):
    kwargs = _refused_input_kwargs(input_name)
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
{_CAPTURE_RAISED}
raised = _capture_raised(lambda: BehaveXRunner(no_report=True, **{kwargs!r}).run())
print("__RESULT__:" + json.dumps({{"raised": raised}}))
"""
    _store_result(context, _run_script(script))


@then('run() raised a ValueError mentioning "{text}"')
@then('discover() raised a ValueError mentioning "{text}"')
@then('load_results() raised a ValueError mentioning "{text}"')
def then_call_raised_value_error(context, text):
    raised = context.api_run_result['raised']
    assert raised and raised['type'] == 'ValueError' and text in raised['message'], (
        f'Expected a ValueError mentioning {text!r}, got {raised}.\nOutput:\n{context.api_run_output}'
    )


@when('I run BehaveXRunner on passing tests through a relative {argument} entry starting with "-" using "{parallel_processes}" parallel processes')
def when_api_run_dash_prefixed_path(context, argument, parallel_processes):
    work_dir = tempfile.mkdtemp()
    context.add_cleanup(shutil.rmtree, work_dir, ignore_errors=True)
    shutil.copytree(secondary_features_path, os.path.join(work_dir, '-suite'),
                    ignore=shutil.ignore_patterns('__pycache__'))
    script = f"""
import json, os, sys
sys.path.insert(0, {repr(root_project_path)})
os.chdir({repr(work_dir)})
from behavex import BehaveXRunner
result = BehaveXRunner({argument}=['-suite/passing_tests.feature'], parallel_processes={int(parallel_processes)}).run()
""" + _SERIALIZE_RESULT
    _store_result(context, _run_script(script))


@given('Python can cancel queued futures')
def given_python_can_cancel_queued_futures(context):
    if sys.version_info < (3, 9):
        context.scenario.skip(reason='Executor.shutdown(cancel_futures=True) requires Python 3.9')


@then('each on_progress event has the summary total as its total')
def then_progress_events_have_summary_total(context):
    result = context.api_run_result
    totals = [event['total'] for event in result['events']]
    assert totals and all(total == result['summary_total'] for total in totals), (
        f'Expected every event total to be {result["summary_total"]}, got {totals}.\n'
        f'BehaveXRunner output:\n{context.api_run_output}'
    )


@when('I run BehaveXRunner with failing tests and serialize the RunResult with model_dump')
def when_api_run_model_dump(context):
    feature_path = os.path.join(secondary_features_path, 'failing_tests.feature')
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner, RunResult
result = BehaveXRunner(paths=[{repr(feature_path)}], no_report=True).run()
_data = {{
    "dump": json.loads(result.model_dump_json()),
    "schema_properties": sorted(RunResult.model_json_schema(mode='serialization')['properties']),
}}
print("__RESULT__:" + json.dumps(_data))
"""
    _store_result(context, _run_script(script))


@then('the dumped RunResult holds passed False, a summary total of 1 and 1 failed scenario')
def then_dumped_run_result_holds_computed_fields(context):
    result = context.api_run_result
    dump = result['dump']
    assert (dump.get('passed') is False and dump.get('summary', {}).get('total') == 1
            and len(dump.get('failed_scenarios', [])) == 1), (
        f'Unexpected model_dump: {dump}.\nOutput:\n{context.api_run_output}'
    )
    missing = {'passed', 'summary', 'failed_scenarios'} - set(result['schema_properties'])
    assert not missing, f'The serialization schema lacks {missing}: {result["schema_properties"]}'


@when('I run BehaveXRunner with passing tests and call {method}() from its on_progress callback')
def when_api_run_calling_from_progress(context, method):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
{_CAPTURE_RAISED}
_raised = []

def _on_progress(event):
    if not _raised:
        _raised.append(_capture_raised(lambda: BehaveXRunner(paths=[{repr(feature_path)}], no_report=True).{method}()))

result = BehaveXRunner(paths=[{repr(feature_path)}], no_report=True, on_progress=_on_progress).run()
print("__RESULT__:" + json.dumps({{"raised": _raised[0] if _raised else None,
                                  "exit_code": result.exit_code, "summary": result.summary.model_dump()}}))
"""
    _store_result(context, _run_script(script))


@then('the second run raised a RuntimeError mentioning "{text}"')
@then('discover() raised a RuntimeError mentioning "{text}"')
@then('the run started during discover() raised a RuntimeError mentioning "{text}"')
def then_overlapping_call_raised_runtime_error(context, text):
    raised = context.api_run_result['raised']
    assert raised and raised['type'] == 'RuntimeError' and text in raised['message'], (
        f'Expected a RuntimeError mentioning {text!r}, got {raised}.\nOutput:\n{context.api_run_output}'
    )


@when('two threads call run() on passing tests at once, the second while the first validates its arguments')
def when_two_threads_run_at_once(context):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    script = f"""
import json, sys, threading
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner, api
{_CAPTURE_RAISED}
_outcomes = {{}}
_first_validating = threading.Event()
_release_first = threading.Event()
_validate_args = api._validate_args

def _validate_args_holding_the_first(args):
    if not _first_validating.is_set():
        _first_validating.set()
        _release_first.wait(60)
    _validate_args(args)

def _run(name):
    _outcomes[name] = _capture_raised(lambda: BehaveXRunner(paths=[{repr(feature_path)}], no_report=True).run())

api._validate_args = _validate_args_holding_the_first
first = threading.Thread(target=_run, args=('first',))
first.start()
_first_validating.wait(60)
second = threading.Thread(target=_run, args=('second',))
second.start()
second.join(120)
_release_first.set()
first.join(120)
print("__RESULT__:" + json.dumps({{"raised": [r for r in _outcomes.values() if r], "outcome_count": len(_outcomes)}}))
"""
    _store_result(context, _run_script(script))


@then('exactly one of the two runs raised a RuntimeError mentioning "{text}"')
def then_exactly_one_run_raised_runtime_error(context, text):
    result = context.api_run_result
    raised = result['raised']
    assert (result['outcome_count'] == 2 and len(raised) == 1 and raised[0]['type'] == 'RuntimeError'
            and text in raised[0]['message']), (
        f'Expected exactly one RuntimeError mentioning {text!r}, got {result}.\nOutput:\n{context.api_run_output}'
    )


@when('I run the behavex CLI with {input_name}')
def when_cli_run_refused_input(context, input_name):
    paths = _refused_input_kwargs(input_name).get('paths', [])
    script = f"""
import sys
sys.path.insert(0, {repr(root_project_path)})
from behavex.runner import main
sys.argv = ['behavex', *{paths!r}, '--no-report']
main()
"""
    context.cli_proc = _run_script(script)


@then('the CLI printed "{text}", then "Exit code: 1", and exited with code 1')
def then_cli_printed_reason_and_exit_code(context, text):
    proc = context.cli_proc
    lines = proc.stdout.splitlines()
    assert proc.returncode == 1 and lines[-2:-1] and lines[-2].startswith(text) and lines[-1] == 'Exit code: 1', (
        f'Exit code {proc.returncode}.\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}'
    )


@when('I run BehaveXRunner with passing tests while sys.stdout is an io.StringIO')
def when_api_run_with_string_io_stdout(context):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    script = f"""
import io, json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
sys.stdout = io.StringIO()
result = BehaveXRunner(paths=[{repr(feature_path)}], no_report=True).run()
captured, sys.stdout = sys.stdout.getvalue(), sys.__stdout__
print(captured)
""" + _SERIALIZE_RESULT
    _store_result(context, _run_script(script))


@when('I run BehaveXRunner twice in one process on passing tests and record PATH')
def when_api_run_twice_recording_path(context):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    script = f"""
import json, os, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
paths = []
for _ in range(2):
    BehaveXRunner(paths=[{repr(feature_path)}], no_report=True).run()
    paths.append(os.environ['PATH'])
print("__RESULT__:" + json.dumps({{"paths": paths}}))
"""
    _store_result(context, _run_script(script))


@then('PATH is the same after both runs')
def then_path_same_after_both_runs(context):
    first, second = context.api_run_result['paths']
    assert first == second, f'PATH changed between runs:\n{first}\n{second}'


discovery_features_path = os.path.join(api_runner_features_path, 'discovery')
discovery_feature = os.path.relpath(os.path.join(discovery_features_path, 'discovery.feature'), root_project_path)


def _discovery_filter_kwargs(context, filter_name):
    if filter_name == 'an include_paths file line':
        return {'include_paths': [discovery_feature + ':7']}
    if filter_name == 'a Scenario Outline example':
        return {'paths': [discovery_feature + ':23']}
    if filter_name == 'a rerun_failures file':
        failures_file = os.path.join(tempfile.mkdtemp(), 'failing_scenarios.txt')
        context.add_cleanup(shutil.rmtree, os.path.dirname(failures_file), ignore_errors=True)
        with open(failures_file, 'w') as failures:
            failures.write('{0}:3,{0}:22'.format(discovery_feature))
        return {'rerun_failures': failures_file}
    kwargs = {'paths': [discovery_features_path]}
    if filter_name == 'the config tags_to_skip':
        kwargs['config'] = _write_config_file(_make_config_dir(context), 'behavex.cfg',
                                              '[test_run]\ntags_to_skip=SKIP\n')
    else:
        kwargs.update({
            'nothing': {},
            'an included tag': {'tags': ['@SMOKE']},
            'an excluded tag': {'tags': ['~@SMOKE']},
            'name': {'name': 'Outline'},
            'exclude': {'exclude': 'other'},
            'include': {'include': 'other'},
        }[filter_name])
    return kwargs


@when('I call discover() and then run() single-process on the discovery features filtered by {filter_name}')
def when_discover_then_run(context, filter_name):
    kwargs = _discovery_filter_kwargs(context, filter_name)
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner

def scenario_key(filename, line, name, feature, tags):
    return [filename, line, name, feature, sorted(tags)]

if __name__ == '__main__':
    discovered = BehaveXRunner(no_report=True, **{kwargs!r}).discover()
    result = BehaveXRunner(no_report=True, parallel_processes=1, **{kwargs!r}).run()
    print("__RESULT__:" + json.dumps({{
        "discovered": sorted(scenario_key(s.filename, s.line, s.name, s.feature, s.tags) for s in discovered),
        "reported": sorted(scenario_key(s.filename, s.line, s.name, s.feature, s.tags)
                           for f in result.features for s in f.scenarios),
    }}))
"""
    _store_result(context, _run_script(script))


@then('discover() listed the scenarios the run reported, with their features and tags')
def then_discovered_matches_reported(context):
    result = context.api_run_result
    assert result['reported'] and result['discovered'] == result['reported'], (
        f'discover() listed {result["discovered"]}\nbut the run reported {result["reported"]}.\n'
        f'Output:\n{context.api_run_output}'
    )


undefined_steps_features_path = os.path.join(api_runner_features_path, 'undefined_steps')
nested_steps_folders_path = os.path.join(api_runner_features_path, 'nested_steps_folders')
_DISCOVER_FEATURES_PATHS = {
    'the discovery features': [discovery_features_path],
    'the undefined steps features': [undefined_steps_features_path],
    'a top feature and a feature with its own steps folder': [
        os.path.join(nested_steps_folders_path, 'top.feature'),
        os.path.join(nested_steps_folders_path, 'nested', 'nested.feature')],
}

@when('I call {call} on {features} with {folder} as the output folder')
def when_discover_with_output_folder(context, call, features, folder):
    base = tempfile.mkdtemp()
    context.add_cleanup(shutil.rmtree, base, ignore_errors=True)
    output_folder = os.path.join(base, 'output')
    if folder == 'an existing folder holding a marker':
        os.makedirs(output_folder)
        with open(os.path.join(output_folder, 'marker.txt'), 'w') as marker:
            marker.write('marker')
    context.output_folder_before = _folder_snapshot(output_folder)
    context.discovery_output_folder = output_folder
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
scenarios = BehaveXRunner(paths={_DISCOVER_FEATURES_PATHS[features]!r},
                          output_folder={repr(output_folder)}).{call}
print("__RESULT__:" + json.dumps({{"count": len(scenarios),
                                  "with_undefined_steps": sum(1 for s in scenarios if s.undefined_steps)}}))
"""
    context.discovery_proc = _run_script(script)
    _store_result(context, context.discovery_proc)


def _folder_snapshot(folder):
    if not os.path.exists(folder):
        return None
    return sorted((os.path.relpath(os.path.join(root, name), folder), os.path.getmtime(os.path.join(root, name)))
                  for root, dirs, files in os.walk(folder) for name in dirs + files)


@then('discover() listed "{count}" scenarios and printed nothing to stdout')
def then_discover_printed_nothing(context, count):
    proc = context.discovery_proc
    assert context.api_run_result['count'] == int(count) and not _non_result_lines(proc), (
        f'STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}'
    )


@then('the output folder is as it was before discover()')
def then_output_folder_untouched(context):
    after = _folder_snapshot(context.discovery_output_folder)
    assert after == context.output_folder_before, f'Before: {context.output_folder_before}\nAfter: {after}'


@when('I call discover() with {input_name}, then run() on passing tests in the same process')
def when_discover_refused_input_then_run(context, input_name):
    kwargs = _refused_input_kwargs(input_name)
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
{_CAPTURE_RAISED}
if __name__ == '__main__':
    raised = _capture_raised(lambda: BehaveXRunner(no_report=True, **{kwargs!r}).discover())
    result = BehaveXRunner(paths=[{repr(feature_path)}], no_report=True).run()
    print("__RESULT__:" + json.dumps({{"raised": raised, "exit_code": result.exit_code,
                                      "summary": result.summary.model_dump()}}))
"""
    _store_result(context, _run_script(script))


@when('I call discover() on the discovery features and start a run while it explores them')
def when_run_during_discover(context):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner, runner
{_CAPTURE_RAISED}
_raised = []
_explore_features = runner.explore_features

def _explore_starting_a_run(*args, **kwargs):
    runner.explore_features = _explore_features
    _raised.append(_capture_raised(lambda: BehaveXRunner(paths=[{repr(feature_path)}], no_report=True).run()))
    return _explore_features(*args, **kwargs)

if __name__ == '__main__':
    runner.explore_features = _explore_starting_a_run
    BehaveXRunner(paths=[{repr(discovery_features_path)}], no_report=True).discover()
    print("__RESULT__:" + json.dumps({{"raised": _raised[0] if _raised else None}}))
"""
    _store_result(context, _run_script(script))


_RUN_MODES = {
    'in a single process': {},
    'as a dry run': {'dry_run': True},
    'in parallel by feature': {'parallel_processes': 2, 'parallel_scheme': 'feature'},
    'in parallel by scenario': {'parallel_processes': 2, 'parallel_scheme': 'scenario'},
}


_LOAD_RESULTS_CASES = {
    'on the secondary features in a single process': {
        'paths': [secondary_features_path], **_RUN_MODES['in a single process']},
    'on the secondary features in parallel by feature': {
        'paths': [secondary_features_path], **_RUN_MODES['in parallel by feature']},
    'on the secondary features in parallel by scenario': {
        'paths': [secondary_features_path], **_RUN_MODES['in parallel by scenario']},
    'on the secondary features as a dry run': {'paths': [secondary_features_path], **_RUN_MODES['as a dry run']},
    'on the secondary features with the Allure formatter': {
        'paths': [secondary_features_path],
        'formatter': 'behavex.outputs.formatters.allure_behavex_formatter:AllureBehaveXFormatter'},
    'on tests whose before_all_workers hook fails': {
        'paths': [os.path.join(api_runner_features_path, 'failing_before_all_workers')], 'parallel_processes': 2},
    'stopped while before_all_workers runs': {
        'paths': [os.path.join(api_runner_features_path, 'stop_before_workers')], 'parallel_processes': 2,
        'stop_while_before_all_workers_runs': True},
}


@when('I run BehaveXRunner {case} with a configured output folder, then call load_results() on that folder')
def when_run_then_load_results(context, case):
    output_folder = os.path.join('output', f'api_runner_load_{get_random_number(6)}')
    context.add_cleanup(shutil.rmtree, output_folder, ignore_errors=True)
    kwargs = dict(_LOAD_RESULTS_CASES[case], output_folder=output_folder)
    stop_while_before_all_workers_runs = kwargs.pop('stop_while_before_all_workers_runs', False)
    script = f"""
import json, sys, threading
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
{_STOP_WHILE_BEFORE_ALL_WORKERS_RUNS}
if __name__ == '__main__':
    runner = BehaveXRunner(**{kwargs!r})
    if {stop_while_before_all_workers_runs!r}:
        threading.Thread(target=_stop_once_hook_entered, args=(runner,), daemon=True).start()
    returned_by_run = runner.run().model_dump()
    loaded_from_folder = BehaveXRunner.load_results({output_folder!r}).model_dump()
    print("__RESULT__:" + json.dumps({{
        "differing_fields": sorted(field for field in returned_by_run
                                   if returned_by_run[field] != loaded_from_folder[field]),
        "exit_code": loaded_from_folder["exit_code"], "stopped": loaded_from_folder["stopped"],
        "total": loaded_from_folder["summary"]["total"],
    }}))
"""
    _store_result(context, _run_script(script))


@then('load_results() returned the same RunResult as run()')
def then_load_results_matches_run(context):
    differing_fields = context.api_run_result['differing_fields']
    assert not differing_fields, (
        f'load_results() differs from run() in {differing_fields}.\nOutput:\n{context.api_run_output}'
    )


@then('the loaded RunResult has exit_code "{exit_code}", stopped "{stopped}" and "{total}" scenarios')
def then_loaded_run_result_has_exit_code_stopped_and_total(context, exit_code, stopped, total):
    loaded = context.api_run_result
    expected = {'exit_code': int(exit_code), 'stopped': stopped == 'True', 'total': int(total)}
    actual = {key: loaded[key] for key in expected}
    assert actual == expected, f'Expected {expected}, got {actual}.\nOutput:\n{context.api_run_output}'


@when('I call load_results() on {folder}')
def when_load_results_on_folder(context, folder):
    output_folder = os.path.join('output', f'api_runner_load_{get_random_number(6)}')
    context.add_cleanup(shutil.rmtree, output_folder, ignore_errors=True)
    folder_setup_code = {
        'the output folder of a no_report run':
            f'BehaveXRunner(paths=[{os.path.join(secondary_features_path, "passing_tests.feature")!r}], '
            f'output_folder={output_folder!r}, no_report=True).run()',
        'a folder that does not exist': 'pass',
        'a folder written by BehaveX 4.6':
            f'os.makedirs({output_folder!r})\n    '
            f'json.dump({{"status": "passed"}}, open(os.path.join({output_folder!r}, "overall_status.json"), "w"))',
        "a passed run's folder without report.json":
            f'BehaveXRunner(paths=[{os.path.join(secondary_features_path, "passing_tests.feature")!r}], '
            f'output_folder={output_folder!r}).run()\n    '
            f'os.remove(os.path.join({output_folder!r}, "report.json"))',
        'a folder whose report.json has no features':
            f'BehaveXRunner(paths=[{os.path.join(secondary_features_path, "passing_tests.feature")!r}], '
            f'output_folder={output_folder!r}).run()\n    '
            f'json.dump({{}}, open(os.path.join({output_folder!r}, "report.json"), "w"))',
    }[folder]
    script = f"""
import json, os, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
{_CAPTURE_RAISED}
if __name__ == '__main__':
    {folder_setup_code}
    raised = _capture_raised(lambda: BehaveXRunner.load_results({output_folder!r}))
    print("__RESULT__:" + json.dumps({{"raised": raised}}))
"""
    _store_result(context, _run_script(script))


@when('I run behavex from the CLI on the secondary features, then call load_results() on its output folder')
def when_cli_run_then_load_results(context):
    output_folder = os.path.join('output', f'api_runner_load_cli_{get_random_number(6)}')
    context.add_cleanup(shutil.rmtree, output_folder, ignore_errors=True)
    execute_command(context, ['behavex', secondary_features_path, '-o', output_folder],
                    env=_clean_child_env(), cwd=root_project_path)
    context.cli_exit_code = context.result.returncode
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
loaded = BehaveXRunner.load_results({output_folder!r})
print("__RESULT__:" + json.dumps({{"exit_code": loaded.exit_code, "run_id": loaded.run_id,
                                  "total": loaded.summary.total}}))
"""
    _store_result(context, _run_script(script))


@then('the loaded RunResult has the CLI\'s exit code, a run_id and "{total}" scenarios')
def then_loaded_cli_run_result(context, total):
    loaded = context.api_run_result
    assert loaded['exit_code'] == context.cli_exit_code and loaded['run_id'] and loaded['total'] == int(total), (
        f'Expected exit_code {context.cli_exit_code}, a run_id and {total} scenarios, got {loaded}.\n'
        f'Output:\n{context.api_run_output}'
    )


@when('I call discover(check_steps=True), then run BehaveXRunner {mode}, on {features}')
def when_discover_check_steps_then_run(context, mode, features):
    kwargs = dict(_RUN_MODES[mode], paths=_DISCOVER_FEATURES_PATHS[features])
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner

if __name__ == '__main__':
    discovered = BehaveXRunner(**{kwargs!r}).discover(check_steps=True)
    result = BehaveXRunner(no_report=True, **{kwargs!r}).run()
    # discover() lists 'Keyword name'; the run reports each step's name and status
    print("__RESULT__:" + json.dumps({{
        "discovered": {{scenario.name: sorted(text.split(' ', 1)[1] for text in scenario.undefined_steps)
                        for scenario in discovered}},
        "reported": {{scenario.name: sorted(step.name for step in scenario.background.steps + scenario.steps
                                            if step.status in ('undefined', 'untested_undefined'))
                      for feature in result.features for scenario in feature.scenarios}},
    }}))
"""
    _store_result(context, _run_script(script))


@then('discover() listed the undefined steps the run reported, "{count}" of them')
def then_discover_listed_reported_undefined_steps(context, count):
    discovered = context.api_run_result['discovered']
    reported = context.api_run_result['reported']
    discovered_count = sum(len(steps) for steps in discovered.values())
    assert discovered == reported and discovered_count == int(count), (
        f'Expected {count} undefined steps, as the run reported.\nDiscovered: {discovered}\n'
        f'Reported: {reported}\nOutput:\n{context.api_run_output}'
    )


@then('"{count}" of the listed scenarios have undefined steps')
def then_listed_scenarios_with_undefined_steps(context, count):
    with_undefined_steps = context.api_run_result['with_undefined_steps']
    assert with_undefined_steps == int(count), (
        f'Expected {count} scenarios with undefined steps, got {with_undefined_steps}'
    )


@when('I call discover(check_steps=True) on features whose {problem}')
def when_discover_check_steps_on_broken_features(context, problem):
    if problem == 'step module fails to import':
        features_path = os.path.join(api_runner_features_path, 'broken_step_module')
    else:
        # No folder above a temporary one holds a steps folder
        features_path = tempfile.mkdtemp()
        context.add_cleanup(shutil.rmtree, features_path, ignore_errors=True)
        with open(os.path.join(features_path, 'no_steps.feature'), 'w') as feature_file:
            feature_file.write('Feature: No Steps\n\n  Scenario: Has no steps folder\n    Given a passing step\n')
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
{_CAPTURE_RAISED}
if __name__ == '__main__':
    raised = _capture_raised(lambda: BehaveXRunner(paths=[{features_path!r}]).discover(check_steps=True))
    print("__RESULT__:" + json.dumps({{"raised": raised}}))
"""
    _store_result(context, _run_script(script))


@when('I run BehaveXRunner on the undefined steps features, then call discover(check_steps=True) on the top feature, '
      'in the same process')
def when_run_then_discover_check_steps(context):
    top_feature_path = os.path.join(nested_steps_folders_path, 'top.feature')
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner

if __name__ == '__main__':
    BehaveXRunner(paths=[{undefined_steps_features_path!r}], no_report=True).run()
    discovered = BehaveXRunner(paths=[{top_feature_path!r}]).discover(check_steps=True)
    print("__RESULT__:" + json.dumps({{"undefined_steps": {{s.name: s.undefined_steps for s in discovered}}}}))
"""
    _store_result(context, _run_script(script))


@then('discover() listed "{count}" undefined steps for the scenario "{name}"')
def then_discover_listed_undefined_steps_for_scenario(context, count, name):
    undefined_steps = context.api_run_result['undefined_steps']
    assert len(undefined_steps[name]) == int(count), (
        f'Expected {count} undefined steps for "{name}", got {undefined_steps}'
    )


@when('I run BehaveXRunner {mode} on the undefined steps features, then on the top feature, in the same process')
def when_run_two_suites_in_one_process(context, mode):
    top_feature_path = os.path.join(nested_steps_folders_path, 'top.feature')
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner

if __name__ == '__main__':
    BehaveXRunner(paths=[{undefined_steps_features_path!r}], no_report=True, **{_RUN_MODES[mode]!r}).run()
    result = BehaveXRunner(paths=[{top_feature_path!r}], no_report=True, **{_RUN_MODES[mode]!r}).run()
    print("__RESULT__:" + json.dumps({{"statuses": {{s.name: s.status for f in result.features
                                                    for s in f.scenarios}}}}))
"""
    _store_result(context, _run_script(script))


@then('the scenario "{name}" ended with behave\'s error status in the second run')
def then_scenario_ended_with_error_status(context, name):
    statuses = context.api_run_result['statuses']
    assert statuses.get(name) == BEHAVE_ERROR_STATUS, (
        f'Expected "{name}" to end as {BEHAVE_ERROR_STATUS}, got {statuses}.\nOutput:\n{context.api_run_output}'
    )


@when('I run BehaveXRunner in a single process on passing tests with sys.stdout redirected')
def when_run_with_stdout_redirected(context):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    script = f"""
import contextlib, io, json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner

if __name__ == '__main__':
    redirected = io.StringIO()
    with contextlib.redirect_stdout(redirected):
        BehaveXRunner(paths=[{feature_path!r}], no_report=True).run()
    print("__RESULT__:" + json.dumps({{"redirected": redirected.getvalue()}}))
"""
    context.redirected_run_proc = _run_script(script)
    _store_result(context, context.redirected_run_proc)


@then('the redirected sys.stdout received behave\'s summary and the process stdout did not')
def then_redirected_stdout_received_summary(context):
    process_stdout = '\n'.join(_non_result_lines(context.redirected_run_proc))
    assert 'scenarios passed' in context.api_run_result['redirected'] and 'scenarios passed' not in process_stdout, (
        f'Redirected:\n{context.api_run_result["redirected"]}\nProcess stdout:\n{process_stdout}'
    )


@when('I run BehaveXRunner in a single process on passing tests, noting the output that had arrived at each '
      'on_progress event')
def when_run_noting_output_at_each_event(context):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    script = f"""
import contextlib, io, json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner

if __name__ == '__main__':
    redirected = io.StringIO()
    output_at_events = []
    with contextlib.redirect_stdout(redirected):
        BehaveXRunner(paths=[{feature_path!r}], no_report=True,
                      on_progress=lambda event: output_at_events.append(redirected.getvalue())).run()
    print("__RESULT__:" + json.dumps({{"output_at_events": output_at_events}}))
"""
    _store_result(context, _run_script(script))


@then('the first on_progress event arrived before behave printed its summary')
def then_first_event_arrived_before_summary(context):
    output_at_events = context.api_run_result['output_at_events']
    # behave's summary line, printed once every scenario has run
    assert output_at_events and 'scenarios passed' not in output_at_events[0], (
        f'Expected the first event before behave\'s summary, got the output:\n{output_at_events[:1]}'
    )


serial_suites_path = os.path.join(api_runner_features_path, 'serial_suites')


@when('I run BehaveXRunner in parallel by {scheme} on the first @SERIAL suite, then on the second, in the same process')
def when_run_two_serial_suites_in_one_process(context, scheme):
    run_mode = _RUN_MODES[f'in parallel by {scheme}']
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner

if __name__ == '__main__':
    BehaveXRunner(paths=[{os.path.join(serial_suites_path, 'first')!r}], no_report=True, **{run_mode!r}).run()
    result = BehaveXRunner(paths=[{os.path.join(serial_suites_path, 'second')!r}], no_report=True,
                           **{run_mode!r}).run()
    print("__RESULT__:" + json.dumps({{"statuses": {{s.name: s.status for f in result.features
                                                    for s in f.scenarios}}}}))
"""
    _store_result(context, _run_script(script))


_SERIAL_STOP_RACES = {
    # stop() lands between the serial loop's stop check and its submission
    'stop() comes right after the stop check': """
_check_stop_requested = runner._mark_run_stopped_if_requested

def _check_then_stop():
    stop_was_requested = _check_stop_requested()
    if not stop_was_requested:
        behavex_runner.stop()
    return stop_was_requested

runner._mark_run_stopped_if_requested = _check_then_stop
""",
    # stop()'s cancel_futures cancels the queued work before a worker picks it up
    'the submitted @SERIAL work is cancelled before it starts': """
from concurrent.futures import Future

def _submit_cancelled(*args, **kwargs):
    cancelled_future = Future()
    cancelled_future.cancel()
    return cancelled_future

runner._submit_unless_stopped = _submit_cancelled
""",
}


@when('I run BehaveXRunner in parallel by {scheme} on the second @SERIAL suite, and {race}')
def when_stop_races_serial_work(context, scheme, race):
    run_mode = _RUN_MODES[f'in parallel by {scheme}']
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner, runner
{_CAPTURE_RAISED}
if __name__ == '__main__':
    behavex_runner = BehaveXRunner(paths=[{os.path.join(serial_suites_path, 'second')!r}], no_report=True, **{run_mode!r})
{textwrap.indent(_SERIAL_STOP_RACES[race], '    ')}
    results = []
    raised = _capture_raised(lambda: results.append(behavex_runner.run()))
    print("__RESULT__:" + json.dumps({{"raised": raised, "stopped": results[0].stopped if results else None}}))
"""
    _store_result(context, _run_script(script))


@then('the run raised no exception and the RunResult stopped is "{stopped}"')
def then_no_exception_and_stopped(context, stopped):
    result = context.api_run_result
    assert result['raised'] is None and result['stopped'] == (stopped == 'True'), (
        f'Expected no exception and stopped={stopped}, got {result}.\nOutput:\n{context.api_run_output}'
    )


@when('I run BehaveXRunner in a single process on a step that runs a subprocess writing to sys.stdout')
def when_run_step_writing_to_stdout_descriptor(context):
    _run_via_api(context, os.path.join(api_runner_features_path, 'stdout_file_descriptor'))


_CTRL_C_TARGETS = {
    'the whole process group, as a terminal does': 'os.killpg(os.getpgid(0), signal.SIGINT)',
    'the host process alone, as Jupyter does': 'os.kill(os.getpid(), signal.SIGINT)',
}


_CTRL_C_PRESS_GAPS = {'once': [], 'twice': ['time.sleep(0.1)']}


@when('I run BehaveXRunner in a single process on slow scenarios and send Ctrl+C {presses} to {target} once the first one finishes')
def when_run_and_send_ctrl_c(context, presses, target):
    ctrl_c_presses_code = '; '.join([_CTRL_C_TARGETS[target]] + [
        f'{gap}; {_CTRL_C_TARGETS[target]}' for gap in _CTRL_C_PRESS_GAPS[presses]])
    script = f"""
import json, multiprocessing, os, signal, sys, time
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
{_CAPTURE_RAISED}
pressed = []

def _press_ctrl_c_on_first_event(event):
    if not pressed:
        pressed.append(True)
        {ctrl_c_presses_code}

if __name__ == '__main__':
    # Python leaves Ctrl+C ignored when its parent ignored it, as the suite's runner may
    signal.signal(signal.SIGINT, signal.default_int_handler)
    host_child = multiprocessing.Process(target=time.sleep, args=(120,))
    host_child.start()
    results = []
    raised = _capture_raised(lambda: results.append(BehaveXRunner(
        paths=[{os.path.join(api_runner_features_path, 'slow_scenarios')!r}], no_report=True,
        on_progress=_press_ctrl_c_on_first_event).run()))
    host_child_alive = host_child.is_alive()
    host_child.terminate()
    statuses = {{s.name: s.status for f in results[0].features for s in f.scenarios}} if results else {{}}
    print("__RESULT__:" + json.dumps({{"raised": raised, "statuses": statuses, "host_child_alive": host_child_alive}}))
"""
    # A process group of its own, so the Ctrl+C reaches only this run
    proc = subprocess.run([sys.executable, '-c', script], capture_output=True, text=True, cwd=root_project_path,
                          env=_clean_child_env(), timeout=120, start_new_session=True)
    _store_result(context, proc)


@when('I run BehaveXRunner in parallel on slow scenarios, call stop() and send Ctrl+C to the host process once the first one finishes')
def when_run_in_parallel_stop_and_send_ctrl_c(context):
    script = f"""
import json, multiprocessing, os, signal, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
{_CAPTURE_RAISED}
pressed = []

def _stop_and_press_ctrl_c_on_first_event(event):
    if not pressed:
        pressed.append(True)
        runner.stop()
        os.kill(os.getpid(), signal.SIGINT)

if __name__ == '__main__':
    # Python leaves Ctrl+C ignored when its parent ignored it, as the suite's runner may
    signal.signal(signal.SIGINT, signal.default_int_handler)
    runner = BehaveXRunner(paths=[{os.path.join(api_runner_features_path, 'slow_scenarios')!r}], no_report=True,
                           parallel_processes=2, parallel_scheme='scenario',
                           on_progress=_stop_and_press_ctrl_c_on_first_event)
    raised = _capture_raised(runner.run)
    print("__RESULT__:" + json.dumps({{"raised": raised, "live_children": len(multiprocessing.active_children())}}))
"""
    proc = subprocess.run([sys.executable, '-c', script], capture_output=True, text=True, cwd=root_project_path,
                          env=_clean_child_env(), timeout=120, start_new_session=True)
    _store_result(context, proc)


@then('the run raised no exception and none of its processes is still running')
def then_no_exception_and_no_live_children(context):
    result = context.api_run_result
    assert result['raised'] is None and result['live_children'] == 0, (
        f'Got {result}.\nOutput:\n{context.api_run_output}'
    )


@then('the run raised no exception and the first scenario passed while the others did not run')
def then_partial_results_after_ctrl_c(context):
    result = context.api_run_result
    statuses = result['statuses']
    assert result['raised'] is None and statuses.get('Slow scenario 01') == 'passed' and statuses.get(
        'Slow scenario 03') not in (None, 'passed'), f'Got {result}.\nOutput:\n{context.api_run_output}'


@then('the run raised no exception and a multiprocessing child the host started itself is still running')
def then_no_exception_and_host_child_still_running(context):
    result = context.api_run_result
    assert result['raised'] is None and result['host_child_alive'] is True, (
        f'Got {context.api_run_result}.\nOutput:\n{context.api_run_output}'
    )


@when('I run BehaveXRunner {mode} on a @SERIAL scenario that kills its worker')
def when_run_with_crashing_worker(context, mode):
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
{_CAPTURE_RAISED}
if __name__ == '__main__':
    results = []
    raised = _capture_raised(lambda: results.append(BehaveXRunner(
        paths=[{os.path.join(api_runner_features_path, 'crashing_worker')!r}], no_report=True,
        **{_RUN_MODES[mode]!r}).run()))
    print("__RESULT__:" + json.dumps({{"raised": raised, "exit_code": results[0].exit_code if results else None,
                                      "stopped": results[0].stopped if results else None}}))
"""
    _store_result(context, _run_script(script))


@then('the run raised no exception, the RunResult exit_code is "{exit_code}" and it was not stopped')
def then_no_exception_exit_code_not_stopped(context, exit_code):
    result = context.api_run_result
    assert result['raised'] is None and result['exit_code'] == int(exit_code) and result['stopped'] is False, (
        f'Expected no exception, exit_code {exit_code} and not stopped, got {result}.\n'
        f'Output:\n{context.api_run_output}'
    )


@when('I run BehaveXRunner {mode} after the host application configured its own logging')
def when_run_after_host_configured_logging(context, mode):
    script = f"""
import io, json, logging, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
{_CAPTURE_RAISED}
if __name__ == '__main__':
    host_log = io.StringIO()
    host_handler = logging.StreamHandler(host_log)
    logging.getLogger().addHandler(host_handler)
    host_logger = logging.getLogger('host_application')
    host_logger.setLevel(logging.INFO)
    raised = _capture_raised(lambda: BehaveXRunner(
        paths=[{os.path.join(secondary_features_path, 'passing_tests.feature')!r}], no_report=True,
        **{_RUN_MODES[mode]!r}).run())
    host_logger.info('logged after the run')
    print("__RESULT__:" + json.dumps({{"raised": raised, "root_handlers_kept": logging.getLogger().handlers == [host_handler],
                                      "host_log": host_log.getvalue()}}))
"""
    _store_result(context, _run_script(script))


@then('the run raised no exception and the host application\'s logging still works as it configured it')
def then_host_logging_untouched(context):
    result = context.api_run_result
    assert result['raised'] is None and result['root_handlers_kept'] and 'logged after the run' in result['host_log'], (
        f'Got {result}.\nOutput:\n{context.api_run_output}'
    )

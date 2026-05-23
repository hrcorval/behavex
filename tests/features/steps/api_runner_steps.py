import json
import os
import random
import re
import shutil
import subprocess
import sys
from typing import List, Optional

from behave import then, when

root_project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
secondary_features_path = os.path.join(root_project_path, 'tests', 'features', 'secondary_features')

# Env vars injected by the parent behavex process that must not leak into the
# child subprocess, as they would override the child's own config and paths.
_PARENT_BEHAVEX_ENV_VARS = frozenset({
    'CONFIG', 'OUTPUT', 'TAGS', 'PARALLEL_SCHEME',
    'PARALLEL_PROCESSES', 'FEATURES_PATH', 'TEMP', 'LOGS', 'LOGGING_LEVEL',
})


def _clean_child_env() -> dict:
    return {k: v for k, v in os.environ.items() if k not in _PARENT_BEHAVEX_ENV_VARS}


def _random_suffix(n: int = 6) -> str:
    return str(random.randint(10 ** (n - 1), 10**n - 1))


# Shared serialization snippet appended to every subprocess script.
# Serializes all model fields needed by Then steps into a single __RESULT__ line.
_SERIALIZE_RESULT = """
_s = result.summary
_data = {
    "run_id": result.run_id,
    "exit_code": result.exit_code,
    "passed": result.passed,
    "output_folder": result.output_folder,
    "feature_count": len(result.features),
    "features": [
        {"name": f.name, "status": f.status, "scenario_count": len(f.scenarios)}
        for f in result.features
    ],
    "summary": {"total": _s.total, "passed": _s.passed, "failed": _s.failed, "skipped": _s.skipped},
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


def _run_script(script: str) -> subprocess.CompletedProcess:
    """Run a Python script in a subprocess using the same Python interpreter."""
    return subprocess.run(
        [sys.executable, '-c', script],
        capture_output=True,
        text=True,
        cwd=root_project_path,
        env=_clean_child_env(),
        timeout=120,
    )


def _parse_result(proc: subprocess.CompletedProcess) -> dict:
    """Extract the __RESULT__ JSON line from subprocess stdout."""
    for line in proc.stdout.splitlines():
        if line.startswith('__RESULT__:'):
            return json.loads(line[len('__RESULT__:'):])
    raise AssertionError(
        f'BehaveXRunner subprocess did not emit a result.\n'
        f'STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}'
    )


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
    """Invoke BehaveXRunner in a subprocess and store the result in context.

    extra_kwargs are passed through as BehaveXRunner constructor arguments.
    String values are automatically repr'd so they are valid Python literals
    when interpolated into the subprocess script.
    """
    def _as_py_literal(v):
        return repr(v)

    kwargs_lines = ''.join(
        f'    {k}={_as_py_literal(v)},\n' for k, v in extra_kwargs.items()
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
    output_folder = os.path.join('output', f'api_runner_{_random_suffix()}')
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
    output_folder = os.path.join('output', f'api_runner_no_report_{_random_suffix()}')
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
    output_folder = os.path.join('output', f'api_runner_fail_{_random_suffix()}')
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


@then('I should see "{text}" in the BehaveXRunner output')
def then_output_contains(context, text):
    assert text in context.api_run_output, (
        f'Expected to find "{text}" in BehaveXRunner output.\n'
        f'Full output:\n{context.api_run_output}'
    )


@then('the RunResult output_folder matches the configured output folder')
def then_output_folder_matches(context):
    actual = context.api_run_result['output_folder']
    expected = context.configured_output_folder
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
    """Run a Python snippet in a subprocess with pydantic blocked."""
    script = _BLOCK_PYDANTIC_SCRIPT.format(body=script_body)
    return subprocess.run(
        ['uv', 'run', 'python', '-c', script],
        capture_output=True,
        text=True,
        cwd=root_project_path,
        env=_clean_child_env(),
        timeout=60,
    )


@when('I run the behavex CLI without pydantic available')
def when_cli_without_pydantic(context):
    # The CLI entry point is runner.main() — it must not require pydantic
    proc = _run_without_pydantic(f"""
import sys
sys.path.insert(0, {repr(root_project_path)})
from behavex.runner import main
# Patch sys.argv so main() gets --help and exits cleanly without running tests
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
    assert 'EXIT:0' in proc.stdout or 'BehaveX' in output, (
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
# Model assertion steps (sub-etapa 2)
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
    context.api_run_result = _parse_result(proc)
    context.api_run_output = proc.stdout


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
# _build_args coverage — name, stop, define, logging_level
# ─────────────────────────────────────────────────────────────────────────────

@when('I run BehaveXRunner with passing tests filtered by name "{name}"')
def when_api_run_with_name(context, name):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    _run_via_api(context, feature_path, name=name)


@when('I run BehaveXRunner with failing tests and stop enabled')
def when_api_run_stop(context):
    feature_path = os.path.join(secondary_features_path, 'failing_tests.feature')
    _run_via_api(context, feature_path, stop=True)


@when('I run BehaveXRunner with userdata tests and define "{userdata}"')
def when_api_run_with_define(context, userdata):
    feature_path = os.path.join(secondary_features_path, 'userdata_tests.feature')
    _run_via_api(context, feature_path, tags=['@USERDATA'], define=[userdata])


@when('I run BehaveXRunner with passing tests and logging_level "{level}"')
def when_api_run_with_logging_level(context, level):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    _run_via_api(context, feature_path, logging_level=level)


# ─────────────────────────────────────────────────────────────────────────────
# on_progress callback steps (015, 016, 017)
# ─────────────────────────────────────────────────────────────────────────────

_SERIALIZE_PROGRESS = """
_data = {
    "exit_code": result.exit_code,
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
        "completed": event.completed,
    })
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
) -> None:
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
{callback_snippet}
result = BehaveXRunner(
    paths=[{repr(feature_path)}],
    no_report=True,
    parallel_processes={parallel_processes},
    parallel_scheme={repr(parallel_scheme)},
    on_progress=_on_progress,
).run()
""" + serialize_snippet
    proc = _run_script(script)
    context.api_run_result = _parse_result(proc)
    context.api_run_output = proc.stdout


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


@when('I run BehaveXRunner with passing tests and an on_progress callback that always raises')
def when_api_run_with_raising_progress_callback(context):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    _run_with_progress_callback(
        context,
        feature_path,
        callback_snippet=_RAISING_PROGRESS_CALLBACK,
        serialize_snippet=_SERIALIZE_EXIT_CODE_ONLY,
    )


@then('the on_progress callback was called at least "{expected}" time')
@then('the on_progress callback was called at least "{expected}" times')
def then_progress_callback_called_at_least(context, expected):
    actual = context.api_run_result['event_count']
    assert actual >= int(expected), (
        f'Expected on_progress to be called at least {expected} time(s), got {actual}.\n'
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


@then('the completed counter in on_progress events is strictly increasing')
def then_progress_completed_strictly_increasing(context):
    events = context.api_run_result['events']
    assert events, 'No on_progress events were captured.'
    completed_values = [e['completed'] for e in events]
    for i in range(1, len(completed_values)):
        assert completed_values[i] > completed_values[i - 1], (
            f'completed counter is not strictly increasing at index {i}: {completed_values}'
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
# stop() steps (022, 023, 024)
# ─────────────────────────────────────────────────────────────────────────────

_SERIALIZE_STOP = """
_data = {"exit_code": result.exit_code, "exception": None}
print("__RESULT__:" + json.dumps(_data))
"""

_SERIALIZE_STOP_NO_RUN = """
_data = {"exit_code": 0, "exception": None}
print("__RESULT__:" + json.dumps(_data))
"""


def _run_stop_script(script: str) -> None:
    proc = _run_script(script)
    for line in proc.stdout.splitlines():
        if line.startswith('__RESULT__:'):
            context_result = json.loads(line[len('__RESULT__:'):])
            return proc, context_result
    raise AssertionError(
        f'stop() subprocess did not emit a result.\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}'
    )


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
    context.api_run_result = _parse_result(proc)
    context.api_run_output = proc.stdout


@when('I run BehaveXRunner with passing tests and call stop() from a background thread')
def when_run_with_stop_non_parallel(context):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    script = f"""
import json, sys, threading
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner

runner = BehaveXRunner(paths=[{repr(feature_path)}], no_report=True)
exception = None

# stop() is called from a background thread 0.5s after run() starts.
# In non-parallel mode there is no executor, so stop() is a no-op.
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
    context.api_run_result = _parse_result(proc)
    context.api_run_output = proc.stdout


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

# stop() is called from a background thread mid-run.
# All futures are already submitted upfront, so stop() acts as a no-op
# on already-queued work, but must not raise or deadlock.
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
    context.api_run_result = _parse_result(proc)
    context.api_run_output = proc.stdout


@then('no exception was raised')
def then_no_exception(context):
    exception = context.api_run_result.get('exception')
    assert exception is None, (
        f'Expected no exception but got: {exception}\n'
        f'BehaveXRunner output:\n{context.api_run_output}'
    )

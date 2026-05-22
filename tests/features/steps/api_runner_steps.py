import json
import os
import random
import shutil
import subprocess

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


def _run_via_api(
    context,
    feature_path: str,
    tags: list | None = None,
    output_folder: str = '',
    no_report: bool = True,
) -> None:
    """Invoke BehaveXRunner in a subprocess and store the result in context."""
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
result = BehaveXRunner(
    paths=[{repr(feature_path)}],
    tags={repr(tags or [])},
    output_folder={repr(output_folder)},
    no_report={no_report},
).run()
""" + _SERIALIZE_RESULT
    proc = subprocess.run(
        ['uv', 'run', 'python', '-c', script],
        capture_output=True,
        text=True,
        cwd=root_project_path,
        env=_clean_child_env(),
    )

    api_result = None
    for line in proc.stdout.splitlines():
        if line.startswith('__RESULT__:'):
            api_result = json.loads(line[len('__RESULT__:'):])

    assert api_result is not None, (
        f'BehaveXRunner subprocess did not emit a result.\n'
        f'STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}'
    )

    context.api_run_result = api_result
    context.api_run_output = proc.stdout


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
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
result = BehaveXRunner(
    paths=[{repr(feature_path)}],
    parallel_processes={int(parallel_processes)},
    parallel_scheme={repr(parallel_scheme)},
    no_report=True,
).run()
""" + _SERIALIZE_RESULT
    proc = subprocess.run(
        ['uv', 'run', 'python', '-c', script],
        capture_output=True,
        text=True,
        cwd=root_project_path,
        env=_clean_child_env(),
    )
    api_result = None
    for line in proc.stdout.splitlines():
        if line.startswith('__RESULT__:'):
            api_result = json.loads(line[len('__RESULT__:'):])
    assert api_result is not None, (
        f'BehaveXRunner subprocess did not emit a result.\n'
        f'STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}'
    )
    context.api_run_result = api_result
    context.api_run_output = proc.stdout


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
    script = f"""
import json, sys
sys.path.insert(0, {repr(root_project_path)})
from behavex import BehaveXRunner
result = BehaveXRunner(
    paths=[{repr(feature_path)}],
    dry_run=True,
    no_report=True,
).run()
""" + _SERIALIZE_RESULT
    proc = subprocess.run(
        ['uv', 'run', 'python', '-c', script],
        capture_output=True,
        text=True,
        cwd=root_project_path,
        env=_clean_child_env(),
    )
    api_result = None
    for line in proc.stdout.splitlines():
        if line.startswith('__RESULT__:'):
            api_result = json.loads(line[len('__RESULT__:'):])
    assert api_result is not None, (
        f'Subprocess did not emit a result.\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}'
    )
    context.api_run_result = api_result
    context.api_run_output = proc.stdout


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
    import re
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
print("__RESULT__:" + json.dumps({{"run_id_1": result1.run_id, "run_id_2": result2.run_id}}))
"""
    proc = subprocess.run(
        ['uv', 'run', 'python', '-c', script],
        capture_output=True,
        text=True,
        cwd=root_project_path,
        env=_clean_child_env(),
    )
    api_result = None
    for line in proc.stdout.splitlines():
        if line.startswith('__RESULT__:'):
            api_result = json.loads(line[len('__RESULT__:'):])
    assert api_result is not None, (
        f'Subprocess did not emit a result.\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}'
    )
    context.api_run_result = api_result
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

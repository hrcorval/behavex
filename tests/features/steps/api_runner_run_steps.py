import os
import re
import shutil
import subprocess

from api_runner_support import (
    _CAPTURE_RAISED,
    BEHAVE_ERROR_STATUS,
    _run_script,
    _run_via_api,
    _store_result,
    api_runner_features_path,
    root_project_path,
    secondary_features_path,
)
from behave import then, when
from execution_steps import get_unique_suffix

_BLOCK_PYDANTIC_SCRIPT = """
import sys
# Block pydantic before any behavex import so the ImportError path is exercised
sys.modules['pydantic'] = None
{body}
"""


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
    output_folder = os.path.join('output', f'api_runner_{get_unique_suffix()}')
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
    output_folder = os.path.join('output', f'api_runner_no_report_{get_unique_suffix()}')
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
    output_folder = os.path.join('output', f'api_runner_fail_{get_unique_suffix()}')
    context.configured_output_folder = output_folder
    context.add_cleanup(shutil.rmtree, output_folder, ignore_errors=True)
    _run_via_api(context, feature_path, output_folder=output_folder, no_report=False)


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


def _run_without_pydantic(script_body: str) -> subprocess.CompletedProcess:
    """Run a Python snippet in a subprocess with pydantic blocked via sys.modules."""
    script = _BLOCK_PYDANTIC_SCRIPT.format(body=script_body)
    return _run_script(script, import_runner=False, timeout=60)


@when('I run the behavex CLI without pydantic available')
def when_cli_without_pydantic(context):
    proc = _run_without_pydantic("""
import sys
from behavex.runner import main
sys.argv = ['behavex', '--help']
try:
    main()
except SystemExit as e:
    print(f'EXIT:{e.code}')
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
    proc = _run_without_pydantic("""
import sys
try:
    from behavex.api import BehaveXRunner
    print('NO_ERROR')
except ImportError as e:
    print(f'IMPORT_ERROR:{e}')
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


@then('the RunResult has at least "{expected}" feature')
def then_feature_count_at_least(context, expected):
    actual = context.api_run_result['feature_count']
    assert actual >= int(expected), (
        f'Expected at least {expected} feature(s), got {actual}.'
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


@then('the RunResult summary has no failed scenarios')
def then_summary_no_failures(context):
    actual = context.api_run_result['summary']['failed']
    assert actual == 0, f'Expected summary.failed=0, got {actual}.'


@then('the RunResult summary has no skipped scenarios')
def then_summary_no_skipped(context):
    actual = context.api_run_result['summary']['skipped']
    assert actual == 0, f'Expected summary.skipped=0, got {actual}.'


@then('the RunResult has "{expected}" failed scenario')
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
from behavex.runner import main
sys.argv = ['behavex', {repr(feature_path)}, '--no-report']
try:
    main()
except SystemExit:
    pass
print("__RESULT__:" + json.dumps({{"modules": [m for m in ('behavex.models', 'pydantic') if m in sys.modules]}}))
"""
    _store_result(context, _run_script(script, import_runner=False))


@then('the CLI run loaded neither "{module_a}" nor "{module_b}"')
def then_cli_loaded_neither(context, module_a, module_b):
    loaded = context.api_run_result['modules']
    assert module_a not in loaded and module_b not in loaded, (
        f'The CLI imported {loaded}.\nOutput:\n{context.api_run_output}'
    )


@when('I run BehaveXRunner with a feature whose background step is undefined')
def when_api_run_undefined_background(context):
    _run_via_api(
        context,
        os.path.join(root_project_path, 'tests', 'features', 'fixtures', 'background_features', 'undefined_background_tests.feature'),
    )


@when('I run BehaveXRunner with a crashing test using "{parallel_processes}" parallel processes and "{parallel_scheme}" parallel scheme')
def when_api_run_crashing_parallel(context, parallel_processes, parallel_scheme):
    _run_via_api(
        context,
        os.path.join(root_project_path, 'tests', 'features', 'fixtures', 'crashing_features', 'crashing_tests.feature'),
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


@then('run() raised a ValueError mentioning "{text}"')
@then('discover() raised a ValueError mentioning "{text}"')
@then('load_results() raised a ValueError mentioning "{text}"')
def then_call_raised_value_error(context, text):
    raised = context.api_run_result['raised']
    assert raised and raised['type'] == 'ValueError' and text in raised['message'], (
        f'Expected a ValueError mentioning {text!r}, got {raised}.\nOutput:\n{context.api_run_output}'
    )


@when('I run BehaveXRunner with failing tests and serialize the RunResult with model_dump')
def when_api_run_model_dump(context):
    feature_path = os.path.join(secondary_features_path, 'failing_tests.feature')
    script = f"""
import json, sys
from behavex import RunResult
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

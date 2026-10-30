import os
import shutil

from api_runner_support import (
    _CAPTURE_RAISED,
    _RUN_MODES,
    _SERIALIZE_RESULT,
    BEHAVE_ERROR_STATUS,
    _non_result_lines,
    _run_script,
    _run_via_api,
    _store_result,
    api_runner_features_path,
    nested_steps_folders_path,
    serial_suites_path,
    undefined_steps_features_path,
)
from behave import then, when
from execution_steps import (
    fixtures_path,
    get_unique_suffix,
    root_project_path,
    secondary_features_path,
)


@when('I run BehaveXRunner on passing tests in one process with tags "{tag_a}", none, "{tag_b}", none')
def when_api_run_repeated_with_tags(context, tag_a, tag_b):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    script = f"""
import json, sys
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


@when('I run BehaveXRunner in one process with a config file setting output folder "{folder_a}", then one setting "{folder_b}"')
def when_api_run_with_two_config_files(context, folder_a, folder_b):
    base = os.path.join(root_project_path, 'output', f'api_runner_config_{get_unique_suffix()}')
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


@when('I run BehaveXRunner in one process on passing tests, then with include_paths on failing tests only')
def when_api_run_paths_then_include_paths(context):
    passing_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    failing_path = os.path.join(secondary_features_path, 'failing_tests.feature')
    script = f"""
import json, sys
totals = [
    BehaveXRunner(paths=[{repr(passing_path)}], no_report=True).run().summary.total,
    BehaveXRunner(include_paths=[{repr(failing_path)}], no_report=True).run().summary.total,
]
print("__RESULT__:" + json.dumps({{"totals": totals}}))
"""
    _store_result(context, _run_script(script))


@when('I run BehaveXRunner in one process with rerun_failures on the failing test, then on passing tests with "{processes}" parallel processes')
def when_api_run_rerun_failures_then_parallel(context, processes):
    base = os.path.join(root_project_path, 'output', f'api_runner_rerun_{get_unique_suffix()}')
    context.add_cleanup(shutil.rmtree, base, ignore_errors=True)
    os.makedirs(base)
    failures_file = os.path.join(base, 'failing_scenarios.txt')
    with open(failures_file, 'w') as failures:
        failures.write(os.path.join(secondary_features_path, 'failing_tests.feature') + ':3')
    passing_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    script = f"""
import json, sys
totals = [
    BehaveXRunner(rerun_failures={repr(failures_file)}, no_report=True).run().summary.total,
    BehaveXRunner(paths=[{repr(passing_path)}], parallel_processes={int(processes)}, no_report=True).run().summary.total,
]
print("__RESULT__:" + json.dumps({{"totals": totals}}))
"""
    _store_result(context, _run_script(script))


@when('I run BehaveXRunner in one process on worker hook tests, then on passing tests')
def when_api_run_worker_hooks_then_passing(context):
    worker_hooks_path = os.path.join(fixtures_path, 'worker_hooks_features')
    passing_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    suffix = get_unique_suffix()
    output_folders = [os.path.join(root_project_path, 'output', f'api_runner_hooks_{suffix}_{run}') for run in (1, 2)]
    script = f"""
import json, sys
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


@when('I run BehaveXRunner in one process as a dry run, then as a real run, on passing scenarios, one with a failing after_scenario hook')
def when_api_dry_run_then_real_run(context):
    feature_path = os.path.join(api_runner_features_path, 'teardown_error', 'teardown_error.feature')
    script = f"""
import json, sys
BehaveXRunner(paths=[{repr(feature_path)}], dry_run=True, no_report=True).run()
result = BehaveXRunner(paths=[{repr(feature_path)}], no_report=True).run()
""" + _SERIALIZE_RESULT
    _store_result(context, _run_script(script))


@when('I run BehaveXRunner with passing tests while sys.stdout is an io.StringIO')
def when_api_run_with_string_io_stdout(context):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    script = f"""
import io, json, sys
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


@when('I run BehaveXRunner {mode} on the undefined steps features, then on the top feature, in the same process')
def when_run_two_suites_in_one_process(context, mode):
    top_feature_path = os.path.join(nested_steps_folders_path, 'top.feature')
    script = f"""
import json, sys

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


@when('I run BehaveXRunner in parallel by {scheme} on the first @SERIAL suite, then on the second, in the same process')
def when_run_two_serial_suites_in_one_process(context, scheme):
    run_mode = _RUN_MODES[f'in parallel by {scheme}']
    script = f"""
import json, sys

if __name__ == '__main__':
    BehaveXRunner(paths=[{os.path.join(serial_suites_path, 'first')!r}], no_report=True, **{run_mode!r}).run()
    result = BehaveXRunner(paths=[{os.path.join(serial_suites_path, 'second')!r}], no_report=True,
                           **{run_mode!r}).run()
    print("__RESULT__:" + json.dumps({{"statuses": {{s.name: s.status for f in result.features
                                                    for s in f.scenarios}}}}))
"""
    _store_result(context, _run_script(script))


@when('I run BehaveXRunner in a single process on a step that runs a subprocess writing to sys.stdout')
def when_run_step_writing_to_stdout_descriptor(context):
    _run_via_api(context, os.path.join(api_runner_features_path, 'stdout_file_descriptor'))


@when('I run BehaveXRunner {mode} after the host application configured its own logging')
def when_run_after_host_configured_logging(context, mode):
    script = f"""
import io, json, logging, sys
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


@when('I run BehaveXRunner {mode} on slow scenarios from a host that forks processes and registered the same step itself')
def when_run_from_forking_host_with_its_own_step(context, mode):
    script = f"""
import json, multiprocessing, sys
from behave import given
{_CAPTURE_RAISED}

@given('a step that takes half a second')
def host_step(context):
    pass

if __name__ == '__main__':
    multiprocessing.set_start_method('fork')
    results = []
    raised = _capture_raised(lambda: results.append(BehaveXRunner(
        paths=[{os.path.join(api_runner_features_path, 'slow_scenarios')!r}], no_report=True,
        **{_RUN_MODES[mode]!r}).run()))
    print("__RESULT__:" + json.dumps({{"raised": raised, "exit_code": results[0].exit_code if results else None}}))
"""
    _store_result(context, _run_script(script))


@then('the run raised no exception and its RunResult exit_code is "{exit_code}"')
def then_no_exception_and_exit_code(context, exit_code):
    result = context.api_run_result
    assert result['raised'] is None and result['exit_code'] == int(exit_code), (
        f'Got {result}.\nOutput:\n{context.api_run_output}'
    )

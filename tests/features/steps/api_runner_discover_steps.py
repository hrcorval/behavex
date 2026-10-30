import os
import shutil
import tempfile

from api_runner_support import (
    _CAPTURE_RAISED,
    _RUN_MODES,
    _STOP_WHILE_BEFORE_ALL_WORKERS_RUNS,
    _non_result_lines,
    _refused_input_kwargs,
    _run_script,
    _store_result,
    api_runner_features_path,
    nested_steps_folders_path,
    root_project_path,
    secondary_features_path,
    undefined_steps_features_path,
)
from behave import then, when
from config_file_steps import _clean_child_env, _make_config_dir, _write_config_file
from execution_steps import execute_command, get_unique_suffix

discovery_features_path = os.path.join(api_runner_features_path, 'discovery')
discovery_feature = os.path.relpath(os.path.join(discovery_features_path, 'discovery.feature'), root_project_path)


_DISCOVER_FEATURES_PATHS = {
    'the discovery features': [discovery_features_path],
    'the undefined steps features': [undefined_steps_features_path],
    'a top feature and a feature with its own steps folder': [
        os.path.join(nested_steps_folders_path, 'top.feature'),
        os.path.join(nested_steps_folders_path, 'nested', 'nested.feature')],
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
    config_file_filters = {
        'the config tags_to_skip': '[test_run]\ntags_to_skip=SKIP\n',
        'the config exclude': '[params]\nexclude=other\n',
        'the config include': '[params]\ninclude=other\n',
    }
    if filter_name in config_file_filters:
        kwargs['config'] = _write_config_file(_make_config_dir(context), 'behavex.cfg',
                                              config_file_filters[filter_name])
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
from behavex import runner
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


@when('I run BehaveXRunner {case} with a configured output folder, then call load_results() on that folder')
def when_run_then_load_results(context, case):
    output_folder = os.path.join('output', f'api_runner_load_{get_unique_suffix()}')
    context.add_cleanup(shutil.rmtree, output_folder, ignore_errors=True)
    kwargs = dict(_LOAD_RESULTS_CASES[case], output_folder=output_folder)
    stop_while_before_all_workers_runs = kwargs.pop('stop_while_before_all_workers_runs', False)
    script = f"""
import json, sys, threading
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
    output_folder = os.path.join('output', f'api_runner_load_{get_unique_suffix()}')
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
{_CAPTURE_RAISED}
if __name__ == '__main__':
    {folder_setup_code}
    raised = _capture_raised(lambda: BehaveXRunner.load_results({output_folder!r}))
    print("__RESULT__:" + json.dumps({{"raised": raised}}))
"""
    _store_result(context, _run_script(script))


@when('I run behavex from the CLI on the secondary features, then call load_results() on its output folder')
def when_cli_run_then_load_results(context):
    output_folder = os.path.join('output', f'api_runner_load_cli_{get_unique_suffix()}')
    context.add_cleanup(shutil.rmtree, output_folder, ignore_errors=True)
    execute_command(context, ['behavex', secondary_features_path, '-o', output_folder],
                    env=_clean_child_env(), cwd=root_project_path)
    context.cli_exit_code = context.result.returncode
    script = f"""
import json, sys
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

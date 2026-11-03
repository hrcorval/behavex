import os
import shutil

from behave import then, when
from execution_steps import fixtures_path, new_output_path, run_behavex_on_target, tests_features_path


@when('I run the behavex command targeting the invalid worker hooks feature')
def when_run_invalid_worker_hooks_feature(context):
    run_behavex_on_target(context, os.path.join(fixtures_path, 'worker_hooks_invalid_features'), '')


@when('I run the behavex command on the "{target}" worker hooks fixture with arguments "{arguments}"')
def when_run_worker_hooks_fixture_with_arguments(context, target, arguments):
    run_behavex_on_target(context, target, arguments)


@when('I run the behavex command on a copy of the "{target}" worker hooks fixture whose environment.py is encoded in Latin-1')
def when_run_latin1_copy_of_worker_hooks_fixture(context, target):
    fixture_copy_path = os.path.abspath(new_output_path())
    shutil.copytree(os.path.join(tests_features_path, target), fixture_copy_path)
    environment_path = os.path.join(fixture_copy_path, 'environment.py')
    with open(environment_path) as environment_file:
        source = environment_file.read()
    with open(environment_path, 'wb') as environment_file:
        environment_file.write(('# -*- coding: latin-1 -*-\n# café\n' + source).encode('latin-1'))
    run_behavex_on_target(context, os.path.join(fixture_copy_path, 'features', 'sub'), '--parallel-processes 1')


@when('I run the behavex command on the "{target}" worker hooks fixture with "{variable}" set to "{value}" and arguments "{arguments}"')
def when_run_worker_hooks_fixture_with_env_variable(context, target, variable, value, arguments):
    env = os.environ.copy()
    env[variable] = value
    run_behavex_on_target(context, target, arguments, env=env)


@then('I should see the worker hook "{hook_name}" was called "{expected_calls}" times')
def then_worker_hook_called_times(context, hook_name, expected_calls):
    calls_path = os.path.join(context.output_path, 'worker_hook_calls.log')
    recorded_calls = []
    if os.path.exists(calls_path):
        with open(calls_path) as calls_file:
            recorded_calls = calls_file.read().split()
    actual_calls = recorded_calls.count(hook_name)
    assert actual_calls == int(expected_calls), (
        f"Expected {hook_name} to be called {expected_calls} times, got {actual_calls}\n"
        f"STDOUT:\n{context.result.stdout}"
    )


def _environment_importing_process_names(context):
    with open(os.path.join(context.output_path, 'environment_imports.log')) as imports_file:
        return imports_file.read().split()


@then('environment.py was imported by worker processes but not by the BehaveX main process')
def then_environment_imported_only_by_workers(context):
    importing_process_names = _environment_importing_process_names(context)
    assert importing_process_names and 'MainProcess' not in importing_process_names, (
        f"Processes that imported environment.py: {importing_process_names}\n"
        f"STDOUT:\n{context.result.stdout}"
    )


@then('environment.py was imported only once, by the BehaveX main process')
def then_environment_imported_once_by_main_process(context):
    importing_process_names = _environment_importing_process_names(context)
    assert importing_process_names == ['MainProcess'], (
        f"Processes that imported environment.py: {importing_process_names}\n"
        f"STDOUT:\n{context.result.stdout}"
    )

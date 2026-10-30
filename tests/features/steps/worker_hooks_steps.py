import os

from behave import then, when
from execution_steps import (
    execute_command,
    get_unique_suffix,
    run_behavex_on_target,
    tests_features_path,
)


@when('I run the behavex command targeting the invalid worker hooks feature')
def when_run_invalid_worker_hooks_feature(context):
    context.output_path = os.path.join('output', 'output_{}'.format(get_unique_suffix()))
    execution_args = [
        'behavex',
        os.path.join(tests_features_path, 'fixtures', 'worker_hooks_invalid_features'),
        '-o', context.output_path,
    ]
    execute_command(context, execution_args)


@when('I run the behavex command on the "{target}" worker hooks fixture with arguments "{arguments}"')
def when_run_worker_hooks_fixture_with_arguments(context, target, arguments):
    run_behavex_on_target(context, target, arguments)


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

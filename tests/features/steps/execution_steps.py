import logging
import subprocess

from behave import given, then, when


@when('I run the behavex command with a passing test')
def step_impl(context):
    context.result = subprocess.run(['behavex', './tests/features/secondary_features/passing_tests.feature', '-o', 'output/passing'], capture_output=True, text=True)
    print(context.result.stdout)
    logging.info(context.result.stdout)

@when('I run the behavex command with a failing test')
def step_impl(context):
    context.result = subprocess.run(['behavex', './tests/features/secondary_features/failing_tests.feature', '-o', 'output/failing'], capture_output=True, text=True)
    logging.info(context.result.stdout)

@when('I run the behavex command with a crashing test')
def step_impl(context):
    context.result = subprocess.run(['behavex', './tests/features/crashing_features/crashing_tests.feature', '-o', 'output/crashing'], capture_output=True, text=True)
    logging.info(context.result.stdout)


@when('I run the behavex command with a skipped test')
def step_impl(context):
    context.result = subprocess.run(['behavex', './tests/features/secondary_features/skippedd_tests.feature', '-o', 'output/skipped'], capture_output=True, text=True)
    logging.info(context.result.stdout)

@when('I run the behavex command with an untested test')
def step_impl(context):
    context.result = subprocess.run(['behavex', './tests/features/secondary_features/untested_tests.feature', '-o', 'output/untested'], capture_output=True, text=True)
    logging.info(context.result.stdout)

@when('I run the behavex command with "{parallel_processes}" parallel processes and parallel scheme set as "{parallel_schema}"')
def step_impl(context, parallel_processes, parallel_schema):
    context.result = subprocess.run(['behavex', './tests/features/secondary_features/', '-o', 'output/parallel_{}_{}'.format(parallel_processes, parallel_schema), '--parallel-processes', parallel_processes, '--parallel-scheme', parallel_schema], capture_output=True, text=True)
    logging.info(context.result.stdout)

@then('I should see the behavex output with "{expected_output}"')
@then('I should see the behavex output with "{expected_output}" and exit code "{expected_exit_code}"')
def step_impl(context, expected_output, expected_exit_code=None):
    if expected_exit_code is not None:
        assert int(context.result.returncode) == int(expected_exit_code), "behavex command failed"
    assert expected_output in context.result.stdout, f"Unexpected output: {context.result.stdout}"

@then('I should not see error messages in the output')
def step_impl(context):
    error_messages = ["error", "exception", "traceback"]
    for message in error_messages:
        assert message not in context.result.stdout.lower(), f"Unexpected output: {context.result.stdout}"

@then('I should not see exception messages in the output')
def step_impl(context):
    exception_messages = ["exception", "traceback"]
    for message in exception_messages:
        assert message not in context.result.stdout.lower(), f"Unexpected output: {context.result.stdout}"

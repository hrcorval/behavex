import logging
import subprocess

from behave import given, then, when


@when('I run the behavex command with a passing test')
def step_impl(context):
    execution_args = ['behavex', './tests/features/secondary_features/passing_tests.feature', '-o', 'output/passing']
    logging.info(' '.join(execution_args))
    context.result = subprocess.run(execution_args, capture_output=True, text=True)
    logging.info(context.result.stdout)

@when('I run the behavex command with a failing test')
def step_impl(context):
    execution_args = ['behavex', './tests/features/secondary_features/failing_tests.feature', '-o', 'output/failing']
    logging.info(' '.join(execution_args))
    context.result = subprocess.run(execution_args, capture_output=True, text=True)
    logging.info(context.result.stdout)

@when('I run the behavex command with a crashing test')
def step_impl(context):
    execution_args = ['behavex', './tests/features/crashing_features/crashing_tests.feature', '-o', 'output/crashing']
    logging.info(' '.join(execution_args))
    context.result = subprocess.run(execution_args, capture_output=True, text=True)
    logging.info(context.result.stdout)

@when('I run the behavex command with a skipped test')
def step_impl(context):
    execution_args = ['behavex', './tests/features/secondary_features/skipped_tests.feature', '-o', 'output/skipped']
    logging.info(' '.join(execution_args))
    context.result = subprocess.run(execution_args, capture_output=True, text=True)
    logging.info(context.result.stdout)

@when('I run the behavex command with an untested test')
def step_impl(context):
    execution_args = ['behavex', './tests/features/secondary_features/untested_tests.feature', '-o', 'output/untested']
    logging.info(' '.join(execution_args))
    context.result = subprocess.run(execution_args, capture_output=True, text=True)
    logging.info(context.result.stdout)

@when('I run the behavex command with "{parallel_processes}" parallel processes and parallel scheme set as "{parallel_schema}"')
def step_impl(context, parallel_processes, parallel_schema):
    execution_args = ['behavex', './tests/features/secondary_features/', '-o', 'output/parallel_{}_{}'.format(parallel_processes, parallel_schema), '--parallel-processes', parallel_processes, '--parallel-scheme', parallel_schema]
    logging.info(' '.join(execution_args))
    context.result = subprocess.run(execution_args, capture_output=True, text=True)
    logging.info(context.result.stdout)

@when('I run the behavex command with the following scheme, processes and tags')
def step_impl(context):
    scheme = context.table[0]['parallel_scheme']
    processes = context.table[0]['parallel_processes']
    tags = context.table[0]['tags']
    tags_to_folder_name = get_tags_string(tags)
    tags_array = get_tags_arguments(tags)
    execution_args = ['behavex', './tests/features/secondary_features/', '-o', 'output/parallel_{}_{}'.format(processes, scheme), '--parallel-processes', processes, '--parallel-scheme', scheme] + tags_array
    logging.info(' '.join(execution_args))
    context.result = subprocess.run(execution_args, capture_output=True, text=True)
    logging.info(context.result.stdout)

@when('I run the behavex command with the following tags')
def step_impl(context):
    tags = context.table[0]['tags']
    tags_to_folder_name = get_tags_string(tags)
    tags_array = get_tags_arguments(tags)
    execution_args = ['behavex', './tests/features/secondary_features/', '-o', 'output/tags{}'.format(tags_to_folder_name)] + tags_array
    logging.info(' '.join(execution_args))
    context.result = subprocess.run(execution_args, capture_output=True, text=True)
    logging.info(context.result.stdout)

@then('I should see the following behavex console outputs')
@then('I should see the following behavex console outputs and exit code "{expected_exit_code}"')
def step_impl(context, expected_exit_code=None):
    if expected_exit_code is not None:
        assert int(context.result.returncode) == int(expected_exit_code), "Behavex exit code is not expected"
    for row in context.table:
        assert row['output_line'] in context.result.stdout, f"Unexpected output: {context.result.stdout}\n\nOutput line not found: {row['output_line']}"


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


def get_tags_arguments(tags):
    tags_array = []
    for tag in tags.split(' '):
        tags_array += tag.split('=')
    return tags_array

def get_tags_string(tags):
    return tags.replace('-t=','_AND_').replace('~','NOT_').replace(',','_OR_').replace(' ','').replace('@','')

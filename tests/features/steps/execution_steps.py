import logging
import os
import random
import subprocess

from behave import given, then, when

root_project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
tests_features_path = os.path.join(root_project_path, 'tests', 'features')

@given('I have the progress bar enabled')
def step_impl(context):
    context.progress_bar = True

@when('I run the behavex command with a passing test')
@when('I run the behavex command with passing tests')
def step_impl(context):
    execution_args = ['behavex', os.path.join(tests_features_path, 'secondary_features/passing_tests.feature'), '-o', 'output/output_{}'.format(get_random_number(6))]
    execute_command(context, execution_args)

@when('I run the behavex command that renames scenarios and features')
def step_impl(context):
    execution_args = ['behavex', os.path.join(tests_features_path, 'secondary_features/rename_tests.feature'), '-o', 'output/output_{}'.format(get_random_number(6))]
    if hasattr(context, 'parallel_processes'):
        execution_args += ['--parallel-processes', context.parallel_processes]
    if hasattr(context, 'parallel_scheme'):
        execution_args += ['--parallel-scheme', context.parallel_scheme]
    execute_command(context, execution_args)

@when('I run the behavex command with a failing test')
def step_impl(context):
    execution_args = ['behavex', os.path.join(tests_features_path, 'secondary_features/failing_tests.feature'), '-o', 'output/output_{}'.format(get_random_number(6))]
    execute_command(context, execution_args)


@when('I run the behavex command with a crashing test')
@when('I run the behavex command with a crashing test with "{parallel_processes}" parallel processes and parallel scheme set as "{parallel_scheme}"')
def step_impl(context, parallel_processes="1", parallel_scheme='scenario'):
    execution_args = ['behavex',
                os.path.join(tests_features_path, os.path.join(tests_features_path, 'crashing_features/crashing_tests.feature')),
                '-o', 'output/output_{}'.format(get_random_number(6)),
                '--parallel-processes', parallel_processes,
                '--parallel-scheme', parallel_scheme]
    execute_command(context, execution_args)


@when('I run the behavex command with a skipped test')
def step_impl(context):
    execution_args = ['behavex', os.path.join(tests_features_path, 'secondary_features/skipped_tests.feature'), '-o', 'output/output_{}'.format(get_random_number(6))]
    execute_command(context, execution_args)


@when('I run the behavex command with an untested test')
def step_impl(context):
    execution_args = ['behavex', os.path.join(tests_features_path, 'secondary_features/untested_tests.feature'), '-o', 'output/output_{}'.format(get_random_number(6))]
    execute_command(context, execution_args)


@when('I run the behavex command with "{parallel_processes}" parallel processes and parallel scheme set as "{parallel_schema}"')
def step_impl(context, parallel_processes, parallel_schema):
    execution_args = ['behavex', os.path.join(tests_features_path, 'secondary_features/'), '-o', 'output/output_{}'.format(get_random_number(6)), '--parallel-processes', parallel_processes, '--parallel-scheme', parallel_schema]
    execute_command(context, execution_args)


@when('I setup the behavex command with "{parallel_processes}" parallel processes and parallel scheme set as "{parallel_scheme}"')
def step_impl(context, parallel_processes, parallel_scheme):
    context.parallel_processes = parallel_processes
    context.parallel_scheme = parallel_scheme


@when('I run the behavex command with the following scheme, processes and tags')
def step_impl(context):
    scheme = context.table[0]['parallel_scheme']
    processes = context.table[0]['parallel_processes']
    tags = context.table[0]['tags']
    tags_to_folder_name = get_tags_string(tags)
    tags_array = get_tags_arguments(tags)
    execution_args = ['behavex', os.path.join(tests_features_path, 'secondary_features/'), '-o', 'output/output_{}'.format(get_random_number(6)), '--parallel-processes', processes, '--parallel-scheme', scheme] + tags_array
    execute_command(context, execution_args)


@when('I run the behavex command with the following tags')
def step_impl(context):
    tags = context.table[0]['tags']
    tags_to_folder_name = get_tags_string(tags)
    tags_array = get_tags_arguments(tags)
    execution_args = ['behavex', os.path.join(tests_features_path, 'secondary_features/'), '-o', 'output/output_{}'.format(get_random_number(6))] + tags_array
    execute_command(context, execution_args)


@when('I run the behavex command by performing a dry run')
def step_impl(context):
    # generate a random number between 1 and 1000000 completing with zeroes to 6 digits
    execution_args = ['behavex', os.path.join(tests_features_path, 'secondary_features/'), '-o', 'output/output_{}'.format(get_random_number(6)), '--dry-run']
    execute_command(context, execution_args)


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

def get_random_number(total_digits):
    return str(random.randint(1, 1000000)).zfill(total_digits)

def execute_command(context, command, print_output=True):
    if "progress_bar" in context and context.progress_bar:
        command.insert(2, '--show-progress-bar')
    context.result = subprocess.run(command, capture_output=True, text=True)
    if print_output:
        logging.info(context.result.stdout)

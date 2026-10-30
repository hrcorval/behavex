import logging
import os
import shlex
import subprocess
import uuid

from behave import given, then, when
from packaging.version import Version

root_project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
tests_features_path = os.path.join(root_project_path, 'tests', 'features')
fixtures_path = os.path.join(tests_features_path, 'fixtures')
secondary_features_path = os.path.join(fixtures_path, 'secondary_features')


@given('The progress bar is enabled')
def given_progress_bar_enabled(context):
    context.progress_bar = True


@when('I run the behavex command with a passing test')
@when('I run the behavex command with passing tests')
def when_run_passing_test(context):
    run_behavex_on_target(context, os.path.join(secondary_features_path, 'passing_tests.feature'), '')


def _require_behave_for_rule(context):
    """Skip the scenario if the installed behave version does not support Rule sections."""
    import behave as _behave
    if Version(_behave.__version__) < Version('1.3.3'):
        context.scenario.skip(reason=f'Rule sections require behave >= 1.3.3 (installed: {_behave.__version__})')
        return False
    return True


@when('I run the behavex command with a rule test')
def when_run_rule_test(context):
    if not _require_behave_for_rule(context):
        return
    run_behavex_on_target(context, os.path.join(fixtures_path, 'rule_features', 'rule_tests.feature'), '')


@when('I run the behavex command with a rule test using "{parallel_processes}" parallel processes and "{parallel_scheme}" parallel scheme')
def when_run_rule_test_parallel(context, parallel_processes, parallel_scheme):
    if not _require_behave_for_rule(context):
        return
    run_behavex_on_target(context, os.path.join(fixtures_path, 'rule_features', 'rule_tests.feature'),
                          f'--parallel-processes {parallel_processes} --parallel-scheme {parallel_scheme}')


@when('I run the behavex command with a file of failing tests')
def when_run_failing_tests_file(context):
    context.output_path = new_output_path()
    execution_args = ['behavex', '-rf', os.path.join(fixtures_path, 'failing_scenarios.txt'), '-o', context.output_path]
    execute_command(context, execution_args)


@when('I run the behavex command on passing tests rerunning the failures of a "{failures_file_state}" file')
def when_rerun_failures_from_missing_or_empty_failures_file(context, failures_file_state):
    context.output_path = new_output_path()
    failures_path = os.path.join('output', 'failures_{}.txt'.format(get_unique_suffix()))
    if failures_file_state in ('empty', 'blank'):
        os.makedirs('output', exist_ok=True)
        with open(failures_path, 'w') as failures_file:
            failures_file.write('\n' if failures_file_state == 'blank' else '')
    execution_args = ['behavex', os.path.join(secondary_features_path, 'passing_tests.feature'),
                      '-rf', failures_path, '-o', context.output_path]
    execute_command(context, execution_args)


@when('I run the behavex command that renames scenarios and features')
def when_run_renaming_test(context):
    run_behavex_on_target(context, os.path.join(secondary_features_path, 'rename_tests.feature'), '')


@when('I run the behavex command with a failing test')
def when_run_failing_test(context):
    run_behavex_on_target(context, os.path.join(secondary_features_path, 'failing_tests.feature'), '')


@when('I run the behavex command with a crashing test')
def when_run_crashing_test(context, parallel_processes="1", parallel_scheme='scenario'):
    run_behavex_on_target(context, os.path.join(fixtures_path, 'crashing_features', 'crashing_tests.feature'), '')


@when('I run the behavex command with no tests')
def when_run_no_tests(context, parallel_processes="1", parallel_scheme='scenario'):
    context.output_path = new_output_path()
    execution_args = ['behavex',
                os.path.join(fixtures_path, 'crashing_features', 'crashing_tests.feature'),
                '-t', 'NO_TESTS',
                '-o', context.output_path]
    execute_command(context, execution_args)


@when('I run the behavex command with a test that crashes in "{behave_hook}" hook')
@when('I run the behavex command with a test that crashes in "{behave_hook}" hook with "{parallel_processes}" parallel processes and "{parallel_scheme}" parallel scheme')
def when_run_crashing_hook_test(context, behave_hook, parallel_processes="1", parallel_scheme='scenario',
                                feature_filename='crashing_environment_tests.feature'):
    run_behavex_on_target(context, os.path.join(fixtures_path, 'crashing_features', feature_filename),
                          f'--parallel-processes {parallel_processes} --parallel-scheme {parallel_scheme} '
                          f'-D crashing_behave_hook={behave_hook}')


@when('I run the behavex command with a muted failing test that crashes in "{behave_hook}" hook with "{parallel_processes}" parallel processes and "{parallel_scheme}" parallel scheme')
def when_run_muted_failing_crashing_hook_test(context, behave_hook, parallel_processes, parallel_scheme):
    when_run_crashing_hook_test(context, behave_hook, parallel_processes, parallel_scheme,
                                feature_filename='muted_failing_tests.feature')


@when('I run the behavex command with a muted rule test that crashes in "{behave_hook}" hook with "{parallel_processes}" parallel processes and "{parallel_scheme}" parallel scheme')
def when_run_muted_rule_crashing_hook_test(context, behave_hook, parallel_processes, parallel_scheme):
    if not _require_behave_for_rule(context):
        return
    when_run_crashing_hook_test(context, behave_hook, parallel_processes, parallel_scheme,
                                feature_filename='muted_rule_tests.feature')


@when('I run the behavex command with a skipped test')
def when_run_skipped_test(context):
    run_behavex_on_target(context, os.path.join(secondary_features_path, 'skipped_tests.feature'), '')


@when('I run the behavex command with an untested test')
def when_run_untested_test(context):
    run_behavex_on_target(context, os.path.join(secondary_features_path, 'untested_tests.feature'), '')


@when('I run the behavex command with "{parallel_processes}" parallel processes and parallel scheme set as "{parallel_scheme}"')
def when_run_with_parallel_config(context, parallel_processes, parallel_scheme):
    run_behavex_on_target(context, secondary_features_path,
                          f'--parallel-processes {parallel_processes} --parallel-scheme {parallel_scheme}')


@when('I setup the behavex command with "{parallel_processes}" parallel processes and parallel scheme set as "{parallel_scheme}"')
def when_setup_parallel_config(context, parallel_processes, parallel_scheme):
    context.parallel_processes = parallel_processes
    context.parallel_scheme = parallel_scheme


@when('I run the behavex command with the following scheme, processes and tags')
@when('I run the behavex command with scenario name "{scenario_name}" and the following scheme, processes and tags')
@when('I run the behavex command using "{argument_separator}" separator with the following scheme, processes and tags')
@when('I run the behavex command using "{argument_separator}" separator for "{feature_name}" feature with the following scheme, processes and tags')
@when('I run the behavex command using "{argument_separator}" separator for "{feature_name}" and "{feature_name_2}" features with the following scheme, processes and tags')
def run_command_with_scheme_processes_and_tags(context, scenario_name=None, argument_separator="equal", feature_name=None, feature_name_2=None):
    scheme = context.table[0]['parallel_scheme']
    processes = context.table[0]['parallel_processes']
    tags = context.table[0]['tags']
    context.output_path = new_output_path()
    tags_to_folder_name = get_tags_string(tags)
    if not tags:
        tags_array = []
    else:
        tags_array = get_tags_arguments(tags)
    feature_path_2 = None
    if feature_name:
        if feature_name_2:
            feature_path = os.path.join(secondary_features_path, feature_name)
            feature_path_2 = os.path.join(secondary_features_path, feature_name_2)
        else:
            feature_path = os.path.join(secondary_features_path, feature_name)
    else:
        feature_path = secondary_features_path
    if argument_separator == 'equal':
        execution_args = ['behavex', feature_path, '-o', context.output_path, '--parallel-processes=' + processes, '--parallel-scheme=' + scheme] + tags_array
    else:
        execution_args = ['behavex', feature_path, '-o', context.output_path, '--parallel-processes', processes, '--parallel-scheme', scheme] + tags_array
    if feature_name_2:
        # append the second feature path to the execution arguments in index 2
        execution_args.insert(2, feature_path_2)
    if scenario_name:
        execution_args.append('--name')
        execution_args.append(scenario_name.replace(' ', '\\ '))
    execute_command(context, execution_args)


@when('I run the behavex command with the following tags')
def when_run_with_tags(context):
    tags = context.table[0]['tags']
    tags_to_folder_name = get_tags_string(tags)
    tags_array = get_tags_arguments(tags)
    context.output_path = new_output_path()
    execution_args = ['behavex', secondary_features_path, '-o', context.output_path] + tags_array
    execute_command(context, execution_args)


@when('I run the behavex command by performing a dry run')
def when_run_dry_run(context):
    run_behavex_on_target(context, secondary_features_path, '--dry-run')


@then('I should see the following behavex console outputs')
@then('I should see the following behavex console outputs and exit code "{expected_exit_code}"')
def then_see_console_outputs(context, expected_exit_code=None):
    if expected_exit_code is not None:
        assert int(context.result.returncode) == int(expected_exit_code), (
            f"Behavex exit code is not expected (got {context.result.returncode}, expected {expected_exit_code})\n"
            f"STDOUT:\n{context.result.stdout}\n"
            f"STDERR:\n{context.result.stderr}"
        )
    for row in context.table:
        assert row['output_line'] in context.result.stdout, f"Unexpected output when checking console outputs: {context.result.stdout}\n\nOutput line not found: {row['output_line']}\n"


@then('I should not see error messages in the output')
def then_no_error_messages(context):
    error_messages = ["error", "exception", "traceback"]
    # Filter out expected behavex-images errors during dry run
    output_lines = context.result.stdout.split('\n')
    filtered_output = []

    for line in output_lines:
        # Skip expected behavex-images errors during dry run
        if '[behavex-images]' in line and ('expected str, bytes or os.PathLike object, not NoneType' in line or
                                           'It was not possible to add the image to the report' in line):
            continue
        # Skip formatter tag lines (e.g. "@ERROR_SCENARIO @IMAGE_ATTACHMENT")
        if all(part.startswith('@') for part in line.strip().split() if part):
            continue
        # Skip expected error messages from test scenarios during dry run
        if ('ERROR - Executing permanently broken action' in line or
            'ERROR - This step is designed to fail' in line or
            'ERROR - Permanently broken action failed' in line or
            'ERROR - Flaky action failed (expected' in line or
            'ERROR - Action failed without retry (expected' in line or
            'ERROR - Unexpected output when checking error messages in the console output:' in line or
            'BehaveX AUTO-RETRY: Scenario' in line or
            'image_attachments_undefined_step.feature:' in line or
            'Errored scenarios:' in line or
            'Failing scenarios:' in line or
            ('features passed' in line and 'failed' in line and 'error' in line) or  # Summary lines like "X features passed, Y failed, Z error"
            ('scenarios passed' in line and 'failed' in line) or  # Summary lines like "X scenarios passed, Y failed"
            ('steps passed' in line and 'failed' in line)):  # Summary lines like "X steps passed, Y failed"
            continue
        filtered_output.append(line)

    filtered_output_text = '\n'.join(filtered_output)

    for message in error_messages:
        assert message not in filtered_output_text.lower(), f"Unexpected output when checking error messages in the console output: {context.result.stdout}\n"


@then('I should not see exception messages in the output')
def then_no_exception_messages(context):
    exception_messages = ["exception", "traceback"]
    for message in exception_messages:
        assert message not in context.result.stdout.lower(), f"Unexpected output when checking exception messages in the console output: {context.result.stdout}\n"


@then('I should not see "{text}" in the console output')
def then_text_not_in_console(context, text):
    assert text not in context.result.stdout, \
        f"Expected '{text}' to not appear in console output, but it did.\nOutput:\n{context.result.stdout}"


@then('I should not see "{text}" in the console output or its errors')
def then_text_not_in_console_or_stderr(context, text):
    output = context.result.stdout + context.result.stderr
    assert text not in output, f"Expected '{text}' to not appear in the output, but it did.\nOutput:\n{output}"


@then('I should see "{text}" in the console output')
def then_text_in_console(context, text):
    assert text in context.result.stdout, \
        f"Expected '{text}' in console output, but it was not found.\nOutput:\n{context.result.stdout}"


@when('I run the behavex command targeting the "{feature_path}" feature')
@when('I run the behavex command targeting the "{feature_path}" feature with "{parallel_processes}" parallel processes')
def when_run_with_feature_path(context, feature_path, parallel_processes='1'):
    context.output_path = new_output_path()
    execution_args = ['behavex',
                      os.path.join(tests_features_path, feature_path),
                      '--parallel-processes', parallel_processes,
                      '-o', context.output_path]
    execute_command(context, execution_args)


@when('I run the behavex command on "{target}" with arguments "{arguments}"')
def when_run_behavex_on_target_with_arguments(context, target, arguments):
    run_behavex_on_target(context, target, arguments)


def run_behavex_on_target(context, target, arguments, env=None):
    context.output_path = new_output_path()
    execution_args = [
        'behavex',
        os.path.join(tests_features_path, target),
        '-o', context.output_path,
    ] + shlex.split(arguments)
    execute_command(context, execution_args, env=env)


def get_tags_arguments(tags):
    tags_array = []
    for tag in tags.split(' '):
        tags_array += tag.split('=')
    return tags_array


def get_tags_string(tags):
    return tags.replace('-t=','_AND_').replace('~','NOT_').replace(',','_OR_').replace(' ','').replace('@','')


def get_unique_suffix():
    return uuid.uuid4().hex[:8]


def new_output_path():
    return os.path.join('output', 'output_{}'.format(get_unique_suffix()))


def execute_command(context, execution_args, print_output=True, env=None, cwd=None):
    if "progress_bar" in context and context.progress_bar:
        execution_args.insert(2, '--show-progress-bar')
    if hasattr(context, 'parallel_processes'):
        execution_args += ['--parallel-processes', context.parallel_processes]
    if hasattr(context, 'parallel_scheme'):
        execution_args += ['--parallel-scheme', context.parallel_scheme]
    logging.info("Executing command: {}".format(" ".join(execution_args)))
    context.result = subprocess.run(execution_args, capture_output=True, text=True, env=env, cwd=cwd)
    if print_output:
        logging.info(context.result.stdout)

import os

from behave import then, when
from execution_steps import execute_command, get_unique_suffix, tests_features_path


@when('I run the behavex command with --no-report flag using "{parallel_processes}" parallel processes')
def when_run_with_no_report(context, parallel_processes):
    context.output_path = os.path.join('output', 'output_{}'.format(get_unique_suffix()))
    execution_args = [
        'behavex',
        os.path.join(tests_features_path, 'secondary_features', 'passing_tests.feature'),
        '-o', context.output_path,
        '--no-report',
        '--parallel-processes', parallel_processes,
    ]
    execute_command(context, execution_args)


@when('I run the behavex command with --no-report flag and evidence attachments using "{parallel_processes}" parallel processes')
def when_run_with_no_report_and_evidence(context, parallel_processes):
    context.output_path = os.path.join('output', 'output_{}'.format(get_unique_suffix()))
    execution_args = [
        'behavex',
        os.path.join(tests_features_path, 'secondary_features', 'evidence_tests.feature'),
        '-t', '@EVIDENCE_ATTACHMENT',
        '-o', context.output_path,
        '--no-report',
        '--parallel-processes', parallel_processes,
    ]
    execute_command(context, execution_args)


@when('I run the behavex command with --no-report flag and image attachments using "{parallel_processes}" parallel processes')
def when_run_with_no_report_and_images(context, parallel_processes):
    context.output_path = os.path.join('output', 'output_{}'.format(get_unique_suffix()))
    execution_args = [
        'behavex',
        os.path.join(tests_features_path, 'secondary_features', 'evidence_tests.feature'),
        '-t', '@IMAGE_EVIDENCE_ATTACHMENT',
        '-o', context.output_path,
        '--no-report',
        '--parallel-processes', parallel_processes,
    ]
    execute_command(context, execution_args)


@then('the output folder should not exist')
def then_output_folder_not_exist(context):
    output_path = os.path.abspath(context.output_path)
    assert not os.path.exists(output_path), \
        f"Output folder should not exist but was found at: {output_path}"

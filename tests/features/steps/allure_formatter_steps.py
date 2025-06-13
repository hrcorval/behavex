import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path

from behave import given, then, when
from execution_steps import (execute_command, get_random_number,
                             root_project_path)

tests_features_path = os.path.join(root_project_path, 'tests', 'features')


@when('I run the behavex command with allure formatter and passing tests')
def step_impl(context):
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = [
        'behavex',
        os.path.join(tests_features_path, 'secondary_features', 'passing_tests.feature'),
        '-o', context.output_path,
        '--formatter=behavex.outputs.formatters.allure_behavex_formatter:AllureBehaveXFormatter'
    ]
    execute_command(context, execution_args)


@when('I run the behavex command with allure formatter and failing tests')
def step_impl(context):
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = [
        'behavex',
        os.path.join(tests_features_path, 'secondary_features', 'failing_tests.feature'),
        '-o', context.output_path,
        '--formatter=behavex.outputs.formatters.allure_behavex_formatter:AllureBehaveXFormatter'
    ]
    execute_command(context, execution_args)


@when('I run the behavex command with allure formatter using custom output directory "{custom_dir}"')
def step_impl(context, custom_dir):
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    context.custom_allure_dir = custom_dir
    execution_args = [
        'behavex',
        os.path.join(tests_features_path, 'secondary_features', 'passing_tests.feature'),
        '-o', context.output_path,
        '--formatter=behavex.outputs.formatters.allure_behavex_formatter:AllureBehaveXFormatter',
        '--formatter-outdir=' + custom_dir
    ]
    execute_command(context, execution_args)


@when('I run the behavex command with allure formatter and mixed test results')
def step_impl(context):
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = [
        'behavex',
        os.path.join(tests_features_path, 'secondary_features'),
        '-o', context.output_path,
        '--formatter=behavex.outputs.formatters.allure_behavex_formatter:AllureBehaveXFormatter'
    ]
    execute_command(context, execution_args)


@when('I run the behavex command with allure formatter and tagged scenarios')
def step_impl(context):
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = [
        'behavex',
        os.path.join(tests_features_path, 'secondary_features', 'passing_tests.feature'),
        '-o', context.output_path,
        '--formatter=behavex.outputs.formatters.allure_behavex_formatter:AllureBehaveXFormatter'
    ]
    execute_command(context, execution_args)


@when('I run the behavex command with allure formatter and scenario with table data')
def step_impl(context):
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = [
        'behavex',
        os.path.join(tests_features_path, 'secondary_features', 'passing_tests.feature'),
        '-o', context.output_path,
        '--formatter=behavex.outputs.formatters.allure_behavex_formatter:AllureBehaveXFormatter'
    ]
    execute_command(context, execution_args)


@when('I run the behavex command with allure formatter and scenario with multiline text')
def step_impl(context):
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = [
        'behavex',
        os.path.join(tests_features_path, 'secondary_features', 'passing_tests.feature'),
        '-o', context.output_path,
        '--formatter=behavex.outputs.formatters.allure_behavex_formatter:AllureBehaveXFormatter'
    ]
    execute_command(context, execution_args)


@when('I run the behavex command with allure formatter and no log attachments')
def step_impl(context):
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = [
        'behavex',
        os.path.join(tests_features_path, 'secondary_features', 'passing_tests.feature'),
        '-o', context.output_path,
        '--formatter=behavex.outputs.formatters.allure_behavex_formatter:AllureBehaveXFormatter',
        '--no-formatter-attach-logs'
    ]
    execute_command(context, execution_args)


@given('I have a valid BehaveX report.json file')
def step_impl(context):
    # Create a temporary valid report.json for testing
    context.temp_dir = tempfile.mkdtemp()
    context.report_json_path = os.path.join(context.temp_dir, 'report.json')

    # Create a minimal valid report.json
    sample_report = {
        "features": [
            {
                "name": "Test Feature",
                "filename": "tests/features/test.feature",
                "scenarios": [
                    {
                        "name": "Test Scenario",
                        "line": 3,
                        "status": "passed",
                        "identifier_hash": "test_hash_123",
                        "tags": ["@test"],
                        "steps": [
                            {
                                "step_type": "given",
                                "name": "a test condition",
                                "status": "passed",
                                "line": 4
                            }
                        ],
                        "start": "2023-01-01T10:00:00",
                        "stop": "2023-01-01T10:00:01"
                    }
                ]
            }
        ]
    }

    with open(context.report_json_path, 'w') as f:
        json.dump(sample_report, f)


@given('I have an invalid JSON report file')
def step_impl(context):
    # Create a temporary invalid JSON file
    context.temp_dir = tempfile.mkdtemp()
    context.invalid_json_path = os.path.join(context.temp_dir, 'invalid_report.json')

    with open(context.invalid_json_path, 'w') as f:
        f.write('{"invalid": json content}')


@when('I run the allure formatter script directly with the report file')
def step_impl(context):
    allure_script_path = os.path.join(root_project_path, 'behavex', 'outputs', 'formatters', 'allure_behavex_formatter.py')
    execution_args = ['python3', allure_script_path, '--report-path', context.report_json_path]
    execute_command(context, execution_args)


@when('I run the allure formatter script with the invalid JSON file')
def step_impl(context):
    allure_script_path = os.path.join(root_project_path, 'behavex', 'outputs', 'formatters', 'allure_behavex_formatter.py')
    execution_args = ['python3', allure_script_path, '--report-path', context.invalid_json_path]
    execute_command(context, execution_args)


@when('I run the allure formatter script with a non-existent report file')
def step_impl(context):
    allure_script_path = os.path.join(root_project_path, 'behavex', 'outputs', 'formatters', 'allure_behavex_formatter.py')
    non_existent_path = '/path/to/non/existent/report.json'
    execution_args = ['python3', allure_script_path, '--report-path', non_existent_path]
    execute_command(context, execution_args)


@then('I should see that allure-results directory was created')
def step_impl(context):
    # Check for allure-results directory in the output path
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    assert os.path.exists(allure_results_path), f"Allure results directory not found at {allure_results_path}"
    assert os.path.isdir(allure_results_path), f"Expected directory but found file at {allure_results_path}"


@then('I should see that custom allure-results directory "{custom_dir}" was created')
def step_impl(context, custom_dir):
    allure_results_path = os.path.join(context.output_path, custom_dir)
    assert os.path.exists(allure_results_path), f"Custom allure results directory not found at {allure_results_path}"
    assert os.path.isdir(allure_results_path), f"Expected directory but found file at {allure_results_path}"


@then('I should see that allure result files were generated for passing scenarios')
def step_impl(context):
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    result_files = [f for f in os.listdir(allure_results_path) if f.endswith('-result.json')]
    assert len(result_files) > 0, "No result files found in allure-results directory"

    # Verify at least one result file contains passing scenario data
    for result_file in result_files:
        with open(os.path.join(allure_results_path, result_file), 'r') as f:
            result_data = json.load(f)
            if result_data.get('status') == 'passed':
                assert 'uuid' in result_data, "Result file missing uuid"
                assert 'name' in result_data, "Result file missing name"
                assert 'steps' in result_data, "Result file missing steps"
                assert 'labels' in result_data, "Result file missing labels"
                return

    assert False, "No passing scenario found in result files"


@then('I should see that allure result files were generated for failing scenarios')
def step_impl(context):
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    result_files = [f for f in os.listdir(allure_results_path) if f.endswith('-result.json')]
    assert len(result_files) > 0, "No result files found in allure-results directory"

    # Verify at least one result file contains failing scenario data
    for result_file in result_files:
        with open(os.path.join(allure_results_path, result_file), 'r') as f:
            result_data = json.load(f)
            if result_data.get('status') == 'failed':
                assert 'statusDetails' in result_data, "Failed result file missing statusDetails"
                assert 'uuid' in result_data, "Result file missing uuid"
                assert 'name' in result_data, "Result file missing name"
                return

    assert False, "No failing scenario found in result files"


@then('I should see that allure result files were generated for mixed scenarios')
def step_impl(context):
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    result_files = [f for f in os.listdir(allure_results_path) if f.endswith('-result.json')]
    assert len(result_files) > 0, "No result files found in allure-results directory"

    statuses_found = set()
    for result_file in result_files:
        with open(os.path.join(allure_results_path, result_file), 'r') as f:
            result_data = json.load(f)
            statuses_found.add(result_data.get('status'))

    assert len(statuses_found) > 1, f"Expected mixed results but only found statuses: {statuses_found}"


@then('I should see that allure result files were generated in custom directory "{custom_dir}"')
def step_impl(context, custom_dir):
    allure_results_path = os.path.join(context.output_path, custom_dir)
    result_files = [f for f in os.listdir(allure_results_path) if f.endswith('-result.json')]
    assert len(result_files) > 0, f"No result files found in custom directory {allure_results_path}"


@then('I should see that categories.json file was created')
def step_impl(context):
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    categories_file = os.path.join(allure_results_path, 'categories.json')
    assert os.path.exists(categories_file), f"Categories file not found at {categories_file}"

    with open(categories_file, 'r') as f:
        categories_data = json.load(f)
        assert isinstance(categories_data, list), "Categories data should be a list"
        assert len(categories_data) > 0, "Categories list should not be empty"


@then('I should see that categories.json contains Product Defects category')
def step_impl(context):
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    categories_file = os.path.join(allure_results_path, 'categories.json')

    with open(categories_file, 'r') as f:
        categories_data = json.load(f)
        category_names = [cat.get('name') for cat in categories_data]
        assert 'Product Defects' in category_names, f"Product Defects category not found. Found: {category_names}"


@then('I should see that categories.json contains both Product Defects and Broken Tests categories')
def step_impl(context):
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    categories_file = os.path.join(allure_results_path, 'categories.json')

    with open(categories_file, 'r') as f:
        categories_data = json.load(f)
        category_names = [cat.get('name') for cat in categories_data]
        assert 'Product Defects' in category_names, f"Product Defects category not found. Found: {category_names}"
        assert 'Broken Tests' in category_names, f"Broken Tests category not found. Found: {category_names}"


@then('I should see that environment-categories.json file was created')
def step_impl(context):
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    env_categories_file = os.path.join(allure_results_path, 'environment-categories.json')
    assert os.path.exists(env_categories_file), f"Environment categories file not found at {env_categories_file}"


@then('I should see that container files were created')
def step_impl(context):
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    container_files = [f for f in os.listdir(allure_results_path) if f.endswith('-container.json')]
    assert len(container_files) > 0, "No container files found in allure-results directory"

    # Verify container file structure
    for container_file in container_files:
        with open(os.path.join(allure_results_path, container_file), 'r') as f:
            container_data = json.load(f)
            assert 'uuid' in container_data, "Container file missing uuid"
            assert 'children' in container_data, "Container file missing children"


@then('I should see that allure result files contain correct tags and labels')
def step_impl(context):
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    result_files = [f for f in os.listdir(allure_results_path) if f.endswith('-result.json')]

    for result_file in result_files:
        with open(os.path.join(allure_results_path, result_file), 'r') as f:
            result_data = json.load(f)
            assert 'labels' in result_data, "Result file missing labels"

            labels = {label['name']: label['value'] for label in result_data['labels']}
            assert 'framework' in labels, "Framework label missing"
            assert labels['framework'] == 'BehaveX', f"Expected framework=BehaveX, got {labels.get('framework')}"


@then('I should see that epic and story labels are correctly processed')
def step_impl(context):
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    result_files = [f for f in os.listdir(allure_results_path) if f.endswith('-result.json')]

    epic_found = False
    story_found = False

    for result_file in result_files:
        with open(os.path.join(allure_results_path, result_file), 'r') as f:
            result_data = json.load(f)
            labels = {label['name']: label['value'] for label in result_data['labels']}

            if 'epic' in labels:
                epic_found = True
            if 'story' in labels:
                story_found = True

    # At least one of the test scenarios should have epic or story labels if properly tagged
    logging.info(f"Epic found: {epic_found}, Story found: {story_found}")


@then('I should see that severity labels are correctly processed')
def step_impl(context):
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    result_files = [f for f in os.listdir(allure_results_path) if f.endswith('-result.json')]

    for result_file in result_files:
        with open(os.path.join(allure_results_path, result_file), 'r') as f:
            result_data = json.load(f)
            labels = {label['name']: label['value'] for label in result_data['labels']}

            # If severity is present, verify it's valid
            if 'severity' in labels:
                valid_severities = ['blocker', 'critical', 'normal', 'minor', 'trivial']
                assert labels['severity'] in valid_severities, f"Invalid severity: {labels['severity']}"


@then('I should see that allure result files contain table attachments')
def step_impl(context):
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    result_files = [f for f in os.listdir(allure_results_path) if f.endswith('-result.json')]

    table_attachment_found = False
    for result_file in result_files:
        with open(os.path.join(allure_results_path, result_file), 'r') as f:
            result_data = json.load(f)

            # Check for table attachments in steps
            for step in result_data.get('steps', []):
                for attachment in step.get('attachments', []):
                    if attachment.get('name') == '.table' and attachment.get('type') == 'text/csv':
                        table_attachment_found = True
                        break

    assert table_attachment_found, "No table attachments found in result files"


@then('I should see that table data is formatted as CSV')
def step_impl(context):
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    result_files = [f for f in os.listdir(allure_results_path) if f.endswith('-result.json')]

    for result_file in result_files:
        with open(os.path.join(allure_results_path, result_file), 'r') as f:
            result_data = json.load(f)

            # Check for table attachments and verify CSV content
            for step in result_data.get('steps', []):
                for attachment in step.get('attachments', []):
                    if attachment.get('name') == '.table':
                        attachment_file = os.path.join(allure_results_path, attachment['source'])
                        if os.path.exists(attachment_file):
                            with open(attachment_file, 'r') as af:
                                content = af.read()
                                # Basic CSV validation - should contain commas and newlines
                                assert ',' in content or '\n' in content, "Content doesn't appear to be CSV format"


@then('I should see that allure result files contain text attachments')
def step_impl(context):
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    result_files = [f for f in os.listdir(allure_results_path) if f.endswith('-result.json')]

    text_attachment_found = False
    for result_file in result_files:
        with open(os.path.join(allure_results_path, result_file), 'r') as f:
            result_data = json.load(f)

            # Check for text attachments in steps
            for step in result_data.get('steps', []):
                for attachment in step.get('attachments', []):
                    if attachment.get('name') == 'Step Text' and attachment.get('type') == 'text/plain':
                        text_attachment_found = True
                        break

    assert text_attachment_found, "No text attachments found in result files"


@then('I should see that multiline text is properly attached')
def step_impl(context):
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    result_files = [f for f in os.listdir(allure_results_path) if f.endswith('-result.json')]

    for result_file in result_files:
        with open(os.path.join(allure_results_path, result_file), 'r') as f:
            result_data = json.load(f)

            # Check for text attachments and verify content
            for step in result_data.get('steps', []):
                for attachment in step.get('attachments', []):
                    if attachment.get('name') == 'Step Text':
                        attachment_file = os.path.join(allure_results_path, attachment['source'])
                        if os.path.exists(attachment_file):
                            with open(attachment_file, 'r') as af:
                                content = af.read()
                                assert len(content) > 0, "Text attachment is empty"


@then('I should see that the script executes successfully')
def step_impl(context):
    assert context.result.returncode == 0, f"Script failed with exit code {context.result.returncode}. Output: {context.result.stdout}"


@then('I should see that allure result files were generated by the script')
def step_impl(context):
    # The script should generate files in the current directory's output/allure-results
    allure_results_path = os.path.join('output', 'allure-results')
    if os.path.exists(allure_results_path):
        result_files = [f for f in os.listdir(allure_results_path) if f.endswith('-result.json')]
        assert len(result_files) > 0, "No result files found after running script"


@then('I should see that all expected allure files are present')
def step_impl(context):
    allure_results_path = os.path.join('output', 'allure-results')
    if os.path.exists(allure_results_path):
        files = os.listdir(allure_results_path)
        result_files = [f for f in files if f.endswith('-result.json')]
        container_files = [f for f in files if f.endswith('-container.json')]

        assert len(result_files) > 0, "No result files found"
        assert len(container_files) > 0, "No container files found"
        assert 'categories.json' in files, "categories.json not found"


@then('I should see an error message about invalid JSON format')
def step_impl(context):
    assert "Invalid JSON format" in context.result.stdout or "json.JSONDecodeError" in context.result.stderr or "Invalid JSON" in context.result.stderr, f"Expected JSON error message but got: {context.result.stdout}"


@then('I should see an error message about missing report file')
def step_impl(context):
    assert "Could not find report file" in context.result.stdout or "FileNotFoundError" in context.result.stderr or "No such file" in context.result.stderr, f"Expected file not found error but got: {context.result.stdout}"


@then('the script should exit with non-zero code')
def step_impl(context):
    assert context.result.returncode != 0, f"Expected non-zero exit code, but got {context.result.returncode}"


@then('I should see that allure result files do not contain scenario log attachments')
def step_impl(context):
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    result_files = [f for f in os.listdir(allure_results_path) if f.endswith('-result.json')]
    assert len(result_files) > 0, "No result files found in allure-results directory"

    # Check that no result file contains scenario.log attachments
    for result_file in result_files:
        with open(os.path.join(allure_results_path, result_file), 'r') as f:
            result_data = json.load(f)

            # Check attachments at the test case level
            attachments = result_data.get('attachments', [])
            scenario_log_attachments = [att for att in attachments if att.get('name') == 'scenario.log']
            assert len(scenario_log_attachments) == 0, f"Found scenario.log attachment in {result_file} when --no-formatter-attach-logs was used"

            # Also check attachments in steps (just to be thorough)
            steps = result_data.get('steps', [])
            for step in steps:
                step_attachments = step.get('attachments', [])
                step_scenario_log_attachments = [att for att in step_attachments if att.get('name') == 'scenario.log']
                assert len(step_scenario_log_attachments) == 0, f"Found scenario.log attachment in step of {result_file} when --no-formatter-attach-logs was used"

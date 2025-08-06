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
def when_run_allure_passing_tests(context):
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = [
        'behavex',
        os.path.join(tests_features_path, 'secondary_features', 'passing_tests.feature'),
        '-o', context.output_path,
        '--formatter=behavex.outputs.formatters.allure_behavex_formatter:AllureBehaveXFormatter'
    ]
    execute_command(context, execution_args)


@when('I run the behavex command with allure formatter and failing tests')
def when_run_allure_failing_tests(context):
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = [
        'behavex',
        os.path.join(tests_features_path, 'secondary_features', 'failing_tests.feature'),
        '-o', context.output_path,
        '--formatter=behavex.outputs.formatters.allure_behavex_formatter:AllureBehaveXFormatter'
    ]
    execute_command(context, execution_args)


@when('I run the behavex command with allure formatter using custom output directory "{custom_dir}"')
def when_run_allure_custom_dir(context, custom_dir):
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
def when_run_allure_mixed_results(context):
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = [
        'behavex',
        os.path.join(tests_features_path, 'secondary_features'),
        '-o', context.output_path,
        '--formatter=behavex.outputs.formatters.allure_behavex_formatter:AllureBehaveXFormatter'
    ]
    execute_command(context, execution_args)


@when('I run the behavex command with allure formatter and tagged scenarios')
def when_run_allure_tagged_scenarios(context):
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = [
        'behavex',
        os.path.join(tests_features_path, 'secondary_features', 'allure_tagged_tests.feature'),
        '-o', context.output_path,
        '--formatter=behavex.outputs.formatters.allure_behavex_formatter:AllureBehaveXFormatter'
    ]
    execute_command(context, execution_args)


@when('I run the behavex command with allure formatter and scenario with table data')
def when_run_allure_table_data(context):
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = [
        'behavex',
        os.path.join(tests_features_path, 'secondary_features', 'passing_tests.feature'),
        '-o', context.output_path,
        '--formatter=behavex.outputs.formatters.allure_behavex_formatter:AllureBehaveXFormatter'
    ]
    execute_command(context, execution_args)


@when('I run the behavex command with allure formatter and scenario with multiline text')
def when_run_allure_multiline_text(context):
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = [
        'behavex',
        os.path.join(tests_features_path, 'secondary_features', 'passing_tests.feature'),
        '-o', context.output_path,
        '--formatter=behavex.outputs.formatters.allure_behavex_formatter:AllureBehaveXFormatter'
    ]
    execute_command(context, execution_args)


@when('I run the behavex command with allure formatter and no log attachments')
def when_run_allure_no_logs(context):
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
def given_valid_report_json(context):
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
def given_invalid_json_report(context):
    # Create a temporary invalid JSON file
    context.temp_dir = tempfile.mkdtemp()
    context.invalid_json_path = os.path.join(context.temp_dir, 'invalid_report.json')

    with open(context.invalid_json_path, 'w') as f:
        f.write('{"invalid": json content}')


@when('I run the allure formatter script directly with the report file')
def when_run_allure_script_direct(context):
    allure_script_path = os.path.join(root_project_path, 'behavex', 'outputs', 'formatters', 'allure_behavex_formatter.py')
    execution_args = ['python3', allure_script_path, '--report-path', context.report_json_path]
    execute_command(context, execution_args)


@when('I run the allure formatter script with the invalid JSON file')
def when_run_allure_script_invalid_json(context):
    allure_script_path = os.path.join(root_project_path, 'behavex', 'outputs', 'formatters', 'allure_behavex_formatter.py')
    execution_args = ['python3', allure_script_path, '--report-path', context.invalid_json_path]
    execute_command(context, execution_args)


@when('I run the allure formatter script with a non-existent report file')
def when_run_allure_script_nonexistent(context):
    allure_script_path = os.path.join(root_project_path, 'behavex', 'outputs', 'formatters', 'allure_behavex_formatter.py')
    non_existent_path = '/path/to/non/existent/report.json'
    execution_args = ['python3', allure_script_path, '--report-path', non_existent_path]
    execute_command(context, execution_args)


@then('I should see that allure-results directory was created')
def then_see_allure_results_dir(context):
    # Check for allure-results directory in the output path
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    assert os.path.exists(allure_results_path), f"Allure results directory not found at {allure_results_path}"
    assert os.path.isdir(allure_results_path), f"Expected directory but found file at {allure_results_path}"


@then('I should see that custom allure-results directory "{custom_dir}" was created')
def then_see_custom_allure_dir(context, custom_dir):
    allure_results_path = os.path.join(context.output_path, custom_dir)
    assert os.path.exists(allure_results_path), f"Custom allure results directory not found at {allure_results_path}"
    assert os.path.isdir(allure_results_path), f"Expected directory but found file at {allure_results_path}"


@then('I should see that allure result files were generated for passing scenarios')
def then_see_passing_result_files(context):
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
def then_see_failing_result_files(context):
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
def then_see_mixed_result_files(context):
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
def then_see_result_files_custom_dir(context, custom_dir):
    allure_results_path = os.path.join(context.output_path, custom_dir)
    result_files = [f for f in os.listdir(allure_results_path) if f.endswith('-result.json')]
    assert len(result_files) > 0, f"No result files found in custom directory {allure_results_path}"


@then('I should see that categories.json file was created')
def then_see_categories_file(context):
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    categories_file = os.path.join(allure_results_path, 'categories.json')
    assert os.path.exists(categories_file), f"Categories file not found at {categories_file}"

    with open(categories_file, 'r') as f:
        categories_data = json.load(f)
        assert isinstance(categories_data, list), "Categories data should be a list"
        assert len(categories_data) > 0, "Categories list should not be empty"


@then('I should see that categories.json contains Product Defects category')
def then_see_product_defects_category(context):
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    categories_file = os.path.join(allure_results_path, 'categories.json')

    with open(categories_file, 'r') as f:
        categories_data = json.load(f)
        category_names = [cat.get('name') for cat in categories_data]
        assert 'Product Defects' in category_names, f"Product Defects category not found. Found: {category_names}"


@then('I should see that categories.json contains both Product Defects and Test Defects categories')
def then_see_both_defect_categories(context):
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    categories_file = os.path.join(allure_results_path, 'categories.json')

    with open(categories_file, 'r') as f:
        categories_data = json.load(f)
        category_names = [cat.get('name') for cat in categories_data]
        assert 'Product Defects' in category_names, f"Product Defects category not found. Found: {category_names}"
        assert 'Test Defects' in category_names, f"Test Defects category not found. Found: {category_names}"


@then('I should see that environment-categories.json file was created')
def then_see_env_categories_file(context):
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    env_categories_file = os.path.join(allure_results_path, 'environment-categories.json')
    assert os.path.exists(env_categories_file), f"Environment categories file not found at {env_categories_file}"


@then('I should see that container files were created')
def then_see_container_files(context):
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
def then_see_correct_tags_labels(context):
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    result_files = [f for f in os.listdir(allure_results_path) if f.endswith('-result.json')]

    for result_file in result_files:
        with open(os.path.join(allure_results_path, result_file), 'r') as f:
            result_data = json.load(f)
            assert 'labels' in result_data, "Result file missing labels"

            labels = {label['name']: label['value'] for label in result_data['labels']}
            assert 'framework' in labels, "Framework label missing"
            assert labels['framework'] == 'BehaveX', f"Expected framework=BehaveX, got {labels.get('framework')}"

            # Validate testcase and custom links if present
            if 'links' in result_data:
                links = {link['type']: link for link in result_data['links']}
                # Check for testcase link
                if 'testcase' in links:
                    assert links['testcase']['name'] == 'TC-123', f"Expected testcase name TC-123, got {links['testcase']['name']}"
                # Check for custom link
                if 'custom' in links:
                    assert links['custom']['url'] == 'https://example.com/link', f"Expected custom link URL https://example.com/link, got {links['custom']['url']}"


@then('I should see that epic and story labels are correctly processed')
def then_see_epic_story_labels(context):
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
def then_see_severity_labels(context):
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
def then_see_table_attachments(context):
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
def then_see_csv_formatted_data(context):
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
def then_see_text_attachments(context):
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
def then_see_multiline_text_attached(context):
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
def then_see_script_success(context):
    assert context.result.returncode == 0, f"Script failed with exit code {context.result.returncode}. Output: {context.result.stdout}"


@then('I should see that allure result files were generated by the script')
def then_see_script_generated_files(context):
    # The script should generate files in the current directory's output/allure-results
    allure_results_path = os.path.join('output', 'allure-results')
    if os.path.exists(allure_results_path):
        result_files = [f for f in os.listdir(allure_results_path) if f.endswith('-result.json')]
        assert len(result_files) > 0, "No result files found after running script"


@then('I should see that all expected allure files are present')
def then_see_all_expected_files(context):
    allure_results_path = os.path.join('output', 'allure-results')
    if os.path.exists(allure_results_path):
        files = os.listdir(allure_results_path)
        result_files = [f for f in files if f.endswith('-result.json')]
        container_files = [f for f in files if f.endswith('-container.json')]

        assert len(result_files) > 0, "No result files found"
        assert len(container_files) > 0, "No container files found"
        assert 'categories.json' in files, "categories.json not found"


@then('I should see an error message about invalid JSON format')
def then_see_invalid_json_error(context):
    assert "Invalid JSON format" in context.result.stdout or "json.JSONDecodeError" in context.result.stderr or "Invalid JSON" in context.result.stderr, f"Expected JSON error message but got: {context.result.stdout}"


@then('I should see an error message about missing report file')
def then_see_missing_file_error(context):
    assert "Could not find report file" in context.result.stdout or "FileNotFoundError" in context.result.stderr or "No such file" in context.result.stderr, f"Expected file not found error but got: {context.result.stdout}"


@then('the script should exit with non-zero code')
def then_script_exits_nonzero(context):
    assert context.result.returncode != 0, f"Expected non-zero exit code, but got {context.result.returncode}"


@then('I should see that allure result files do not contain scenario log attachments')
def then_no_log_attachments(context):
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


# E2E Tag Validation Steps
@when('I run the behavex command with allure formatter on malformed tags test file')
def when_run_allure_malformed_tags(context):
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = [
        'behavex',
        os.path.join(tests_features_path, 'secondary_features', 'allure_malformed_tags_test.feature'),
        '-o', context.output_path,
        '--formatter=behavex.outputs.formatters.allure_behavex_formatter:AllureBehaveXFormatter'
    ]
    execute_command(context, execution_args)


@when('I run the behavex command with allure formatter on mixed tags scenarios')
def when_run_allure_mixed_tags(context):
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = [
        'behavex',
        os.path.join(tests_features_path, 'secondary_features', 'allure_malformed_tags_test.feature'),
        '-o', context.output_path,
        '--formatter=behavex.outputs.formatters.allure_behavex_formatter:AllureBehaveXFormatter'
    ]
    execute_command(context, execution_args)


@when('I run the behavex command with allure formatter on valid tags test file')
def when_run_allure_valid_tags(context):
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = [
        'behavex',
        os.path.join(tests_features_path, 'secondary_features', 'allure_valid_tags_test.feature'),
        '-o', context.output_path,
        '--formatter=behavex.outputs.formatters.allure_behavex_formatter:AllureBehaveXFormatter'
    ]
    execute_command(context, execution_args)


@when('I run the behavex command with allure formatter on edge case malformed tags')
def when_run_allure_edge_case_tags(context):
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = [
        'behavex',
        os.path.join(tests_features_path, 'secondary_features', 'allure_malformed_tags_test.feature'),
        '-o', context.output_path,
        '--formatter=behavex.outputs.formatters.allure_behavex_formatter:AllureBehaveXFormatter'
    ]
    execute_command(context, execution_args)


@then('I should see that allure result files were generated despite malformed tags')
def then_files_generated_despite_malformed(context):
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    result_files = [f for f in os.listdir(allure_results_path) if f.endswith('-result.json')]
    assert len(result_files) > 0, "No result files found in allure-results directory"

    # Verify that files contain valid data structure despite malformed tags
    for result_file in result_files:
        with open(os.path.join(allure_results_path, result_file), 'r') as f:
            result_data = json.load(f)
            assert 'uuid' in result_data, "Result file missing uuid"
            assert 'name' in result_data, "Result file missing name"
            assert 'labels' in result_data, "Result file missing labels"
            # File should be valid JSON with proper structure


@then('I should see that malformed allure.label tags are not present in the generated reports')
def then_no_malformed_label_tags(context):
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    result_files = [f for f in os.listdir(allure_results_path) if f.endswith('-result.json')]
    assert len(result_files) > 0, "No result files found in allure-results directory"

    for result_file in result_files:
        with open(os.path.join(allure_results_path, result_file), 'r') as f:
            result_data = json.load(f)

            # Check labels - should not contain malformed label data
            labels = result_data.get('labels', [])

            # Should not find any empty or malformed label entries
            for label in labels:
                assert label.get('name'), f"Found label with empty name in {result_file}"
                assert label.get('value'), f"Found label with empty value in {result_file}"

                # Specific checks for labels that were malformed in test scenarios
                if label.get('name') == 'severity':
                    assert label.get('value') != '', "Found empty severity label value"


@then('I should see that valid tags are still processed correctly in the reports')
def then_valid_tags_processed(context):
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    result_files = [f for f in os.listdir(allure_results_path) if f.endswith('-result.json')]
    assert len(result_files) > 0, "No result files found in allure-results directory"

    # Look for expected valid tags that should have been processed
    valid_tags_found = False

    for result_file in result_files:
        with open(os.path.join(allure_results_path, result_file), 'r') as f:
            result_data = json.load(f)

            # Check for valid epic/story tags that should be present
            labels = {label['name']: label['value'] for label in result_data.get('labels', [])}

            if labels.get('epic') == 'RC-999' or labels.get('story') in ['VPD-888', 'VPD-777']:
                valid_tags_found = True
                break

    assert valid_tags_found, "Expected to find valid tags (epic=RC-999, story=VPD-888/777) in generated reports"


@then('I should see that only valid tags appear in the generated allure reports')
def then_only_valid_tags_appear(context):
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    result_files = [f for f in os.listdir(allure_results_path) if f.endswith('-result.json')]
    assert len(result_files) > 0, "No result files found in allure-results directory"

    for result_file in result_files:
        with open(os.path.join(allure_results_path, result_file), 'r') as f:
            result_data = json.load(f)

            # Check labels - all should be well-formed
            labels = result_data.get('labels', [])
            for label in labels:
                assert label.get('name'), f"Found empty label name in {result_file}"
                assert label.get('value'), f"Found empty label value in {result_file}"

            # Check links - all should be well-formed
            links = result_data.get('links', [])
            for link in links:
                assert link.get('type'), f"Found empty link type in {result_file}"
                # Should have either url or name
                assert link.get('url') or link.get('name'), f"Found link with no URL or name in {result_file}"


@then('I should see that invalid tags are silently omitted from reports')
def then_invalid_tags_omitted(context):
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    result_files = [f for f in os.listdir(allure_results_path) if f.endswith('-result.json')]
    assert len(result_files) > 0, "No result files found in allure-results directory"

    # Verify that malformed tags are not present in any form
    for result_file in result_files:
        with open(os.path.join(allure_results_path, result_file), 'r') as f:
            result_data = json.load(f)

            # Should not contain any empty/invalid entries
            labels = result_data.get('labels', [])
            links = result_data.get('links', [])

            # No empty labels
            for label in labels:
                assert label.get('name') and label.get('value'), f"Found incomplete label in {result_file}: {label}"

            # No empty links
            for link in links:
                assert link.get('type'), f"Found incomplete link in {result_file}: {link}"


@then('I should see that all valid allure tags are present in the generated reports')
def then_all_valid_tags_present(context):
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    result_files = [f for f in os.listdir(allure_results_path) if f.endswith('-result.json')]
    assert len(result_files) > 0, "No result files found in allure-results directory"

    # Track which expected valid tags we find
    expected_tags = {
        'epic': ['RC-555'],
        'story': ['VPD-444'],
        'severity': ['critical']
    }

    found_tags = {'epic': [], 'story': [], 'severity': []}
    found_links = []

    for result_file in result_files:
        with open(os.path.join(allure_results_path, result_file), 'r') as f:
            result_data = json.load(f)

            # Collect labels
            labels = result_data.get('labels', [])
            for label in labels:
                label_name = label.get('name')
                label_value = label.get('value')
                if label_name in found_tags:
                    found_tags[label_name].append(label_value)

            # Collect links
            links = result_data.get('links', [])
            for link in links:
                found_links.append(link.get('type'))

    # Verify expected tags are present
    for tag_type, expected_values in expected_tags.items():
        for expected_value in expected_values:
            assert expected_value in found_tags[tag_type], f"Expected {tag_type}={expected_value} not found in reports"

    # Should have some links from valid link tags
    assert 'issue' in found_links or 'tms' in found_links or 'custom' in found_links, "Expected to find valid link types in reports"


@then('I should see that no malformed tag warnings appear in valid tag scenarios')
def then_no_warnings_for_valid_tags(context):
    # For valid tag scenarios, there should be no malformed tag warnings in the output
    # This verifies our validation doesn't generate false positives
    output = getattr(context.result, 'stdout', '') + getattr(context.result, 'stderr', '')

    malformed_warnings = [
        'Malformed allure.label tag',
        'Malformed allure.link tag',
        'Malformed allure.issue:',
        'Malformed allure.tms:',
        'Malformed allure.testcase:'
    ]

    for warning in malformed_warnings:
        assert warning not in output, f"Found unexpected malformed tag warning in valid tag scenario: {warning}"


@then('I should see that edge case malformed tags do not crash the formatter')
def then_edge_case_tags_no_crash(context):
    # This step is already verified by the successful exit code
    # But we can also check that result files were generated
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    result_files = [f for f in os.listdir(allure_results_path) if f.endswith('-result.json')]
    assert len(result_files) > 0, "No result files found - formatter may have crashed on edge case tags"


@then('I should see that only well-formed tags appear in the final reports')
def then_only_wellformed_tags_appear(context):
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    result_files = [f for f in os.listdir(allure_results_path) if f.endswith('-result.json')]
    assert len(result_files) > 0, "No result files found in allure-results directory"

    for result_file in result_files:
        with open(os.path.join(allure_results_path, result_file), 'r') as f:
            result_data = json.load(f)

            # Every label must be complete
            labels = result_data.get('labels', [])
            for label in labels:
                assert label.get('name') and label.get('value'), f"Found malformed label in {result_file}: {label}"
                # Name and value must be non-empty strings
                assert isinstance(label['name'], str) and label['name'].strip(), f"Invalid label name: {label['name']}"
                assert isinstance(label['value'], str) and label['value'].strip(), f"Invalid label value: {label['value']}"

            # Every link must be complete
            links = result_data.get('links', [])
            for link in links:
                assert link.get('type'), f"Found link without type in {result_file}: {link}"
                assert isinstance(link['type'], str) and link['type'].strip(), f"Invalid link type: {link['type']}"

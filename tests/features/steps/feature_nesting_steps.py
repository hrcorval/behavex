import os
import shutil
import subprocess
import tempfile

from behave import given, then, when
from bs4 import BeautifulSoup

from behavex.runner import run


@given('I have created feature files with same tags but different names')
def step_create_feature_files(context):
    # Create temporary directory for test features
    context.temp_dir = tempfile.mkdtemp()
    context.output_dir = tempfile.mkdtemp()

    # Create feature files with same tag but different names
    feature_1_content = """@test_A
Feature: Test A part 1

Background:
  Given some common setup for Test A part 1

@scenario11
Scenario: Scenario 11
  Given I am on the first part page
  When I click on the first button
  Then I should see the first result

@scenario12
Scenario: Scenario 12
  Given I am on the first part page
  When I click on the second button
  Then I should see the second result
"""

    feature_2_content = """@test_A
Feature: Test A part 2

@scenario21
Scenario: Scenario 21
  Given I am on the second part page
  When I click on the first button
  Then I should see the third result

@scenario22
Scenario: Scenario 22
  Given I am on the second part page
  When I click on the second button
  Then I should see the fourth result
"""

    feature_3_content = """@test_A
Feature: Test A part 3

@scenario31
Scenario: Scenario 31
  Given I am on the third part page
  When I click on the first button
  Then I should see the fifth result

@scenario32
Scenario: Scenario 32
  Given I am on the third part page
  When I click on the second button
  Then I should see the sixth result
"""

    # Write feature files
    with open(os.path.join(context.temp_dir, 'test_a_part_1.feature'), 'w') as f:
        f.write(feature_1_content)

    with open(os.path.join(context.temp_dir, 'test_a_part_2.feature'), 'w') as f:
        f.write(feature_2_content)

    with open(os.path.join(context.temp_dir, 'test_a_part_3.feature'), 'w') as f:
        f.write(feature_3_content)

    # Create steps directory and step definitions
    steps_dir = os.path.join(context.temp_dir, 'steps')
    os.makedirs(steps_dir)

    steps_content = """from behave import given, when, then

@given('some common setup for Test A part 1')
def step_impl(context):
    pass

@given('I am on the first part page')
def step_impl(context):
    pass

@given('I am on the second part page')
def step_impl(context):
    pass

@given('I am on the third part page')
def step_impl(context):
    pass

@when('I click on the first button')
def step_impl(context):
    pass

@when('I click on the second button')
def step_impl(context):
    pass

@then('I should see the first result')
def step_impl(context):
    pass

@then('I should see the second result')
def step_impl(context):
    pass

@then('I should see the third result')
def step_impl(context):
    pass

@then('I should see the fourth result')
def step_impl(context):
    pass

@then('I should see the fifth result')
def step_impl(context):
    pass

@then('I should see the sixth result')
def step_impl(context):
    pass
"""

    with open(os.path.join(steps_dir, '__init__.py'), 'w') as f:
        f.write('# Step definitions for feature nesting test')

    with open(os.path.join(steps_dir, 'nesting_test_steps.py'), 'w') as f:
        f.write(steps_content)


@when('I run BehaveX on these feature files with parallel scenario execution')
def step_run_parallel_scenario(context):
    context.execution_mode = 'parallel_scenario'
    _run_behavex(context, ['--parallel-processes=2', '--parallel-scheme=scenario'])


@when('I run BehaveX on these feature files with parallel feature execution')
def step_run_parallel_feature(context):
    context.execution_mode = 'parallel_feature'
    _run_behavex(context, ['--parallel-processes=2', '--parallel-scheme=feature'])


@when('I run BehaveX on these feature files with single process execution')
def step_run_single_process(context):
    context.execution_mode = 'single_process'
    _run_behavex(context, ['--parallel-processes=1'])


def _run_behavex(context, extra_args):
    # Run BehaveX with the specified arguments
    cmd = ['python', '-m', 'behavex', context.temp_dir, '-o', context.output_dir] + extra_args
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=context.temp_dir)
    context.behavex_result = result
    context.html_report_path = os.path.join(context.output_dir, 'report.html')


@then('I should see features displayed flat in the HTML report')
def step_check_flat_display(context):
    # Parse the HTML report and check structure
    assert os.path.exists(context.html_report_path), f"HTML report not found at {context.html_report_path}"

    with open(context.html_report_path, 'r') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all feature rows (these should be at the same level)
    feature_rows = soup.find_all('tr', {'class': lambda x: x and 'data_feature' in x})

    # Should have exactly 3 feature rows
    assert len(feature_rows) == 3, f"Expected 3 feature rows, found {len(feature_rows)}"

    # Extract feature names
    feature_names = []
    for row in feature_rows:
        feature_name_span = row.find('span', {'data-feature': True})
        if feature_name_span:
            feature_name = feature_name_span.find('b').text.strip()
            feature_names.append(feature_name)

    context.feature_names = feature_names

    # Should contain all expected feature names
    expected_names = ['Test A part 1', 'Test A part 2', 'Test A part 3']
    for name in expected_names:
        assert name in feature_names, f"Feature '{name}' not found in feature list: {feature_names}"


@then('I should not see features nested within other features')
def step_check_no_nesting(context):
    # Check that no feature rows are nested inside other feature rows
    with open(context.html_report_path, 'r') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all feature containers
    feature_containers = soup.find_all('tr', {'data-feature-id': True})

    # Check that none of these containers contain other feature rows
    for container in feature_containers:
        nested_features = container.find_all('tr', {'class': lambda x: x and 'data_feature' in x})
        # A container might contain the feature row itself, but not additional feature rows
        assert len(nested_features) <= 1, f"Found nested features within a feature container: {[f.text for f in nested_features]}"


@then('each feature should have its own row in the summary table')
def step_check_summary_table(context):
    # Verify that each feature has its own row in the main summary table
    with open(context.html_report_path, 'r') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the summary table
    summary_table = soup.find('table', {'id': 'summary'})
    assert summary_table is not None, "Summary table not found"

    # Count feature rows in summary table
    feature_rows = summary_table.find_all('tr', {'class': lambda x: x and 'data_feature' in x})
    assert len(feature_rows) == 3, f"Expected 3 feature rows in summary table, found {len(feature_rows)}"

    # Clean up temp directories
    if hasattr(context, 'temp_dir'):
        shutil.rmtree(context.temp_dir, ignore_errors=True)
    if hasattr(context, 'output_dir'):
        shutil.rmtree(context.output_dir, ignore_errors=True)

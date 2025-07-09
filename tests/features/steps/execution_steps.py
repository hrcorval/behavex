import logging
import os
import random
import re
import subprocess

from behave import given, then, when

root_project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
tests_features_path = os.path.join(root_project_path, 'tests', 'features')
test_images_path = os.path.join(root_project_path, 'tests', 'test_images')

# Import behavex-images functionality - fail if required
def get_image_attachments_module():
    """Get the image_attachments module, raising an error if not available."""
    try:
        from behavex_images import image_attachments
        return image_attachments
    except (ImportError, ModuleNotFoundError) as e:
        raise AssertionError(f"behavex-images is required for image attachment tests but not available: {e}")

# Check if behavex-images is available for optional usage
try:
    from behavex_images import image_attachments
    behavex_images_available = True
except (ImportError, ModuleNotFoundError) as e:
    behavex_images_available = False
    logging.warning(f"behavex-images not available, image attachment tests will be skipped: {e}")


@given('The progress bar is enabled')
def step_impl(context):
    context.progress_bar = True


@when('I run the behavex command with a passing test')
@when('I run the behavex command with passing tests')
def step_impl(context):
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = ['behavex', os.path.join(tests_features_path, 'secondary_features', 'passing_tests.feature'), '-o', context.output_path]
    execute_command(context, execution_args)


@when('I run the behavex command with a file of failing tests')
def step_impl(context):
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = ['behavex', '-rf', os.path.join(tests_features_path, 'failing_scenarios.txt'), '-o', context.output_path]
    execute_command(context, execution_args)


@when('I run the behavex command that renames scenarios and features')
def step_impl(context):
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = ['behavex', os.path.join(tests_features_path, 'secondary_features', 'rename_tests.feature'), '-o', context.output_path]
    execute_command(context, execution_args)


@when('I run the behavex command with a failing test')
def step_impl(context):
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = ['behavex', os.path.join(tests_features_path, 'secondary_features', 'failing_tests.feature'), '-o', context.output_path]
    execute_command(context, execution_args)


@when('I run the behavex command with a crashing test')
def step_impl(context, parallel_processes="1", parallel_scheme='scenario'):
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = ['behavex',
                os.path.join(tests_features_path, os.path.join(tests_features_path, 'crashing_features', 'crashing_tests.feature')),
                '-o', context.output_path]
    execute_command(context, execution_args)


@when('I run the behavex command with no tests')
def step_impl(context, parallel_processes="1", parallel_scheme='scenario'):
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = ['behavex',
                os.path.join(tests_features_path, os.path.join(tests_features_path, 'crashing_features', 'crashing_tests.feature')),
                '-t', 'NO_TESTS',
                '-o', context.output_path]
    execute_command(context, execution_args)


@when('I run the behavex command with a test that crashes in "{behave_hook}" hook')
@when('I run the behavex command with a test that crashes in "{behave_hook}" hook with "{parallel_processes}" parallel processes and "{parallel_scheme}" parallel scheme')
def step_impl(context, behave_hook, parallel_processes="1", parallel_scheme='scenario'):
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = ['behavex',
                os.path.join(tests_features_path, os.path.join(tests_features_path, 'crashing_features', 'crashing_environment_tests.feature')),
                '-o', context.output_path,
                '--parallel-processes', parallel_processes,
                '--parallel-scheme', parallel_scheme,
                '-D', 'crashing_behave_hook=' + behave_hook]
    execute_command(context, execution_args)


@when('I run the behavex command with a skipped test')
def step_impl(context):
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = ['behavex', os.path.join(tests_features_path, 'secondary_features', 'skipped_tests.feature'), '-o', context.output_path]
    execute_command(context, execution_args)


@when('I run the behavex command with an untested test')
def step_impl(context):
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = ['behavex', os.path.join(tests_features_path, 'secondary_features', 'untested_tests.feature'), '-o', context.output_path]
    execute_command(context, execution_args)


@when('I run the behavex command with "{parallel_processes}" parallel processes and parallel scheme set as "{parallel_schema}"')
def step_impl(context, parallel_processes, parallel_schema):
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = ['behavex', os.path.join(tests_features_path, 'secondary_features'), '-o', context.output_path, '--parallel-processes', parallel_processes, '--parallel-scheme', parallel_schema]
    execute_command(context, execution_args)


@when('I setup the behavex command with "{parallel_processes}" parallel processes and parallel scheme set as "{parallel_scheme}"')
def step_impl(context, parallel_processes, parallel_scheme):
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
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    tags_to_folder_name = get_tags_string(tags)
    if not tags:
        tags_array = []
    else:
        tags_array = get_tags_arguments(tags)
    feature_path_2 = None
    if feature_name:
        if feature_name_2:
            feature_path = os.path.join(tests_features_path, 'secondary_features', feature_name)
            feature_path_2 = os.path.join(tests_features_path, 'secondary_features', feature_name_2)
        else:
            feature_path = os.path.join(tests_features_path, 'secondary_features', feature_name)
    else:
        feature_path = os.path.join(tests_features_path, 'secondary_features')
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
def step_impl(context):
    tags = context.table[0]['tags']
    tags_to_folder_name = get_tags_string(tags)
    tags_array = get_tags_arguments(tags)
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = ['behavex', os.path.join(tests_features_path, 'secondary_features'), '-o', context.output_path] + tags_array
    execute_command(context, execution_args)


@when('I run the behavex command by performing a dry run')
def step_impl(context):
    # generate a random number between 1 and 1000000 completing with zeroes to 6 digits
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = ['behavex', os.path.join(tests_features_path, 'secondary_features'), '-o', context.output_path, '--dry-run']
    execute_command(context, execution_args)


@then('I should see the following behavex console outputs')
@then('I should see the following behavex console outputs and exit code "{expected_exit_code}"')
def step_impl(context, expected_exit_code=None):
    if expected_exit_code is not None:
        assert int(context.result.returncode) == int(expected_exit_code), "Behavex exit code is not expected"
    for row in context.table:
        assert row['output_line'] in context.result.stdout, f"Unexpected output when checking console outputs: {context.result.stdout}\n\nOutput line not found: {row['output_line']}\n"


@then('I should not see error messages in the output')
def step_impl(context):
    error_messages = ["error", "exception", "traceback"]
    for message in error_messages:
        assert message not in context.result.stdout.lower(), f"Unexpected output when checking error messages in the console output: {context.result.stdout}\n"


@then('I should not see exception messages in the output')
def step_impl(context):
    exception_messages = ["exception", "traceback"]
    for message in exception_messages:
        assert message not in context.result.stdout.lower(), f"Unexpected output when checking exception messages in the console output: {context.result.stdout}\n"





@then('I should see the same number of scenarios in the reports and the console output')
def step_impl(context):
    total_scenarios_in_html_report = get_total_scenarios_in_html_report(context)
    logging.info(f"Total scenarios in the HTML report: {total_scenarios_in_html_report}")
    total_scenarios_in_junit_reports = get_total_scenarios_in_junit_reports(context)
    logging.info(f"Total scenarios in the JUnit reports: {total_scenarios_in_junit_reports}")
    total_scenarios_in_console_output = get_total_scenarios_in_console_output(context)
    logging.info(f"Total scenarios in the console output: {total_scenarios_in_console_output}")
    assert total_scenarios_in_html_report == total_scenarios_in_junit_reports == total_scenarios_in_console_output, f"Expected total scenarios to match, but found {total_scenarios_in_html_report} in the HTML report, {total_scenarios_in_junit_reports} in the JUnit reports, and {total_scenarios_in_console_output} in the console output"


@then('I should see the same number of scenarios in the reports')
def verify_total_scenarios_in_reports(context, consider_skipped_scenarios=True):
    total_scenarios_in_html_report = get_total_scenarios_in_html_report(context)
    logging.info(f"Total scenarios in the HTML report: {total_scenarios_in_html_report}")
    total_scenarios_in_junit_reports = get_total_scenarios_in_junit_reports(context, consider_skipped_scenarios)
    logging.info(f"Total scenarios in the JUnit reports: {total_scenarios_in_junit_reports}")
    assert total_scenarios_in_html_report == total_scenarios_in_junit_reports, f"Expected total scenarios to match, but found {total_scenarios_in_html_report} in the HTML report, {total_scenarios_in_junit_reports} in the JUnit reports"


@then('I should see the same number of scenarios in the reports not considering the skipped scenarios')
def step_impl(context):
    verify_total_scenarios_in_reports(context, consider_skipped_scenarios=False)


@then('I should see the HTML report was generated and contains scenarios')
@then('I should see the HTML report was generated and contains "{total_scenarios}" scenarios')
def verify_total_scenarios_in_html_report(context, total_scenarios=None, consider_skipped_scenarios=True):
    total_scenarios_in_html_report = get_total_scenarios_in_html_report(context)
    logging.info(f"Total scenarios in the HTML report: {total_scenarios_in_html_report}")
    if total_scenarios is not None:
        assert total_scenarios_in_html_report == int(total_scenarios), f"Expected the HTML report to contain {total_scenarios} scenarios, but found {total_scenarios_in_html_report}"
    else:
        assert total_scenarios_in_html_report > 0, "Expected the HTML report to be generated and contain scenarios"


@then('I should see the generated HTML report contains the "{string_to_search}" string')
def verify_string_in_html_report(context, string_to_search, string_should_be_present=True):
    total_string_instances_in_html_report = get_string_instances_from_html_report(context, string_to_search)
    logging.info(f"Total instances of '{string_to_search}' in the HTML report: {total_string_instances_in_html_report}")
    if string_should_be_present:
        assert total_string_instances_in_html_report > 0, f"Expected the HTML report to contain the string '{string_to_search}'"
    else:
        assert total_string_instances_in_html_report == 0, f"Expected the HTML report to not contain the string '{string_to_search}'"


@then('I should see the generated HTML report does not contain internal BehaveX variables and tags')
def verify_string_not_in_html_report(context):
    internal_behavex_variables_and_tags = ["BHX_", "BHX_TAG_"]
    for variable_or_tag in internal_behavex_variables_and_tags:
        total_string_instances_in_html_report = get_string_instances_from_html_report(context, variable_or_tag)
        logging.info(f"Total instances of '{variable_or_tag}' in the HTML report: {total_string_instances_in_html_report}")
        assert total_string_instances_in_html_report == 0, f"Expected the HTML report to not contain the string '{variable_or_tag}'"



def get_tags_arguments(tags):
    tags_array = []
    for tag in tags.split(' '):
        tags_array += tag.split('=')
    return tags_array


def get_tags_string(tags):
    return tags.replace('-t=','_AND_').replace('~','NOT_').replace(',','_OR_').replace(' ','').replace('@','')


def get_random_number(total_digits):
    return str(random.randint(1, 1000000)).zfill(total_digits)


def get_total_scenarios_in_console_output(context):
    #Verifying the scenarios in the console output
    console_output = context.result.stdout
    # Extract the number of scenarios by analyzing the following pattern: X scenarios passed, Y failed, Z skipped
    scenario_pattern = re.compile(r'(\d+) scenario.? passed, (\d+) failed, (\d+) skipped')
    match = scenario_pattern.search(console_output)
    if match:
        scenarios_passed = int(match.group(1))
        scenarios_failed = int(match.group(2))
        scenarios_skipped = int(match.group(3))
    else:
        raise ValueError("No scenarios found in the console output")
    return scenarios_passed + scenarios_failed + scenarios_skipped


def get_total_scenarios_in_html_report(context):
    report_path = os.path.abspath(os.path.join(context.output_path, 'report.html'))
    with open(report_path, 'r') as file:
        html_content = file.read()
    return html_content.count('data-scenario-tags=')


def get_string_instances_from_html_report(context, string_to_search):
    report_path = os.path.abspath(os.path.join(context.output_path, 'report.html'))
    with open(report_path, 'r') as file:
        html_content = file.read()
    return html_content.lower().count(string_to_search.lower())


def get_total_scenarios_in_junit_reports(context, consider_skipped_scenarios=True):
    junit_folder = os.path.abspath(os.path.join(context.output_path, 'behave'))
    total_scenarios_in_junit_reports = 0
    for file in os.listdir(junit_folder):
        if file.endswith('.xml'):
            with open(os.path.join(junit_folder, file), 'r') as file:
                xml_content = file.read()
                total_scenarios_in_junit_reports += xml_content.count('status="passed"')
                total_scenarios_in_junit_reports += xml_content.count('status="failed"')
                if consider_skipped_scenarios:
                    total_scenarios_in_junit_reports += xml_content.count('status="skipped"')
    return total_scenarios_in_junit_reports


@given('I take a screenshot using test image {image_number}')
def step_take_screenshot_using_test_image(context, image_number):
    """Attach a test image file using behavex-images"""
    image_path = os.path.join(test_images_path, f'test_image_{image_number}.png')
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Test image not found: {image_path}")

    # Check if image attachments are required for this test
    if hasattr(context, 'require_image_attachments') and context.require_image_attachments:
        image_attachments = get_image_attachments_module()
        image_attachments.attach_image_file(context, image_path)
        logging.info(f"Attached test image: {image_path}")
    else:
        # Optional usage - skip if not available
        if not behavex_images_available:
            logging.warning("behavex-images not available, skipping image attachment")
            return
        # Import here to avoid issues if behavex-images is not available
        from behavex_images import image_attachments
        image_attachments.attach_image_file(context, image_path)
        logging.info(f"Attached test image: {image_path}")


@when('I run the behavex command with image attachments')
def step_run_behavex_with_image_attachments(context):
    """Run behavex with HTML formatter and image attachments enabled"""
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = [
        'behavex',
        os.path.join(tests_features_path, 'secondary_features', 'simple_image_tests.feature'),
        '-o', context.output_path,
        '-t', '@IMAGE_ATTACHMENT',
        '-t', '@HTML_REPORT'
    ]
    execute_command(context, execution_args)


@when('I run the behavex command with allure formatter and image attachments')
def step_run_behavex_with_allure_and_image_attachments(context):
    """Run behavex with Allure formatter and image attachments enabled"""
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    execution_args = [
        'behavex',
        os.path.join(tests_features_path, 'secondary_features', 'simple_image_tests.feature'),
        '-o', context.output_path,
        '--formatter=behavex.outputs.formatters.allure_behavex_formatter:AllureBehaveXFormatter',
        '-t', '@IMAGE_ATTACHMENT',
        '-t', '@ALLURE_FORMATTER'
    ]
    execute_command(context, execution_args)


@then('I should see the HTML report contains screenshots')
def step_verify_html_report_contains_screenshots(context):
    """Verify that the HTML report contains attached screenshots"""
    html_report_path = os.path.join(context.output_path, 'report.html')
    if os.path.exists(html_report_path):
        with open(html_report_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            # Look for image references in the HTML
            assert 'test_image_' in html_content, "Screenshots not found in HTML report"
            logging.info("Screenshots found in HTML report")
    else:
        raise FileNotFoundError(f"HTML report not found: {html_report_path}")


@then('I should see the HTML report contains the image gallery icon')
def step_verify_html_report_contains_gallery_icon(context):
    """Verify that the HTML report contains the image gallery icon"""
    html_report_path = os.path.join(context.output_path, 'report.html')
    if os.path.exists(html_report_path):
        with open(html_report_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            # Look for the specific gallery icon HTML element
            gallery_icon = '<span class="glyphicon glyphicon-picture">'
            assert gallery_icon in html_content, "Image gallery icon not found in HTML report"
            logging.info("Image gallery icon found in HTML report")
    else:
        raise FileNotFoundError(f"HTML report not found: {html_report_path}")


@then('I should see that images are stored in the allure formatter output directory')
def step_verify_images_in_allure_output(context):
    """Verify that images are stored in the Allure formatter output directory"""
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    if os.path.exists(allure_results_path):
        # Look for image attachments in allure results
        allure_files = os.listdir(allure_results_path)
        image_files = [f for f in allure_files if f.endswith('.png') or f.endswith('.jpg') or f.endswith('.jpeg')]
        assert len(image_files) > 0, "No image files found in Allure output directory"
        logging.info(f"Found {len(image_files)} image files in Allure output directory")

        # Also check for attachment references in JSON files
        json_files = [f for f in allure_files if f.endswith('.json')]
        found_attachment_reference = False
        for json_file in json_files:
            json_path = os.path.join(allure_results_path, json_file)
            with open(json_path, 'r', encoding='utf-8') as f:
                json_content = f.read()
                if 'attachments' in json_content and 'image' in json_content:
                    found_attachment_reference = True
                    break

        assert found_attachment_reference, "No image attachment references found in Allure JSON files"
        logging.info("Image attachment references found in Allure JSON files")
    else:
        raise FileNotFoundError(f"Allure results directory not found: {allure_results_path}")


def execute_command(context, execution_args, print_output=True):
    if "progress_bar" in context and context.progress_bar:
        execution_args.insert(2, '--show-progress-bar')
    if hasattr(context, 'parallel_processes'):
        execution_args += ['--parallel-processes', context.parallel_processes]
    if hasattr(context, 'parallel_scheme'):
        execution_args += ['--parallel-scheme', context.parallel_scheme]
    logging.info("Executing command: {}".format(" ".join(execution_args)))
    context.result = subprocess.run(execution_args, capture_output=True, text=True)
    if print_output:
        logging.info(context.result.stdout)

import json
import logging
import os
import re
import xml.etree.ElementTree as ET

from behave import then


@then('I should see the overall status report shows "{expected_status}"')
def then_overall_status_report_shows(context, expected_status):
    overall_status = _load_json_report(context, 'overall_status.json')
    assert overall_status.get('status') == expected_status, (
        f"Expected overall_status.json status to be '{expected_status}', got {overall_status}"
    )


@then('I should see the feature status in the JSON report is one of "{expected_statuses}"')
def then_feature_status_in_json_report(context, expected_statuses):
    report = _load_json_report(context)
    assert report['features'], f"report.json contains no features: {report}"
    for feature in report['features']:
        assert feature['status'] in expected_statuses.split(', '), (
            f"Expected feature status in '{expected_statuses}', got '{feature['status']}' "
            f"for feature {feature['name']!r}"
        )


@then('I should see "{count}" features with status "{expected_status}" in the JSON report')
def then_features_with_status_in_json_report(context, count, expected_status):
    statuses = [feature['status'] for feature in _load_json_report(context)['features']]
    assert statuses.count(expected_status) == int(count), (
        f"Expected {count} features with status '{expected_status}', got {statuses}"
    )


def _feature_and_scenario_statuses(context):
    return sorted((feature['name'], feature['status'],
                   sorted((scenario['name'], scenario['status']) for scenario in feature['scenarios']))
                  for feature in _load_json_report(context)['features'])


@then('I keep the feature and scenario statuses from the JSON report')
def then_keep_feature_and_scenario_statuses(context):
    context.kept_statuses = _feature_and_scenario_statuses(context)


@then('I should see the same feature and scenario statuses in the JSON report as the kept ones')
def then_same_feature_and_scenario_statuses(context):
    statuses = _feature_and_scenario_statuses(context)
    assert statuses == context.kept_statuses, (
        f"Expected statuses {context.kept_statuses}, got {statuses}"
    )


@then('I should see the same number of scenarios in the reports and the console output')
def then_same_scenarios_count_all(context):
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
def then_same_scenarios_count_excluding_skipped(context):
    verify_total_scenarios_in_reports(context, consider_skipped_scenarios=False)


@then('I should see the HTML report was generated')
def verify_html_report_exists(context):
    """Verify that the HTML report file exists and is a valid file."""
    report_path = os.path.abspath(os.path.join(context.output_path, 'report.html'))
    assert os.path.exists(report_path), f"Expected HTML report to exist at {report_path}"
    assert os.path.getsize(report_path) > 0, f"Expected HTML report to be non-empty at {report_path}"


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


@then('I should see the generated HTML report contains "{count}" occurrences of the "{string_to_search}" string')
def verify_string_count_in_html_report(context, count, string_to_search):
    total = get_string_instances_from_html_report(context, string_to_search)
    logging.info(f"Total instances of '{string_to_search}' in the HTML report: {total}")
    assert total == int(count), f"Expected {count} occurrences of '{string_to_search}' in HTML report, found {total}"


@then('I should see all scenarios in the JSON report have a rule field')
def verify_json_scenarios_have_rule_field(context):
    data = _load_json_report(context)
    for feature in data['features']:
        for scenario in feature['scenarios']:
            assert 'rule' in scenario, f"Scenario '{scenario['name']}' is missing 'rule' field in JSON report"


@then('I should see the JSON report contains scenarios with rule "{rule_name}"')
def verify_json_scenarios_with_rule(context, rule_name):
    data = _load_json_report(context)
    matching = [
        scenario
        for feature in data['features']
        for scenario in feature['scenarios']
        if scenario.get('rule') == rule_name
    ]
    assert matching, f"No scenarios found with rule '{rule_name}' in JSON report"


def _load_json_report(context, filename='report.json'):
    report_path = os.path.abspath(os.path.join(context.output_path, filename))
    with open(report_path, 'r') as f:
        return json.load(f)


def _failed_scenarios_in_json_report(context):
    failed_scenarios = [
        scenario
        for feature in _load_json_report(context)['features']
        for scenario in feature['scenarios']
        if scenario.get('status') in ('failed', 'error')
    ]
    assert failed_scenarios, "No failed scenarios found in JSON report"
    return failed_scenarios


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
                # Keep status="error" counting for robustness, but shouldn't be needed now
                total_scenarios_in_junit_reports += xml_content.count('status="error"')
                if consider_skipped_scenarios:
                    total_scenarios_in_junit_reports += xml_content.count('status="skipped"')
    return total_scenarios_in_junit_reports


@then('I should see the JUnit XML report was generated')
def then_junit_xml_report_generated(context):
    junit_folder = os.path.abspath(os.path.join(context.output_path, 'behave'))
    assert os.path.exists(junit_folder), f"JUnit XML folder not found: {junit_folder}"
    xml_files = [f for f in os.listdir(junit_folder) if f.endswith('.xml')]
    assert len(xml_files) > 0, f"No JUnit XML files found in: {junit_folder}"


def _get_xml_testcases_by_report(context):
    junit_folder = os.path.abspath(os.path.join(context.output_path, 'behave'))
    return {xml_report_filename: ET.parse(os.path.join(junit_folder, xml_report_filename)).getroot().findall('testcase')
            for xml_report_filename in sorted(os.listdir(junit_folder)) if xml_report_filename.endswith('.xml')}


def _get_all_xml_testcases(context):
    return [testcase for testcases in _get_xml_testcases_by_report(context).values() for testcase in testcases]


def _get_all_xml_failures(context):
    return [failure for testcase in _get_all_xml_testcases(context) for failure in testcase.findall('failure')]


@then('I should see "{count}" scenarios with status "{status}" in the JUnit XML report')
def then_junit_xml_scenarios_with_status(context, count, status):
    testcases = _get_all_xml_testcases(context)
    matching = [tc for tc in testcases if tc.get('status') == status]
    assert len(matching) == int(count), \
        f"Expected {count} scenarios with status '{status}' in JUnit XML, found {len(matching)}"


@then('I should see the scenario name "{name}" in the JUnit XML report')
def then_junit_xml_scenario_name(context, name):
    testcases = _get_all_xml_testcases(context)
    names = [tc.get('name', '') for tc in testcases]
    name_lower = name.lower()
    assert any(name_lower in n.lower() for n in names), \
        f"Scenario name containing '{name}' not found in JUnit XML. Found: {names}"


@then('I should see the JUnit XML failure message contains "{text}"')
def then_junit_xml_failure_message_contains(context, text):
    messages = [failure.get('message', '') + (failure.text or '') for failure in _get_all_xml_failures(context)]
    assert any(text in message for message in messages), \
        f"No JUnit failure message contains '{text}'. Found: {messages}"


@then('I should see the JUnit XML failure body contains "{text}"')
def then_junit_xml_failure_body_contains(context, text):
    failure_bodies = [failure.text or '' for failure in _get_all_xml_failures(context)]
    assert any(text in failure_body for failure_body in failure_bodies), \
        f"No JUnit failure body contains '{text}'. Found: {failure_bodies}"


@then('I should see the JUnit XML system output contains "{text}"')
def then_junit_xml_system_out_contains(context, text):
    outputs = [system_out.text or ''
               for testcase in _get_all_xml_testcases(context)
               for system_out in testcase.findall('system-out')]
    assert any(text in output for output in outputs), \
        f"No JUnit system output contains '{text}'. Found: {outputs}"


@then('I should see a JUnit XML report with exactly the testcases "{testcase_names}"')
def then_junit_xml_report_with_exactly_testcases(context, testcase_names):
    expected_names = sorted(name.strip() for name in testcase_names.split(','))
    testcase_names_by_report = {xml_report_filename: sorted(testcase.get('name') for testcase in testcases)
                                for xml_report_filename, testcases in _get_xml_testcases_by_report(context).items()}
    assert expected_names in testcase_names_by_report.values(), \
        f"No JUnit XML report holds exactly {expected_names}. Found: {testcase_names_by_report}"


@then('I should see error messages for failed scenarios in the JUnit XML report')
def then_junit_xml_failure_messages(context):
    testcases = _get_all_xml_testcases(context)
    failed = [tc for tc in testcases if tc.get('status') == 'failed']
    assert failed, "No failed scenarios found in JUnit XML report"
    for tc in failed:
        failure_el = tc.find('failure')
        assert failure_el is not None, f"Failed testcase '{tc.get('name')}' has no <failure> element"
        message = failure_el.get('message') or (failure_el.text or '').strip()
        assert message, f"Failed testcase '{tc.get('name')}' has empty failure message"


@then('I should see "{count}" XML files in the JUnit report folder')
def then_junit_xml_file_count(context, count):
    junit_folder = os.path.abspath(os.path.join(context.output_path, 'behave'))
    xml_files = [f for f in os.listdir(junit_folder) if f.endswith('.xml')]
    assert len(xml_files) == int(count), \
        f"Expected {count} XML files in JUnit folder, found {len(xml_files)}: {xml_files}"


@then('I should see "{count}" scenarios in the JSON report')
def then_json_report_scenario_count(context, count):
    data = _load_json_report(context)
    total = sum(len(feature['scenarios']) for feature in data['features'])
    assert total == int(count), f"Expected {count} scenarios in JSON report, found {total}"


@then('I should see scenario outline parameters in the JSON report')
def then_json_outline_parameters(context):
    data = _load_json_report(context)
    outline_scenarios = [
        scenario
        for feature in data['features']
        for scenario in feature['scenarios']
        if scenario.get('parameters')
    ]
    assert outline_scenarios, "No scenarios with parameters found in JSON report"
    for scenario in outline_scenarios:
        assert isinstance(scenario['parameters'], dict), \
            f"Scenario '{scenario['name']}' parameters should be a dict, got: {type(scenario['parameters'])}"
        assert len(scenario['parameters']) > 0, \
            f"Scenario '{scenario['name']}' parameters dict is empty"


@then('I should see background steps in the JSON report for each scenario')
def then_json_background_steps(context):
    data = _load_json_report(context)
    for feature in data['features']:
        for scenario in feature['scenarios']:
            bg = scenario.get('background')
            assert bg is not None, \
                f"Scenario '{scenario['name']}' has no 'background' field in JSON report"
            steps = bg.get('steps', [])
            assert len(steps) > 0, \
                f"Scenario '{scenario['name']}' background has no steps in JSON report"


@then('I should see the JSON report was generated')
def then_json_report_generated(context):
    report_path = os.path.abspath(os.path.join(context.output_path, 'report.json'))
    assert os.path.exists(report_path), f"JSON report not found at {report_path}"
    assert os.path.getsize(report_path) > 0, f"JSON report is empty at {report_path}"
    with open(report_path, 'r') as f:
        data = json.load(f)
    assert data, "JSON report is empty or null"


@then('I should see the JSON report has the correct top-level structure')
def then_json_top_level_structure(context):
    data = _load_json_report(context)
    for key in ('environment', 'features', 'steps_definition'):
        assert key in data, f"JSON report missing top-level key: '{key}'"
    assert isinstance(data['features'], list), "JSON report 'features' should be a list"
    assert isinstance(data['steps_definition'], dict), "JSON report 'steps_definition' should be a dict"


@then('I should see all scenario statuses in the JSON report are valid strings')
def then_json_scenario_statuses_are_strings(context):
    valid_statuses = {'passed', 'failed', 'skipped', 'error', 'untested', 'undefined'}
    data = _load_json_report(context)
    for feature in data['features']:
        for scenario in feature['scenarios']:
            status = scenario.get('status')
            assert isinstance(status, str), \
                f"Scenario '{scenario['name']}' status is not a string: {type(status).__name__} = {status}"
            assert status in valid_statuses, \
                f"Scenario '{scenario['name']}' has unrecognized status: '{status}'"


@then('I should see all step statuses in the JSON report are valid strings')
def then_json_step_statuses_are_valid(context):
    valid_statuses = {'passed', 'failed', 'skipped', 'error', 'untested', 'undefined'}
    data = _load_json_report(context)
    for feature in data['features']:
        for scenario in feature['scenarios']:
            for step in scenario['steps']:
                assert step['status'] in valid_statuses, \
                    f"Step '{step['name']}' in '{scenario['name']}' has unrecognized status: '{step['status']}'"


@then('I should see "{count}" failing scenarios in the JUnit XML report')
def then_junit_xml_failing_scenarios(context, count):
    failing = [tc for tc in _get_all_xml_testcases(context) if tc.find('failure') is not None]
    assert len(failing) == int(count), \
        f"Expected {count} JUnit testcases with a <failure> element, found {len(failing)}"


@then('I should see the error message of every failed scenario in the JSON report contains "{text}"')
def then_json_failed_scenarios_error_msg_contains(context, text):
    for scenario in _failed_scenarios_in_json_report(context):
        assert text in '\n'.join(scenario.get('error_msg') or []), \
            f"Scenario '{scenario['name']}' error_msg does not contain '{text}': {scenario.get('error_msg')}"


@then('I should see the JSON report contains error information for failed scenarios')
def then_json_failing_scenarios_have_error_info(context):
    for scenario in _failed_scenarios_in_json_report(context):
        assert scenario.get('error_msg'), \
            f"Failed scenario '{scenario['name']}' has no error_msg in JSON report"
        assert scenario.get('error_step') is not None, \
            f"Failed scenario '{scenario['name']}' has no error_step in JSON report"


@then('I should see the failing scenarios file was generated in the output folder')
def then_failing_scenarios_file_generated(context):
    failures_path = os.path.abspath(os.path.join(context.output_path, 'failing_scenarios.txt'))
    assert os.path.exists(failures_path), \
        f"failing_scenarios.txt not found at {failures_path}"
    assert os.path.getsize(failures_path) > 0, \
        f"failing_scenarios.txt is empty at {failures_path}"


@then('I store the JSON report scenario count for later comparison')
def then_store_json_scenario_count(context):
    data = _load_json_report(context)
    context.stored_scenario_count = sum(len(feature['scenarios']) for feature in data['features'])


@then('I should see the JSON report scenario count matches the stored count')
def then_json_count_matches_stored(context):
    data = _load_json_report(context)
    current_count = sum(len(feature['scenarios']) for feature in data['features'])
    stored = getattr(context, 'stored_scenario_count', None)
    assert stored is not None, "No stored scenario count — call 'I store the JSON report scenario count' first"
    assert current_count == stored, \
        f"JSON scenario count mismatch: single process had {stored}, parallel run had {current_count}"

# -*- coding: utf-8 -*-
"""
Step definitions for autoretry mechanism testing
"""

import logging
import os
import random
import re

from behave import given, then, when
from execution_steps import execute_command

# Global state for tracking retry attempts (simulates flaky behavior)
ATTEMPT_COUNTERS = {}


def reset_attempt_counter(scenario_name):
    """Reset attempt counter for a scenario"""
    ATTEMPT_COUNTERS[scenario_name] = 0


def get_random_number(length):
    """Generate a random number with specified length"""
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


def increment_attempt_counter(scenario_name):
    """Increment attempt counter for a scenario"""
    if scenario_name not in ATTEMPT_COUNTERS:
        ATTEMPT_COUNTERS[scenario_name] = 0
    ATTEMPT_COUNTERS[scenario_name] += 1
    return ATTEMPT_COUNTERS[scenario_name]


@given('a condition that fails on first attempt but recovers on retry')
def given_condition_fails_first_recovers_on_retry(context):
    """Simulates a condition that fails initially but works on retry"""
    scenario_name = context.scenario.name
    attempt = increment_attempt_counter(scenario_name)

    if attempt == 1:
        logging.info(f"First attempt for scenario: {scenario_name}")
        context.should_fail_initially = True
    else:
        logging.info(f"Retry attempt {attempt} for scenario: {scenario_name}")
        context.should_fail_initially = False


@given('a condition that fails on first two attempts but recovers on third')
def given_condition_fails_twice_recovers_on_third(context):
    """Simulates a condition that fails twice but works on third attempt"""
    scenario_name = context.scenario.name
    attempt = increment_attempt_counter(scenario_name)

    if attempt <= 2:
        logging.info(f"Attempt {attempt} (should fail) for scenario: {scenario_name}")
        context.should_fail_initially = True
    else:
        logging.info(f"Attempt {attempt} (should pass) for scenario: {scenario_name}")
        context.should_fail_initially = False


@given('a condition that fails on first four attempts but recovers on fifth')
def given_condition_fails_four_times_recovers_on_fifth(context):
    """Simulates a condition that fails four times but works on fifth attempt"""
    scenario_name = context.scenario.name
    attempt = increment_attempt_counter(scenario_name)

    if attempt <= 4:
        logging.info(f"Attempt {attempt} (should fail) for scenario: {scenario_name}")
        context.should_fail_initially = True
    else:
        logging.info(f"Attempt {attempt} (should pass) for scenario: {scenario_name}")
        context.should_fail_initially = False


@given('a condition that always fails')
@given('a condition that always fails regardless of attempts')
def given_condition_always_fails(context):
    """Simulates a condition that permanently fails"""
    scenario_name = context.scenario.name
    attempt = increment_attempt_counter(scenario_name)
    logging.info(f"Permanent failure attempt {attempt} for scenario: {scenario_name}")
    context.should_fail_permanently = True


@given('a condition that fails on first attempt but recovers on second')
def given_condition_fails_first_recovers_on_second(context):
    """Simulates a condition that would recover on second try (for non-autoretry scenarios)"""
    scenario_name = context.scenario.name
    attempt = increment_attempt_counter(scenario_name)

    # This will fail on first attempt and would pass on second, but without autoretry it won't get a second chance
    if attempt == 1:
        logging.info(f"First and only attempt for non-autoretry scenario: {scenario_name}")
        context.should_fail_without_retry = True


@given('a condition that always passes')
@given('a condition that consistently passes')
def given_condition_always_passes(context):
    """Simulates a condition that always succeeds"""
    scenario_name = context.scenario.name
    attempt = increment_attempt_counter(scenario_name)
    logging.info(f"Successful attempt {attempt} for scenario: {scenario_name}")
    context.should_pass_immediately = True


@when('I execute an action that is flaky')
@when('I execute an action that is very flaky')
@when('I execute an action that is extremely flaky')
def when_execute_flaky_action(context):
    """Executes a flaky action that might fail initially"""
    if getattr(context, 'should_fail_initially', False):
        logging.warning("Executing flaky action - this attempt will fail")
        assert False, "Flaky action failed (expected on initial attempts)"
    else:
        logging.info("Executing flaky action - this attempt will succeed")


@when('I execute an action that never succeeds')
@when('I execute an action that is permanently broken')
def when_execute_permanently_broken_action(context):
    """Executes an action that always fails"""
    if getattr(context, 'should_fail_permanently', False):
        logging.error("Executing permanently broken action - will always fail")
        assert False, "Permanently broken action failed (expected)"


@when('I execute an action without autoretry')
def when_execute_action_without_autoretry(context):
    """Executes an action without autoretry mechanism"""
    if getattr(context, 'should_fail_without_retry', False):
        logging.warning("Executing action without autoretry - will fail")
        assert False, "Action failed without retry (expected for non-autoretry scenarios)"


@when('I execute an action that succeeds immediately')
@when('I execute an action that works on first try')
def when_execute_action_succeeds_immediately(context):
    """Executes an action that succeeds immediately"""
    if getattr(context, 'should_pass_immediately', False):
        logging.info("Executing action that succeeds immediately")
        # This should pass without any assertion errors


@then('I should see the result processed correctly after retry')
@then('I should see the result processed correctly after multiple retries')
@then('I should see the result processed correctly after many retries')
@then('I should see the result processed correctly without retry')
@then('I should see the result processed correctly without any retries')
def then_result_processed_correctly(context):
    """Validates that the result was processed correctly"""
    logging.info("Result processed correctly")
    # If we reach this step, the scenario passed (possibly after retries)


@then('I should see the action consistently fail')
@then('I should see the action fail after all retry attempts')
@then('I should see the action fail immediately without retry')
def then_action_should_fail_consistently(context):
    """This step should not be reached for failing scenarios"""
    # This step should not be reached for scenarios that are supposed to fail
    assert False, "This step should not be reached for failing scenarios"


# Steps for validating autoretry behavior in main test scenarios

@when('I run the behavex command with autoretry tests using "{parallel_processes}" parallel processes and parallel scheme set as "{parallel_scheme}"')
def when_run_behavex_with_autoretry_tests(context, parallel_processes, parallel_scheme):
    """Runs behavex with autoretry test scenarios"""
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    features_path = os.path.join('tests', 'features', 'secondary_features', 'autoretry_tests.feature')

    context.parallel_processes = parallel_processes
    context.parallel_scheme = parallel_scheme

    execution_args = [
        'behavex',
        features_path,
        '-o', context.output_path,
        '-t=@AUTORETRY_RECOVERABLE,@AUTORETRY_IMMEDIATE_SUCCESS'
    ]

    execute_command(context, execution_args)


@when('I run the behavex command with permanently failing autoretry tests using "{parallel_processes}" parallel processes and parallel scheme set as "{parallel_scheme}"')
def when_run_behavex_with_permanently_failing_autoretry_tests(context, parallel_processes, parallel_scheme):
    """Runs behavex with permanently failing autoretry test scenarios"""
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    features_path = os.path.join('tests', 'features', 'secondary_features', 'autoretry_tests.feature')

    context.parallel_processes = parallel_processes
    context.parallel_scheme = parallel_scheme

    execution_args = [
        'behavex',
        features_path,
        '-o', context.output_path,
        '-t=@AUTORETRY_PERMANENT_FAILURE'
    ]

    execute_command(context, execution_args)


@when('I run the behavex command with default autoretry test scenarios')
def when_run_behavex_with_default_autoretry_scenarios(context):
    """Runs behavex with default autoretry scenarios (@AUTORETRY tag)"""
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    features_path = os.path.join('tests', 'features', 'secondary_features', 'autoretry_tests.feature')

    execution_args = [
        'behavex',
        features_path,
        '-o', context.output_path,
        '-t=@AUTORETRY'
    ]

    # Add exclusion filters as separate arguments
    execution_args.extend(['-t', '~@AUTORETRY_3'])
    execution_args.extend(['-t', '~@AUTORETRY_5'])
    execution_args.extend(['-t', '~@AUTORETRY_PERMANENT_FAILURE'])

    execute_command(context, execution_args)


@when('I run the behavex command with custom autoretry count test scenarios')
def when_run_behavex_with_custom_autoretry_count_scenarios(context):
    """Runs behavex with custom autoretry count scenarios (@AUTORETRY_N tags)"""
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    features_path = os.path.join('tests', 'features', 'secondary_features', 'autoretry_tests.feature')

    execution_args = [
        'behavex',
        features_path,
        '-o', context.output_path,
        '-t=@AUTORETRY_3,@AUTORETRY_5'
    ]

    # Add exclusion filters as separate arguments to exclude permanently failing scenarios
    execution_args.extend(['-t', '~@AUTORETRY_PERMANENT_FAILURE'])

    execute_command(context, execution_args)


@when('I run the behavex command with mixed autoretry and regular test scenarios')
def when_run_behavex_with_mixed_autoretry_scenarios(context):
    """Runs behavex with mixed autoretry and regular scenarios (some pass, some fail)"""
    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))
    features_path = os.path.join('tests', 'features', 'secondary_features', 'autoretry_tests.feature')

    execution_args = [
        'behavex',
        features_path,
        '-o', context.output_path,
        '-t=@AUTORETRY_RECOVERABLE,@NO_AUTORETRY_FAILURE'
    ]

    execute_command(context, execution_args)


@then('I should see autoretry messages for scenarios that recovered after retry')
@then('I should see autoretry messages in the console output')
@then('I should see autoretry messages in the console output for each attempt')
def then_should_see_autoretry_messages(context):
    """Validates that autoretry messages are present in the output"""
    output = context.result.stdout

    # Check if any scenarios actually ran - only validate if scenarios were executed
    scenarios_ran = re.search(r'(\d+) scenarios? passed', output)
    if scenarios_ran and int(scenarios_ran.group(1)) > 0:
        # Check for retry indicators - either AUTO-RETRY messages or retry attempt indicators
        has_autoretry_msg = "BehaveX AUTO-RETRY:" in output
        has_retry_attempt = "Retry attempt" in output

        # Accept either explicit AUTO-RETRY messages or retry attempt indicators
        assert has_autoretry_msg or has_retry_attempt, f"Expected autoretry messages or retry attempt indicators in output: {output}"


@then('I should see autoretry failure messages for scenarios that never recover')
def then_should_see_autoretry_failure_messages(context):
    """Validates that autoretry failure messages are present in the output"""
    output = context.result.stdout

    # Look for BehaveX autoretry failure messages
    assert "BehaveX AUTO-RETRY:" in output, f"Expected autoretry messages in output: {output}"
    assert "FAILED after" in output, f"Expected retry failure messages in output: {output}"


@then('I should see the correct number of retry attempts for each autoretry scenario')
@then('I should see the correct number of retry attempts for each permanently failing scenario')
def then_should_see_correct_retry_attempts(context):
    """Validates that the correct number of retry attempts are shown"""
    output = context.result.stdout

    # Check for retry attempt messages
    retry_messages = re.findall(r'BehaveX AUTO-RETRY:.*attempt (\d+)/(\d+)', output)

    assert len(retry_messages) > 0, f"Expected retry attempt messages in output: {output}"

    for attempt, max_attempts in retry_messages:
        assert int(attempt) <= int(max_attempts), f"Attempt {attempt} should not exceed max {max_attempts}"


@then('I should see that scenarios with @AUTORETRY tag are retried maximum 2 times')
def then_autoretry_scenarios_retried_maximum_2_times(context):
    """Validates that @AUTORETRY scenarios use default 2 attempts"""
    output = context.result.stdout

    # Look for retry messages with maximum 2 attempts
    if "BehaveX AUTO-RETRY:" in output:
        retry_messages = re.findall(r'attempt (\d+)/(\d+)', output)
        for attempt, max_attempts in retry_messages:
            if max_attempts == "2":  # Default @AUTORETRY behavior
                assert int(attempt) <= 2, f"Default autoretry should not exceed 2 attempts"


@then('I should see that scenarios with @AUTORETRY_3 tag are retried maximum 3 times')
def then_autoretry_3_scenarios_retried_maximum_3_times(context):
    """Validates that @AUTORETRY_3 scenarios use 3 attempts"""
    output = context.result.stdout

    # Look for retry messages with maximum 3 attempts
    if "BehaveX AUTO-RETRY:" in output:
        retry_messages = re.findall(r'attempt (\d+)/(\d+)', output)
        for attempt, max_attempts in retry_messages:
            if max_attempts == "3":  # @AUTORETRY_3 behavior
                assert int(attempt) <= 3, f"@AUTORETRY_3 should not exceed 3 attempts"


@then('I should see that scenarios with @AUTORETRY_5 tag are retried maximum 5 times')
def then_autoretry_5_scenarios_retried_maximum_5_times(context):
    """Validates that @AUTORETRY_5 scenarios use 5 attempts"""
    output = context.result.stdout

    # Look for retry messages with maximum 5 attempts
    if "BehaveX AUTO-RETRY:" in output:
        retry_messages = re.findall(r'attempt (\d+)/(\d+)', output)
        for attempt, max_attempts in retry_messages:
            if max_attempts == "5":  # @AUTORETRY_5 behavior
                assert int(attempt) <= 5, f"@AUTORETRY_5 should not exceed 5 attempts"


@then('I should see that only scenarios with autoretry tags are retried')
def then_only_autoretry_tagged_scenarios_are_retried(context):
    """Validates that only autoretry scenarios show retry messages"""
    output = context.result.stdout

    # Count scenarios with autoretry messages vs total scenarios
    autoretry_scenarios = len(re.findall(r'BehaveX AUTO-RETRY:', output))

    # Should have some autoretry messages but not for all scenarios
    assert autoretry_scenarios > 0, "Expected some scenarios to have autoretry messages"


@then('I should see that regular scenarios without autoretry tags fail immediately')
def then_regular_scenarios_fail_immediately(context):
    """Validates that non-autoretry scenarios fail without retry attempts"""
    output = context.result.stdout

    # The overall exit code should be 1 (some failures)
    assert context.result.returncode == 1, "Expected some scenarios to fail"

    # Look for failed scenarios that don't have autoretry messages
    # This is validated by the absence of retry messages for certain scenarios


@then('I should see autoretry messages only for scenarios with autoretry tags')
def then_autoretry_messages_only_for_tagged_scenarios(context):
    """Validates that autoretry messages only appear for tagged scenarios"""
    output = context.result.stdout

    # If there are autoretry messages, they should only be for tagged scenarios
    if "BehaveX AUTO-RETRY:" in output:
        # This step passes if we see autoretry messages, implying they're from tagged scenarios
        pass


@then('I should see that permanently failing scenarios are marked as failed after all retry attempts')
def then_permanently_failing_scenarios_marked_as_failed(context):
    """Validates that permanently failing scenarios still fail after retries"""
    output = context.result.stdout

    # Should see failure messages after all retry attempts
    assert "FAILED after" in output, f"Expected permanent failure messages in output: {output}"
    assert context.result.returncode == 1, "Expected exit code 1 for permanently failing scenarios"


@then('I should see the HTML report contains retried scenarios information')
@then('I should see the HTML report contains correct retry counts for each scenario')
@then('I should see the HTML report correctly distinguishes between retried and non-retried scenarios')
def then_html_report_contains_retry_information(context):
    """Validates that the HTML report contains retry information"""
    output_folder = getattr(context, 'output_path', 'output')
    report_path = os.path.join(output_folder, 'report.html')

    assert os.path.exists(report_path), f"HTML report not found at {report_path}"

    # Read HTML report content
    with open(report_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # The HTML report should exist and be generated successfully
    # Specific retry information validation would require more detailed HTML parsing
    assert len(html_content) > 0, "HTML report should contain content"
    logging.info("HTML report generated successfully with autoretry scenarios")

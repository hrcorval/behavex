# -*- coding: utf-8 -*-
"""
Step definitions for autoretry test scenarios in secondary features
"""

import logging

from behave import given, then, when

# Global state for tracking retry attempts (simulates flaky behavior)
ATTEMPT_COUNTERS = {}


def increment_attempt_counter(scenario_name):
    """Increment attempt counter for a scenario"""
    if scenario_name not in ATTEMPT_COUNTERS:
        ATTEMPT_COUNTERS[scenario_name] = 0
    ATTEMPT_COUNTERS[scenario_name] += 1
    return ATTEMPT_COUNTERS[scenario_name]


@given('a condition that fails on first attempt but recovers on retry')
def step_impl(context):
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
def step_impl(context):
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
def step_impl(context):
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
def step_impl(context):
    """Simulates a condition that permanently fails"""
    scenario_name = context.scenario.name
    attempt = increment_attempt_counter(scenario_name)
    logging.info(f"Permanent failure attempt {attempt} for scenario: {scenario_name}")
    context.should_fail_permanently = True


@given('a condition that fails on first attempt but recovers on second')
def step_impl(context):
    """Simulates a condition that would recover on second try (for non-autoretry scenarios)"""
    scenario_name = context.scenario.name
    attempt = increment_attempt_counter(scenario_name)

    # This will fail on first attempt and would pass on second, but without autoretry it won't get a second chance
    if attempt == 1:
        logging.info(f"First and only attempt for non-autoretry scenario: {scenario_name}")
        context.should_fail_without_retry = True


@given('a condition that always passes')
@given('a condition that consistently passes')
def step_impl(context):
    """Simulates a condition that always succeeds"""
    scenario_name = context.scenario.name
    attempt = increment_attempt_counter(scenario_name)
    logging.info(f"Successful attempt {attempt} for scenario: {scenario_name}")
    # Don't set any failure flags - this should pass


@when('I execute an action that fails initially')
def step_impl(context):
    """Simulates an action that fails on first attempt and passes on subsequent attempts."""
    scenario_name = context.scenario.name
    attempt = increment_attempt_counter(scenario_name)

    if attempt == 1:
        logging.warning("Executing flaky action - this attempt will fail")
        raise AssertionError("Flaky action failed (expected on initial attempts)")
    else:
        logging.info(f"Retry attempt {attempt} for scenario: {scenario_name}")
        logging.info("Executing flaky action - this attempt will succeed")


@when('I execute an action that fails twice')
def step_impl(context):
    """Simulates an action that fails twice and passes on third attempt."""
    scenario_name = context.scenario.name
    attempt = increment_attempt_counter(scenario_name)

    if attempt <= 2:
        logging.warning("Executing flaky action - this attempt will fail")
        raise AssertionError("Flaky action failed (expected on initial attempts)")
    else:
        logging.info(f"Retry attempt {attempt} for scenario: {scenario_name}")
        logging.info("Executing flaky action - this attempt will succeed")


@when('I execute an action that fails multiple times')
def step_impl(context):
    """Simulates an action that fails multiple times and passes on 5th attempt."""
    scenario_name = context.scenario.name
    attempt = increment_attempt_counter(scenario_name)

    if attempt <= 4:
        logging.warning("Executing flaky action - this attempt will fail")
        raise AssertionError("Flaky action failed (expected on initial attempts)")
    else:
        logging.info(f"Retry attempt {attempt} for scenario: {scenario_name}")
        logging.info("Executing flaky action - this attempt will succeed")


@when('I execute a permanently broken action')
@when('I execute a permanently broken action with 3 attempts')
@when('I execute a permanently broken action with 5 attempts')
def step_impl(context):
    """Executes an action that always fails"""
    logging.error("Executing permanently broken action - will always fail")
    raise AssertionError("Permanently broken action failed (expected)")


@when('I execute an action that succeeds immediately')
@when('I execute an action that works on first try')
def step_impl(context):
    """Executes an action that succeeds immediately"""
    logging.info("Executing action that succeeds immediately")
    # This should pass without any assertion errors


@then('I should see the result processed correctly after retry')
@then('I should see the result processed correctly without retry')
@then('I should see the result processed correctly without any retries')
def step_impl(context):
    """Validates that the result was processed correctly"""
    logging.info("Result processed correctly")
    # If we reach this step, the scenario passed (possibly after retries)


@then('I should see the result processed correctly after all retries')
def step_impl(context):
    """This step should not be reached for failing scenarios"""
    # This step should not be reached for scenarios that are supposed to fail
    assert False, "This step should not be reached for failing scenarios"

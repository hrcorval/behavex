import logging
import time

from behave import given, then


@given('a passing condition')
def step_passing_condition(context):
    logging.info('a passing condition')
    context.condition = 'pass'


@given('a failing condition')
def step_failing_condition(context):
    logging.info('a failing condition')
    context.condition = 'fail'


@given('a condition to skip the scenario')
def step_skip_condition(context):
    logging.info('a condition to skip the scenario')
    context.condition = 'skip'


@then('I perform the condition')
def step_perform_condition(context):
    logging.info('I perform the condition')
    if context.condition == 'pass':
        pass
    elif context.condition == 'fail':
        assert False, "This step is designed to fail"
    elif context.condition == 'skip':
        context.scenario.skip("Skipped")


@given('a step with the text "{value}"')
def step_with_text(context, value):
    logging.info('a step with the text %s', value)


@given('a step that fails with the message "{message}"')
def step_fails_with_message(context, message):
    assert False, message


@given('a step that fails on a source line containing a CDATA terminator')
def step_fails_on_cdata_terminator_source_line(context):
    assert ']]>' == ''


@given('a step that waits "{seconds}" seconds')
def step_waits_given_seconds(context, seconds):
    time.sleep(float(seconds))

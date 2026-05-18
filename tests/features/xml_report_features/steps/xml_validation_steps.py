import logging

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

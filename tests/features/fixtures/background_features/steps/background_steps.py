import logging

from behave import given, then


@given('a passing condition')
def step_passing_condition(context):
    logging.info('a passing condition')
    context.condition = 'pass'


@then('I perform the condition')
def step_perform_condition(context):
    logging.info('I perform the condition')

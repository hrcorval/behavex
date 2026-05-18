import logging

from behave import given


@given('a passing condition')
def step_passing_condition(context):
    # Local copy needed: fixture features run in isolated subprocesses that only
    # load steps from their own steps/ directory.
    logging.info('a passing condition')


@given('a step that raises a simple exception')
def step_raises_simple_exception(context):
    raise ValueError("Something went wrong: invalid input value")


@given('a step that raises a chained exception with two levels')
def step_raises_chained_exception_two_levels(context):
    try:
        raise ValueError("Root cause: database connection failed")
    except ValueError as e:
        raise RuntimeError("Service layer error: could not process request") from e


@given('a step that raises a chained exception with three levels')
def step_raises_chained_exception_three_levels(context):
    try:
        try:
            raise IOError("Level 1: file not found at /data/config.json")
        except IOError as e:
            raise ValueError("Level 2: configuration could not be loaded") from e
    except ValueError as e:
        raise RuntimeError("Level 3: application failed to initialize") from e

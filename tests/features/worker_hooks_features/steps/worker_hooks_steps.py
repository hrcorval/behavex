import logging

from behave import given, then


@given('the shared context values are available')
def step_shared_context_available(context):
    assert hasattr(context, 'shared_url'), \
        "shared_url was not injected from before_all_workers into the worker context"
    logging.info(f"Shared context available: shared_url={context.shared_url}")


@then('the string value "{attr}" should equal "{expected}"')
def step_string_value_equals(context, attr, expected):
    actual = getattr(context, attr, None)
    assert actual == expected, \
        f"Expected context.{attr} == '{expected}' but got '{actual}'"
    logging.info(f"context.{attr} = '{actual}' ✓")


@then('the integer value "{attr}" should equal "{expected}"')
def step_integer_value_equals(context, attr, expected):
    actual = getattr(context, attr, None)
    assert actual == int(expected), \
        f"Expected context.{attr} == {expected} but got {actual!r}"
    logging.info(f"context.{attr} = {actual} ✓")


@then('the boolean value "{attr}" should be true')
def step_boolean_value_true(context, attr):
    actual = getattr(context, attr, None)
    assert actual is True, \
        f"Expected context.{attr} to be True but got {actual!r}"
    logging.info(f"context.{attr} = {actual} ✓")


@then('the list value "{attr}" should contain "{item}"')
def step_list_value_contains(context, attr, item):
    actual = getattr(context, attr, None)
    assert isinstance(actual, list) and item in actual, \
        f"Expected context.{attr} to contain '{item}' but got {actual!r}"
    logging.info(f"context.{attr} contains '{item}' ✓")

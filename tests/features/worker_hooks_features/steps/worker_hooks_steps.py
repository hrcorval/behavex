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


@then('context.behavex.parallel_scheme should be a valid scheme')
def step_behavex_parallel_scheme(context):
    bx = context.behavex
    assert bx.parallel_scheme in ('scenario', 'feature'), \
        f"Expected parallel_scheme in ('scenario', 'feature') but got {bx.parallel_scheme!r}"
    logging.info(f"context.behavex.parallel_scheme = '{bx.parallel_scheme}' ✓")


@then('context.behavex.parallel_processes should be a positive integer')
def step_behavex_parallel_processes(context):
    bx = context.behavex
    assert isinstance(bx.parallel_processes, int) and bx.parallel_processes >= 1, \
        f"Expected parallel_processes >= 1 but got {bx.parallel_processes!r}"
    logging.info(f"context.behavex.parallel_processes = {bx.parallel_processes} ✓")


@then('context.behavex.is_worker should be a boolean')
def step_behavex_is_worker(context):
    bx = context.behavex
    assert isinstance(bx.is_worker, bool), \
        f"Expected is_worker to be bool but got {type(bx.is_worker).__name__}"
    logging.info(f"context.behavex.is_worker = {bx.is_worker} ✓")


@then('context.behavex.worker_id should be a non-negative integer')
def step_behavex_worker_id(context):
    bx = context.behavex
    assert isinstance(bx.worker_id, int) and bx.worker_id >= 0, \
        f"Expected worker_id >= 0 but got {bx.worker_id!r}"
    logging.info(f"context.behavex.worker_id = {bx.worker_id} ✓")

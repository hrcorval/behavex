from behave import then


@then('the shared stage name should be "{expected}"')
def step_shared_stage_name(context, expected):
    actual = getattr(context, 'stage_name', None)
    assert actual == expected, f"Expected context.stage_name == '{expected}' but got {actual!r}"

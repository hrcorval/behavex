from behave import given


@given('a passing step')
def step_passing(context):
    pass


@given('a step that raises a non-assertion exception')
def step_raises_error(context):
    raise RuntimeError('every attempt errors')

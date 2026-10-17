from behave import given

_attempts = {}


@given('a step that raises on its first attempt')
def step_raises_on_first_attempt(context):
    _attempts[context.scenario.name] = _attempts.get(context.scenario.name, 0) + 1
    if _attempts[context.scenario.name] == 1:
        raise RuntimeError('first attempt raises')


@given('a passing step')
def step_passing(context):
    pass

from behave import given


@given('a passing step')
def step_passing(context):
    pass


_attempts = {}


@given('a step that fails on its first attempt')
def step_fails_on_first_attempt(context):
    _attempts[context.scenario.name] = _attempts.get(context.scenario.name, 0) + 1
    assert _attempts[context.scenario.name] > 1, 'first attempt fails'


@given('a step that always fails')
def step_always_fails(context):
    assert False, 'every attempt fails'

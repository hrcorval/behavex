from behave import given


@given('a passing step')
def given_passing_step(context):
    pass


@given('a step that interrupts the run')
def given_interrupting_step(context):
    raise KeyboardInterrupt()

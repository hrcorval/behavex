import step_library.library_steps  # noqa: F401
from behave import given, step


@step('a passing step')
def step_passing(context):
    pass


@given(r'a step defined with the regex matcher of environment\.py')
def step_with_regex_matcher(context):
    pass

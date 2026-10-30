from behave import step


@step('a step only the first serial suite defines')
def step_only_in_first_suite(context):
    pass

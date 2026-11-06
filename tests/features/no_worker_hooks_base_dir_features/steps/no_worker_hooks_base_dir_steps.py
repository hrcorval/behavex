from behave import step


@step('the environment set the value from its sibling package')
def step_environment_set_value_from_sibling_package(context):
    assert context.value == 'ok', context.value

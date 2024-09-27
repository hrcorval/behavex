from behave import given, then, when


@given('a failing condition')
def step_impl(context):
    context.condition = 'fail'

@given('a passing condition')
def step_impl(context):
    context.condition = 'pass'

@given('a condition to skip the scenario')
def step_impl(context):
    context.condition = 'skip'

@given('a condition to exit the scenario')
def step_impl(context):
    context.condition = 'exit'

@given('a condition to leave the scenario untested')
def step_impl(context):
    context.condition = 'untested'

@then('I perform the condition')
def step_impl(context):
    if context.condition == 'fail':
        # This step will cause the test to fail
        assert False, "This step is designed to fail"
    elif context.condition == 'pass':
        # This step will pass
        assert True
    elif context.condition == 'skip':
        # This step will be skipped
        context.scenario.skip("This scenario is skipped")
    elif context.condition == 'exit':
        # This step will be skipped
        print("Exiting the scenario")
        exit(1)
    elif context.condition == 'untested':
        # This step will be skipped
        pass

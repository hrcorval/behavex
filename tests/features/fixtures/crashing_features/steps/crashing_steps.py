from behave import given, then, when


@given('a failing condition')
def given_failing_condition(context):
    context.condition = 'fail'

@given('a passing condition')
def given_passing_condition(context):
    context.condition = 'pass'

@given('a condition to skip the scenario')
def given_skip_condition(context):
    context.condition = 'skip'

@given('a condition to exit the scenario')
def given_exit_condition(context):
    context.condition = 'exit'

@given('a condition to leave the scenario untested')
def given_untested_condition(context):
    context.condition = 'untested'

@then('I perform the condition')
def then_perform_condition(context):
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

import logging

from behave import given, then, when


@given('a failing condition')
def step_impl(context):
    context.condition = 'fail'
    logging.info('a failing condition')

@given('a passing condition')
def step_impl(context):
    context.condition = 'pass'
    logging.info('a passing condition')

@given('a condition to skip the scenario')
def step_impl(context):
    context.condition = 'skip'
    logging.info('a condition to skip the scenario')

@given('a condition to exit the scenario')
def step_impl(context):
    context.condition = 'exit'
    logging.info('a condition to exit the scenario')

@given('a condition to leave the scenario untested')
def step_impl(context):
    context.condition = 'untested'
    logging.info('a condition to leave the scenario untested')

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
        exit(1)
    elif context.condition == 'untested':
        # This step will be skipped
        pass

@given('I rename the {feature_or_scenario} from context to have the suffix "{suffix}"')
def step_impl(context, feature_or_scenario, suffix):
    if feature_or_scenario == 'feature':
        context.new_feature_name = context.feature.name + suffix
        logging.info('I rename the feature from \n"{}" \nto \n"{}"'.format(context.feature.name, context.new_feature_name))
    elif feature_or_scenario == 'scenario':
        context.new_scenario_name = context.scenario.name + suffix
        logging.info('I rename the scenario from \n"{}" \nto \n"{}"'.format(context.scenario.name, context.new_scenario_name))
    else:
        raise ValueError('Invalid element, it should be "feature" or "scenario"')

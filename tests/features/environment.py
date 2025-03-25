
def before_scenario(context, scenario):
    context.progress_bar = False


def after_scenario(context, scenario):
    # print the scenario name and the execution status
    print(f"Scenario: {scenario.name} - Execution Status: {context.scenario_status}")

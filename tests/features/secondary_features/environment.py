
def after_scenario(context, scenario):
    if hasattr(context, 'new_scenario_name'):
        scenario.name = context.new_scenario_name
    if hasattr(context, 'new_feature_name'):
        scenario.feature.name = context.new_feature_name

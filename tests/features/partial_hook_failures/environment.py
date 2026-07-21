def before_scenario(context, scenario):
    if scenario.name == "Second scenario fails its before_scenario hook":
        raise AssertionError("Intentional before_scenario failure for regression test")

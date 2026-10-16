def after_scenario(context, scenario):
    if 'FAILING_TEARDOWN' in scenario.tags:
        raise RuntimeError('teardown failed')

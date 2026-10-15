def before_scenario(context, scenario):
    if 'FAILING_HOOK' in scenario.effective_tags:
        raise RuntimeError('before_scenario fails on purpose')

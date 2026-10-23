def before_scenario(context, scenario):
    if 'FAILING_CLEANUP' in scenario.tags:
        context.add_cleanup(_fail_cleanup)


def after_scenario(context, scenario):
    if 'FAILING_TEARDOWN' in scenario.tags:
        raise RuntimeError('teardown failed')


def after_tag(context, tag):
    if tag == 'FAILING_AFTER_TAG':
        raise RuntimeError('after_tag failed')


def _fail_cleanup():
    raise RuntimeError('cleanup failed')

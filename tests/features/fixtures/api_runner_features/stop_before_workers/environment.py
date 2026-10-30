import __main__


def before_all_workers(context):
    # the driving script calls stop() between these two events
    hook_entered = getattr(__main__, 'hook_entered', None)
    if hook_entered is not None:
        hook_entered.set()
        __main__.stop_called.wait(timeout=60)

"""
Secondary environment used to validate before_all_workers / after_all_workers hooks.

Shared values set here must be accessible in before_all and all step definitions
without any extra wiring.
"""
import os


def _record_call_and_fail_if_requested(hook_name):
    with open(os.path.join(os.environ['OUTPUT'], 'worker_hook_calls.log'), 'a') as calls_file:
        calls_file.write(hook_name + '\n')
    if os.environ.get('FAILING_WORKER_HOOK') == hook_name:
        raise RuntimeError(f'{hook_name} failed on purpose')


def before_all_workers(context):
    _record_call_and_fail_if_requested('before_all_workers')
    context.shared_url = "https://staging.behavex.io"
    context.shared_retries = 3
    context.shared_enabled = True
    context.shared_tags = ["smoke", "regression"]


def after_all_workers(context):
    _record_call_and_fail_if_requested('after_all_workers')
    # Verify shared values are still readable in after_all_workers
    assert context.shared_url == "https://staging.behavex.io", \
        "after_all_workers: shared_url not accessible"


def before_all(context):
    # Shared values must be injected before before_all runs
    assert hasattr(context, 'shared_url'), \
        "before_all: shared_url was not injected from before_all_workers"

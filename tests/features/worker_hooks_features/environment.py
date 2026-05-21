"""
Secondary environment used to validate before_all_workers / after_all_workers hooks.

Shared values set here must be accessible in before_all and all step definitions
without any extra wiring.
"""


def before_all_workers(context):
    context.shared_url = "https://staging.behavex.io"
    context.shared_retries = 3
    context.shared_enabled = True
    context.shared_tags = ["smoke", "regression"]


def after_all_workers(context):
    # Verify shared values are still readable in after_all_workers
    assert context.shared_url == "https://staging.behavex.io", \
        "after_all_workers: shared_url not accessible"


def before_all(context):
    # Shared values must be injected before before_all runs
    assert hasattr(context, 'shared_url'), \
        "before_all: shared_url was not injected from before_all_workers"

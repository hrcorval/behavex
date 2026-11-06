import os

from worker_hooks_base_dir_helpers import EXPECTED_VALUE

if os.environ.get('FAILING_ENVIRONMENT_IMPORT'):
    raise RuntimeError('environment.py failed on purpose')


def _record_call(hook_name):
    with open(os.path.join(os.environ['OUTPUT'], 'worker_hook_calls.log'), 'a') as calls_file:
        calls_file.write(hook_name + '\n')


def before_all_workers(context):
    _record_call('before_all_workers')


def after_all_workers(context):
    _record_call('after_all_workers')


def before_all(context):
    context.value = EXPECTED_VALUE

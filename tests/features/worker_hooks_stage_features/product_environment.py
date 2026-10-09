import os


def before_all_workers(context):
    with open(os.path.join(os.environ['OUTPUT'], 'worker_hook_calls.log'), 'a') as calls_file:
        calls_file.write('before_all_workers\n')
    context.stage_name = 'product'


def after_all_workers(context):
    with open(os.path.join(os.environ['OUTPUT'], 'worker_hook_calls.log'), 'a') as calls_file:
        calls_file.write('after_all_workers\n')

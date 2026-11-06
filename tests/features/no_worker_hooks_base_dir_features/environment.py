import multiprocessing
import os

from no_worker_hooks_base_dir_helpers import EXPECTED_VALUE

with open(os.path.join(os.environ['OUTPUT'], 'environment_imports.log'), 'a') as imports_file:
    imports_file.write(multiprocessing.current_process().name + '\n')


def before_all(context):
    context.value = EXPECTED_VALUE

import subprocess
import sys

from behave import given


@given('a step that runs a subprocess writing to sys.stdout')
def step_subprocess_to_stdout(context):
    subprocess.run([sys.executable, '-c', 'print("subprocess output")'], stdout=sys.stdout, check=True)

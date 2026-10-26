import os

from behave import given


@given('a step that kills the process running it')
def step_kills_its_process(context):
    os._exit(3)


@given('a passing step')
def step_passing(context):
    pass

import time

from behave import given


@given('a step that takes half a second')
def step_takes_half_a_second(context):
    time.sleep(0.5)

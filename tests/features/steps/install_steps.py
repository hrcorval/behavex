from behave import given, when, then
import subprocess


@given('I have installed behavex')
def step_impl(context):
    pass  # Assuming behavex is already installed


@when('I run the behavex command')
def step_impl(context):
    context.result = subprocess.run(['behavex', '--help'], capture_output=True, text=True)


@then('I should see the behavex output')
def step_impl(context):
    assert context.result.returncode == 0, "behavex command failed"
    assert "BehaveX - test automation wrapper on top of Behave" in context.result.stdout, "Unexpected output from behavex command"

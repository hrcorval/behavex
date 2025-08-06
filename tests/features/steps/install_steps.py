# nosec B404
import logging
import subprocess

from behave import given, then, when


@given('I have installed behavex')
def given_behavex_installed(context):
    pass  # Assuming behavex is already installed


@when('I run the behavex command')
def when_run_behavex_command(context):
    context.result = subprocess.run(['behavex', '--help'], capture_output=True, text=True)
    logging.info(context.result.stdout)


@then('I should see the behavex output')
def then_see_behavex_output(context):
    assert context.result.returncode == 0, "behavex command failed"
    assert "BehaveX - test automation wrapper on top of Behave" in context.result.stdout, "Unexpected output from behavex command"

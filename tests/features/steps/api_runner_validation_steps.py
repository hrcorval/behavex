import os
import shutil
import tempfile

from api_runner_support import (
    _CAPTURE_RAISED,
    _SERIALIZE_RESULT,
    _refused_input_kwargs,
    _run_script,
    _store_result,
)
from behave import then, when
from execution_steps import secondary_features_path


@when('I run BehaveXRunner on passing tests with {argument} set to "{value}"')
def when_api_run_with_argument_value(context, argument, value):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    script = f"""
import json, sys
{_CAPTURE_RAISED}
raised = _capture_raised(lambda: BehaveXRunner(paths=[{repr(feature_path)}], no_report=True, {argument}={repr(value)}).run())
print("__RESULT__:" + json.dumps({{"raised": raised}}))
"""
    _store_result(context, _run_script(script))


@when('I call run() with {input_name}')
def when_api_run_refused_input(context, input_name):
    kwargs = _refused_input_kwargs(input_name)
    script = f"""
import json, sys
{_CAPTURE_RAISED}
raised = _capture_raised(lambda: BehaveXRunner(no_report=True, **{kwargs!r}).run())
print("__RESULT__:" + json.dumps({{"raised": raised}}))
"""
    _store_result(context, _run_script(script))


@when('I run BehaveXRunner on passing tests through a relative {argument} entry starting with "-" using "{parallel_processes}" parallel processes')
def when_api_run_dash_prefixed_path(context, argument, parallel_processes):
    work_dir = tempfile.mkdtemp()
    context.add_cleanup(shutil.rmtree, work_dir, ignore_errors=True)
    shutil.copytree(secondary_features_path, os.path.join(work_dir, '-suite'),
                    ignore=shutil.ignore_patterns('__pycache__'))
    script = f"""
import json, os, sys
os.chdir({repr(work_dir)})
from behavex import BehaveXRunner
result = BehaveXRunner({argument}=['-suite/passing_tests.feature'], parallel_processes={int(parallel_processes)}).run()
""" + _SERIALIZE_RESULT
    _store_result(context, _run_script(script, import_runner=False))


@when('two threads call run() on passing tests at once, the second while the first validates its arguments')
def when_two_threads_run_at_once(context):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    script = f"""
import json, sys, threading
from behavex import api
{_CAPTURE_RAISED}
_outcomes = {{}}
_first_validating = threading.Event()
_release_first = threading.Event()
_validate_args = api._validate_args

def _validate_args_holding_the_first(args):
    if not _first_validating.is_set():
        _first_validating.set()
        _release_first.wait(60)
    _validate_args(args)

def _run(name):
    _outcomes[name] = _capture_raised(lambda: BehaveXRunner(paths=[{repr(feature_path)}], no_report=True).run())

api._validate_args = _validate_args_holding_the_first
first = threading.Thread(target=_run, args=('first',))
first.start()
_first_validating.wait(60)
second = threading.Thread(target=_run, args=('second',))
second.start()
second.join(120)
_release_first.set()
first.join(120)
print("__RESULT__:" + json.dumps({{"raised": [r for r in _outcomes.values() if r], "outcome_count": len(_outcomes)}}))
"""
    _store_result(context, _run_script(script))


@then('exactly one of the two runs raised a RuntimeError mentioning "{text}"')
def then_exactly_one_run_raised_runtime_error(context, text):
    result = context.api_run_result
    raised = result['raised']
    assert (result['outcome_count'] == 2 and len(raised) == 1 and raised[0]['type'] == 'RuntimeError'
            and text in raised[0]['message']), (
        f'Expected exactly one RuntimeError mentioning {text!r}, got {result}.\nOutput:\n{context.api_run_output}'
    )


@when('I run the behavex CLI with {input_name}')
def when_cli_run_refused_input(context, input_name):
    paths = _refused_input_kwargs(input_name).get('paths', [])
    script = f"""
import sys
from behavex.runner import main
sys.argv = ['behavex', *{paths!r}, '--no-report']
main()
"""
    context.cli_proc = _run_script(script, import_runner=False)


@then('the CLI printed "{text}", then "Exit code: 1", and exited with code 1')
def then_cli_printed_reason_and_exit_code(context, text):
    proc = context.cli_proc
    lines = proc.stdout.splitlines()
    assert proc.returncode == 1 and lines[-2:-1] and lines[-2].startswith(text) and lines[-1] == 'Exit code: 1', (
        f'Exit code {proc.returncode}.\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}'
    )

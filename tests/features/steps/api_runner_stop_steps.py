import json
import os
import sys
import textwrap

from api_runner_support import (
    _CAPTURE_RAISED,
    _PROGRESS_CALLBACK,
    _RUN_MODES,
    _SERIALIZE_PROGRESS,
    _STOP_WHILE_BEFORE_ALL_WORKERS_RUNS,
    _run_script,
    _store_result,
    api_runner_features_path,
    serial_suites_path,
)
from behave import given, then, when
from execution_steps import secondary_features_path

_SERIAL_STOP_RACES = {
    # stop() lands between the serial loop's stop check and its submission
    'stop() comes right after the stop check': """
_check_stop_requested = dispatch._mark_run_stopped_if_requested

def _check_then_stop():
    stop_was_requested = _check_stop_requested()
    if not stop_was_requested:
        behavex_runner.stop()
    return stop_was_requested

mock.patch.object(dispatch, '_mark_run_stopped_if_requested', _check_then_stop).start()
""",
    # stop()'s cancel_futures cancels the queued work before a worker picks it up
    'the submitted @SERIAL work is cancelled before it starts': """
from concurrent.futures import Future

def _submit_cancelled(*args, **kwargs):
    cancelled_future = Future()
    cancelled_future.cancel()
    return cancelled_future

mock.patch.object(dispatch, '_submit_unless_stopped', _submit_cancelled).start()
""",
}


@when('I call stop() on a BehaveXRunner that is not running')
def when_stop_outside_run(context):
    script = """
import json, sys
runner = BehaveXRunner(paths=["tests/features"])
try:
    runner.stop()
    exception = None
except Exception as e:
    exception = str(e)
_data = {"exit_code": 0, "exception": exception}
print("__RESULT__:" + json.dumps(_data))
"""
    proc = _run_script(script)
    _store_result(context, proc)


@when('I run BehaveXRunner with passing tests and call stop() from a background thread')
def when_run_with_stop_non_parallel(context):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    script = f"""
import json, sys, threading

runner = BehaveXRunner(paths=[{repr(feature_path)}], no_report=True)
exception = None

# stop() has no effect on a single-process run
timer = threading.Timer(0.5, runner.stop)
timer.start()
try:
    result = runner.run()
    exit_code = result.exit_code
except Exception as e:
    exit_code = 2
    exception = str(e)
finally:
    timer.cancel()

_data = {{"exit_code": exit_code, "exception": exception}}
print("__RESULT__:" + json.dumps(_data))
"""
    proc = _run_script(script)
    _store_result(context, proc)


@when('I run BehaveXRunner with passing tests in parallel and call stop() from a background thread')
def when_run_parallel_with_stop(context):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    script = f"""
import json, sys, threading

runner = BehaveXRunner(
    paths=[{repr(feature_path)}],
    no_report=True,
    parallel_processes=2,
    parallel_scheme='scenario',
)
exception = None

timer = threading.Timer(0.5, runner.stop)
timer.start()
try:
    result = runner.run()
    exit_code = result.exit_code
except Exception as e:
    exit_code = 2
    exception = str(e)
finally:
    timer.cancel()

_data = {{"exit_code": exit_code, "exception": exception}}
print("__RESULT__:" + json.dumps(_data))
"""
    proc = _run_script(script)
    _store_result(context, proc)


@then('no exception was raised')
def then_no_exception(context):
    exception = context.api_run_result.get('exception')
    assert exception is None, (
        f'Expected no exception but got: {exception}\n'
        f'BehaveXRunner output:\n{context.api_run_output}'
    )


@when('I run BehaveXRunner on "{fixture}" with "{parallel_processes}" parallel processes, "{parallel_scheme}" scheme, and call stop() on progress event "{event_number}"')
def when_run_parallel_stopping_on_event(context, fixture, parallel_processes, parallel_scheme, event_number):
    _run_parallel_stopping_on_event(context, fixture, parallel_processes, parallel_scheme, event_number, 'runner')


@when('I run BehaveXRunner on "{fixture}" with "{parallel_processes}" parallel processes, "{parallel_scheme}" scheme, and call stop() on another, idle BehaveXRunner on progress event "{event_number}"')
def when_run_parallel_stopping_idle_runner_on_event(context, fixture, parallel_processes, parallel_scheme, event_number):
    _run_parallel_stopping_on_event(context, fixture, parallel_processes, parallel_scheme, event_number, 'idle_runner')


def _run_parallel_stopping_on_event(context, fixture, parallel_processes, parallel_scheme, event_number,
                                    stopped_runner_name):
    feature_path = os.path.join(api_runner_features_path, fixture)
    script = f"""
import json, sys
{_PROGRESS_CALLBACK}
_record = _on_progress

def _on_progress(event):
    _record(event)
    if len(_events) == {int(event_number)}:
        {stopped_runner_name}.stop()

idle_runner = BehaveXRunner(paths=[{repr(feature_path)}])
runner = BehaveXRunner(
    paths=[{repr(feature_path)}],
    no_report=True,
    parallel_processes={int(parallel_processes)},
    parallel_scheme={repr(parallel_scheme)},
    on_progress=_on_progress,
)
result = runner.run()
""" + _SERIALIZE_PROGRESS
    _store_result(context, _run_script(script))


@when('I run BehaveXRunner on "{fixture}" with "{parallel_processes}" parallel processes, "{parallel_scheme}" scheme, and call stop() while before_all_workers runs')
def when_run_parallel_stopping_in_before_all_workers(context, fixture, parallel_processes, parallel_scheme):
    feature_path = os.path.join(api_runner_features_path, fixture)
    script = f"""
import json, sys, threading

{_STOP_WHILE_BEFORE_ALL_WORKERS_RUNS}
runner = BehaveXRunner(
    paths=[{repr(feature_path)}],
    no_report=True,
    parallel_processes={int(parallel_processes)},
    parallel_scheme={repr(parallel_scheme)},
)
threading.Thread(target=_stop_once_hook_entered, args=(runner,), daemon=True).start()
result = runner.run()
_events = []
""" + _SERIALIZE_PROGRESS
    _store_result(context, _run_script(script))


@then('the RunResult summary total is less than "{expected}"')
def then_summary_total_lt(context, expected):
    actual = context.api_run_result['summary_total']
    assert actual < int(expected), (
        f'Expected summary.total < {expected}, got {actual}.\n'
        f'BehaveXRunner output:\n{context.api_run_output}'
    )


@when('the runner waits on a queued future that stop() cancels meanwhile')
def when_waiting_on_future_cancelled_meanwhile(context):
    script = """
import json, sys, threading
from concurrent.futures import Future
from behavex import dispatch

future = Future()
threading.Timer(0.3, future.cancel).start()
execution_codes = []
dispatch._wait_for_futures([future], execution_codes)
print("__RESULT__:" + json.dumps({"execution_codes": execution_codes}))
"""
    _store_result(context, _run_script(script, import_runner=False))


@then('no execution code was recorded for the cancelled future')
def then_no_execution_code_recorded(context):
    assert context.api_run_result['execution_codes'] == [], context.api_run_result


@when('I run BehaveXRunner on "twelve_scenarios.feature" with "2" parallel processes, slow result callbacks, and call stop() on progress event "1"')
def when_run_parallel_slow_callbacks_stopping_on_first_event(context):
    feature_path = os.path.join(api_runner_features_path, 'twelve_scenarios.feature')
    script = f"""
import json, sys, time
from unittest import mock
from behavex import dispatch
{_PROGRESS_CALLBACK}
_record = _on_progress
_handle_result = dispatch.handle_execution_complete_callback
_results_handled = []

def _slow_handle_result(codes, json_reports, progress_bar, future):
    if future.cancelled():
        return
    time.sleep(0.5)
    _handle_result(codes, json_reports, progress_bar, future)
    _results_handled.append(future)

mock.patch.object(dispatch, 'handle_execution_complete_callback', _slow_handle_result).start()

def _on_progress(event):
    _record(event)
    if len(_events) == 1:
        runner.stop()

runner = BehaveXRunner(paths=[{repr(feature_path)}], no_report=True, parallel_processes=2,
                       parallel_scheme='scenario', on_progress=_on_progress)
result = runner.run()
_events_at_return = len(_events)
time.sleep(2)
print("__HANDLED__:" + json.dumps({{"results_handled": len(_results_handled), "events_at_return": _events_at_return}}))
""" + _SERIALIZE_PROGRESS
    _store_result(context, _run_script(script))
    for line in context.api_run_output.splitlines():
        if line.startswith('__HANDLED__:'):
            context.api_run_result.update(json.loads(line[len('__HANDLED__:'):]))


@then('every scenario whose result was handled is in the RunResult and fired its event before run() returned')
def then_every_handled_result_reported(context):
    result = context.api_run_result
    assert result['stopped'], result
    assert result['summary_total'] == result['results_handled'] == result['events_at_return'], (
        f'{result["results_handled"]} results handled, {result["summary_total"]} in the RunResult, '
        f'{result["events_at_return"]} events before run() returned.\nOutput:\n{context.api_run_output}'
    )


@given('Python can cancel queued futures')
def given_python_can_cancel_queued_futures(context):
    if sys.version_info < (3, 9):
        context.scenario.skip(reason='Executor.shutdown(cancel_futures=True) requires Python 3.9')


@when('I run BehaveXRunner in parallel by {scheme} on the second @SERIAL suite, and {race}')
def when_stop_races_serial_work(context, scheme, race):
    run_mode = _RUN_MODES[f'in parallel by {scheme}']
    script = f"""
import json, sys
from unittest import mock
from behavex import dispatch
{_CAPTURE_RAISED}
if __name__ == '__main__':
    behavex_runner = BehaveXRunner(paths=[{os.path.join(serial_suites_path, 'second')!r}], no_report=True, **{run_mode!r})
{textwrap.indent(_SERIAL_STOP_RACES[race], '    ')}
    results = []
    raised = _capture_raised(lambda: results.append(behavex_runner.run()))
    print("__RESULT__:" + json.dumps({{"raised": raised, "stopped": results[0].stopped if results else None}}))
"""
    _store_result(context, _run_script(script))


@then('the run raised no exception and the RunResult stopped is "{stopped}"')
def then_no_exception_and_stopped(context, stopped):
    result = context.api_run_result
    assert result['raised'] is None and result['stopped'] == (stopped == 'True'), (
        f'Expected no exception and stopped={stopped}, got {result}.\nOutput:\n{context.api_run_output}'
    )

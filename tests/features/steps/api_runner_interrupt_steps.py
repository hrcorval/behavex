import os

from api_runner_support import (
    _CAPTURE_RAISED,
    _RUN_MODES,
    _SERIALIZE_RESULT,
    _run_script,
    _store_result,
    api_runner_features_path,
)
from behave import then, when
from execution_steps import secondary_features_path

_CTRL_C_TARGETS = {
    'the whole process group, as a terminal does': 'os.killpg(os.getpgid(0), signal.SIGINT)',
    'the host process alone, as Jupyter does': 'os.kill(os.getpid(), signal.SIGINT)',
}


_CTRL_C_PRESS_GAPS = {'once': [], 'twice': ['time.sleep(0.1)']}


@when('I run BehaveXRunner with passing tests while merging the results raises KeyboardInterrupt')
def when_api_run_interrupted_before_merge(context):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    script = f"""
import json, sys
from behavex import runner

def _interrupt(*args, **kwargs):
    raise KeyboardInterrupt

runner.shut_down_worker_pool_and_write_merged_report = _interrupt
result = BehaveXRunner(paths=[{repr(feature_path)}], no_report=True).run()
""" + _SERIALIZE_RESULT
    _store_result(context, _run_script(script))


@when('a worker gets a Ctrl+C while it puts a message on the host queue')
def when_worker_ctrl_c_during_host_queue_put(context):
    script = """
import json, os, signal, sys
from behavex import host_messages

class HostQueueInterruptedMidPut:
    put_completed = False
    def put(self, message):
        os.kill(os.getpid(), signal.SIGINT)
        self.put_completed = True

host_queue = HostQueueInterruptedMidPut()
signal.signal(signal.SIGINT, host_messages.stop_behave_on_first_ctrl_c)
interrupt_raised_after_put = None
try:
    host_messages.HostQueueDeferringCtrlC(host_queue).put(('output', 'line'))
except KeyboardInterrupt:
    interrupt_raised_after_put = host_queue.put_completed
print("__RESULT__:" + json.dumps({"interrupt_raised_after_put": interrupt_raised_after_put}))
"""
    _store_result(context, _run_script(script, import_runner=False))


@then('the put completed before the KeyboardInterrupt was raised')
def then_put_completed_before_keyboard_interrupt(context):
    assert context.api_run_result['interrupt_raised_after_put'] is True, context.api_run_result


@when('I run BehaveXRunner in a single process on slow scenarios and send Ctrl+C {presses} to {target} once the first one finishes')
def when_run_and_send_ctrl_c(context, presses, target):
    ctrl_c_presses_code = '; '.join([_CTRL_C_TARGETS[target]] + [
        f'{gap}; {_CTRL_C_TARGETS[target]}' for gap in _CTRL_C_PRESS_GAPS[presses]])
    script = f"""
import json, multiprocessing, os, signal, sys, time
{_CAPTURE_RAISED}
pressed = []

def _press_ctrl_c_on_first_event(event):
    if not pressed:
        pressed.append(True)
        {ctrl_c_presses_code}

if __name__ == '__main__':
    # Python leaves Ctrl+C ignored when its parent ignored it, as the suite's runner may
    signal.signal(signal.SIGINT, signal.default_int_handler)
    host_child = multiprocessing.Process(target=time.sleep, args=(120,))
    host_child.start()
    results = []
    raised = _capture_raised(lambda: results.append(BehaveXRunner(
        paths=[{os.path.join(api_runner_features_path, 'slow_scenarios')!r}], no_report=True,
        on_progress=_press_ctrl_c_on_first_event).run()))
    host_child_alive = host_child.is_alive()
    host_child.terminate()
    statuses = {{s.name: s.status for f in results[0].features for s in f.scenarios}} if results else {{}}
    print("__RESULT__:" + json.dumps({{"raised": raised, "statuses": statuses, "host_child_alive": host_child_alive}}))
"""
    # A process group of its own, so the Ctrl+C reaches only this run
    _store_result(context, _run_script(script, start_new_session=True))


@when('I run BehaveXRunner in parallel on slow scenarios, call stop() and send Ctrl+C to the host process once the first one finishes')
def when_run_in_parallel_stop_and_send_ctrl_c(context):
    script = f"""
import json, multiprocessing, os, signal, sys
{_CAPTURE_RAISED}
pressed = []

def _stop_and_press_ctrl_c_on_first_event(event):
    if not pressed:
        pressed.append(True)
        runner.stop()
        os.kill(os.getpid(), signal.SIGINT)

if __name__ == '__main__':
    # Python leaves Ctrl+C ignored when its parent ignored it, as the suite's runner may
    signal.signal(signal.SIGINT, signal.default_int_handler)
    runner = BehaveXRunner(paths=[{os.path.join(api_runner_features_path, 'slow_scenarios')!r}], no_report=True,
                           parallel_processes=2, parallel_scheme='scenario',
                           on_progress=_stop_and_press_ctrl_c_on_first_event)
    raised = _capture_raised(runner.run)
    print("__RESULT__:" + json.dumps({{"raised": raised, "live_children": len(multiprocessing.active_children())}}))
"""
    _store_result(context, _run_script(script, start_new_session=True))


@then('the run raised no exception and none of its processes is still running')
def then_no_exception_and_no_live_children(context):
    result = context.api_run_result
    assert result['raised'] is None and result['live_children'] == 0, (
        f'Got {result}.\nOutput:\n{context.api_run_output}'
    )


@then('the run raised no exception and the first scenario passed while the others did not run')
def then_partial_results_after_ctrl_c(context):
    result = context.api_run_result
    statuses = result['statuses']
    assert result['raised'] is None and statuses.get('Slow scenario 01') == 'passed' and statuses.get(
        'Slow scenario 03') not in (None, 'passed'), f'Got {result}.\nOutput:\n{context.api_run_output}'


@then('the run raised no exception and a multiprocessing child the host started itself is still running')
def then_no_exception_and_host_child_still_running(context):
    result = context.api_run_result
    assert result['raised'] is None and result['host_child_alive'] is True, (
        f'Got {context.api_run_result}.\nOutput:\n{context.api_run_output}'
    )


@when('I run BehaveXRunner {mode} on a @SERIAL scenario that kills its worker')
def when_run_with_crashing_worker(context, mode):
    script = f"""
import json, sys
{_CAPTURE_RAISED}
if __name__ == '__main__':
    results = []
    raised = _capture_raised(lambda: results.append(BehaveXRunner(
        paths=[{os.path.join(api_runner_features_path, 'crashing_worker')!r}], no_report=True,
        **{_RUN_MODES[mode]!r}).run()))
    print("__RESULT__:" + json.dumps({{"raised": raised, "exit_code": results[0].exit_code if results else None,
                                      "stopped": results[0].stopped if results else None}}))
"""
    _store_result(context, _run_script(script))


@then('the run raised no exception, the RunResult exit_code is "{exit_code}" and it was not stopped')
def then_no_exception_exit_code_not_stopped(context, exit_code):
    result = context.api_run_result
    assert result['raised'] is None and result['exit_code'] == int(exit_code) and result['stopped'] is False, (
        f'Expected no exception, exit_code {exit_code} and not stopped, got {result}.\n'
        f'Output:\n{context.api_run_output}'
    )

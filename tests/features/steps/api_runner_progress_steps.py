import os
from typing import List, Optional

from api_runner_support import (
    _PROGRESS_CALLBACK,
    _SERIALIZE_PROGRESS,
    BEHAVE_ERROR_STATUS,
    _run_script,
    _store_result,
    api_runner_features_path,
    secondary_features_path,
)
from behave import then, when

_RAISING_ON_FIRST_CALL_PROGRESS_CALLBACK = _PROGRESS_CALLBACK + """
    if len(_events) == 1:
        raise RuntimeError("boom")
"""


_RAISING_PROGRESS_CALLBACK = """
def _on_progress(event):
    raise RuntimeError("boom")
"""


_SERIALIZE_EXIT_CODE_ONLY = """
_data = {"exit_code": result.exit_code, "event_count": 0, "events": []}
print("__RESULT__:" + json.dumps(_data))
"""


@then('the RunResult summary untested is "{expected}"')
def then_summary_untested(context, expected):
    actual = context.api_run_result['summary']['untested']
    assert actual == int(expected), (
        f'Expected summary.untested={expected}, got {actual}.'
    )


def _run_with_progress_callback(
    context,
    feature_path: str,
    callback_snippet: str = _PROGRESS_CALLBACK,
    parallel_processes: int = 1,
    parallel_scheme: str = 'scenario',
    serialize_snippet: str = _SERIALIZE_PROGRESS,
    stop_on_failure: bool = False,
    tags: Optional[List[str]] = None,
    name: Optional[str] = None,
) -> None:
    script = f"""
import json, sys
{callback_snippet}
result = BehaveXRunner(
    paths=[{repr(feature_path)}],
    tags={repr(tags or [])},
    no_report=True,
    parallel_processes={parallel_processes},
    parallel_scheme={repr(parallel_scheme)},
    stop_on_failure={stop_on_failure},
    name={name!r},
    on_progress=_on_progress,
).run()
""" + serialize_snippet
    proc = _run_script(script)
    _store_result(context, proc)


@when('I run BehaveXRunner with passing tests and an on_progress callback')
def when_api_run_with_progress_callback(context):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    _run_with_progress_callback(context, feature_path)


@when('I run BehaveXRunner with passing tests using "{parallel_processes}" parallel processes, "{parallel_scheme}" scheme, and an on_progress callback')
def when_api_run_parallel_with_progress_callback(context, parallel_processes, parallel_scheme):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    _run_with_progress_callback(
        context,
        feature_path,
        parallel_processes=int(parallel_processes),
        parallel_scheme=parallel_scheme,
    )


@when('I run BehaveXRunner with stop_on_failure on a failure followed by passing scenarios using "{parallel_processes}" parallel processes and an on_progress callback')
def when_api_run_stop_on_failure_with_progress_callback(context, parallel_processes):
    _run_with_progress_callback(
        context,
        os.path.join(api_runner_features_path, 'stop_on_failure.feature'),
        parallel_processes=int(parallel_processes),
        stop_on_failure=True,
    )


@when('I run BehaveXRunner on @SERIAL and parallel scenarios using "{parallel_processes}" parallel processes, "{parallel_scheme}" scheme, and an on_progress callback')
def when_api_run_serial_mix_with_progress_callback(context, parallel_processes, parallel_scheme):
    _run_with_progress_callback(
        context,
        os.path.join(api_runner_features_path, 'serial_mix'),
        parallel_processes=int(parallel_processes),
        parallel_scheme=parallel_scheme,
    )


@when('I run BehaveXRunner with passing tests and an on_progress callback that always raises')
def when_api_run_with_raising_progress_callback(context):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    _run_with_progress_callback(
        context,
        feature_path,
        callback_snippet=_RAISING_PROGRESS_CALLBACK,
        serialize_snippet=_SERIALIZE_EXIT_CODE_ONLY,
    )


@when('I run BehaveXRunner with passing tests and an on_progress callback that raises on its first call')
def when_api_run_with_raising_once_progress_callback(context):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    _run_with_progress_callback(
        context,
        feature_path,
        callback_snippet=_RAISING_ON_FIRST_CALL_PROGRESS_CALLBACK,
    )


@then('each on_progress event has a non-empty scenario_name and feature_name')
def then_progress_events_have_names(context):
    events = context.api_run_result['events']
    assert events, 'No on_progress events were captured.'
    for i, event in enumerate(events):
        assert event['scenario_name'], f'Event {i} has empty scenario_name: {event}'
        assert event['feature_name'], f'Event {i} has empty feature_name: {event}'


@then('each on_progress event has a status of "{expected_status}"')
def then_progress_events_have_status(context, expected_status):
    events = context.api_run_result['events']
    assert events, 'No on_progress events were captured.'
    for i, event in enumerate(events):
        assert event['status'] == expected_status, (
            f'Event {i} has status "{event["status"]}", expected "{expected_status}": {event}'
        )


@then('the completed_count in on_progress events is strictly increasing up to the summary total')
def then_progress_completed_count_strictly_increasing(context):
    events = context.api_run_result['events']
    assert events, 'No on_progress events were captured.'
    completed_values = [e['completed_count'] for e in events]
    for i in range(1, len(completed_values)):
        assert completed_values[i] > completed_values[i - 1], (
            f'completed_count is not strictly increasing at index {i}: {completed_values}'
        )
    assert completed_values[-1] == context.api_run_result['summary_total'], (
        f'Expected the last completed_count to be {context.api_run_result["summary_total"]}: {completed_values}'
    )


@when('I run BehaveXRunner with failing tests and an on_progress callback')
def when_api_run_failing_with_progress_callback(context):
    feature_path = os.path.join(secondary_features_path, 'failing_tests.feature')
    _run_with_progress_callback(context, feature_path)


@when('I run BehaveXRunner with failing tests using "{parallel_processes}" parallel processes, "{parallel_scheme}" scheme, and an on_progress callback')
def when_api_run_failing_parallel_with_progress_callback(context, parallel_processes, parallel_scheme):
    feature_path = os.path.join(secondary_features_path, 'failing_tests.feature')
    _run_with_progress_callback(
        context,
        feature_path,
        parallel_processes=int(parallel_processes),
        parallel_scheme=parallel_scheme,
    )


@then('at least one on_progress event has behave\'s error status')
def then_at_least_one_progress_event_has_behave_error_status(context):
    then_at_least_one_progress_event_has_status(context, BEHAVE_ERROR_STATUS)


@then('at least one on_progress event has a status of "{expected_status}"')
def then_at_least_one_progress_event_has_status(context, expected_status):
    events = context.api_run_result['events']
    assert events, 'No on_progress events were captured.'
    matching = [e for e in events if e['status'] == expected_status]
    assert matching, (
        f'No on_progress event with status "{expected_status}" found.\n'
        f'Events: {events}'
    )


@when('I run BehaveXRunner on @AUTORETRY scenarios that pass on a retry or fail every attempt with an on_progress callback')
def when_api_run_autoretry_with_progress_callback(context):
    _run_with_progress_callback(context, os.path.join(api_runner_features_path, 'autoretry_flaky.feature'))


@when('I run BehaveXRunner on @AUTORETRY scenarios whose step raises an error or whose teardown fails on every attempt with an on_progress callback')
def when_api_run_autoretry_errors_with_progress_callback(context):
    _run_with_progress_callback(
        context, os.path.join(api_runner_features_path, 'teardown_error', 'autoretry_errors.feature')
    )


@when('I run BehaveXRunner with tags "{tags}" on @AUTORETRY scenarios, one excluded by the tag filter, with an on_progress callback')
def when_api_run_filtered_autoretry_with_progress_callback(context, tags):
    _run_with_progress_callback(
        context, os.path.join(api_runner_features_path, 'autoretry_filtered.feature'), tags=[tags]
    )


@when('I run BehaveXRunner with name "{name}" on an @AUTORETRY Scenario Outline with an on_progress callback')
def when_api_run_name_filtered_autoretry_outline_with_progress_callback(context, name):
    _run_with_progress_callback(
        context, os.path.join(api_runner_features_path, 'autoretry_outline_by_name.feature'), name=name
    )


@then('no on_progress event is for the scenario "{scenario_name}"')
def then_no_progress_event_for_scenario(context, scenario_name):
    events = context.api_run_result['events']
    assert all(e['scenario_name'] != scenario_name for e in events), (
        f'Unexpected on_progress event for "{scenario_name}": {events}'
    )


@when('I run BehaveXRunner on passing scenarios, one with a failing after_scenario hook, with an on_progress callback')
def when_api_run_failing_teardown_with_progress_callback(context):
    _run_with_progress_callback(
        context, os.path.join(api_runner_features_path, 'teardown_error', 'teardown_error.feature')
    )


@when('I run BehaveXRunner on passing scenarios, one with a failing cleanup and one with a failing after_tag hook, with an on_progress callback')
def when_api_run_late_teardown_errors_with_progress_callback(context):
    _run_with_progress_callback(
        context, os.path.join(api_runner_features_path, 'teardown_error', 'late_teardown_errors.feature')
    )


@then("each on_progress event status matches the scenario's final status in the RunResult")
def then_progress_status_matches_final_status(context):
    final_statuses = context.api_run_result['final_statuses']
    reported = {e['scenario_name']: e['status'] for e in context.api_run_result['events']}
    assert reported == final_statuses, (
        f'on_progress statuses {reported} differ from the final statuses {final_statuses}.\n'
        f'BehaveXRunner output:\n{context.api_run_output}'
    )


@then('each on_progress event has the summary total as its total')
def then_progress_events_have_summary_total(context):
    result = context.api_run_result
    totals = [event['total'] for event in result['events']]
    assert totals and all(total == result['summary_total'] for total in totals), (
        f'Expected every event total to be {result["summary_total"]}, got {totals}.\n'
        f'BehaveXRunner output:\n{context.api_run_output}'
    )


@when('I run BehaveXRunner in a single process on passing tests, noting the output that had arrived at each '
      'on_progress event')
def when_run_noting_output_at_each_event(context):
    feature_path = os.path.join(secondary_features_path, 'passing_tests.feature')
    script = f"""
import contextlib, io, json, sys

if __name__ == '__main__':
    redirected = io.StringIO()
    output_at_events = []
    with contextlib.redirect_stdout(redirected):
        BehaveXRunner(paths=[{feature_path!r}], no_report=True,
                      on_progress=lambda event: output_at_events.append(redirected.getvalue())).run()
    print("__RESULT__:" + json.dumps({{"output_at_events": output_at_events}}))
"""
    _store_result(context, _run_script(script))


@then('the first on_progress event arrived before behave printed its summary')
def then_first_event_arrived_before_summary(context):
    output_at_events = context.api_run_result['output_at_events']
    # behave's summary line, printed once every scenario has run
    assert output_at_events and 'scenarios passed' not in output_at_events[0], (
        f'Expected the first event before behave\'s summary, got the output:\n{output_at_events[:1]}'
    )

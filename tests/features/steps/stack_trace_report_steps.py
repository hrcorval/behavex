import os

from behave import then, when
from execution_steps import execute_command, get_unique_suffix, tests_features_path


@when('I run the behavex command with chained exception tests')
def when_run_chained_exception_tests(context):
    context.output_path = os.path.join('output', 'output_{}'.format(get_unique_suffix()))
    execution_args = [
        'behavex',
        os.path.join(tests_features_path, 'chained_exception_features', 'chained_exception_tests.feature'),
        '-o', context.output_path,
    ]
    execute_command(context, execution_args)


@when('I run the behavex command with only passing chained exception test')
def when_run_only_passing_chained_exception_test(context):
    context.output_path = os.path.join('output', 'output_{}'.format(get_unique_suffix()))
    execution_args = [
        'behavex',
        os.path.join(tests_features_path, 'chained_exception_features', 'chained_exception_tests.feature'),
        '-t', '@PASSING_SCENARIO',
        '-o', context.output_path,
    ]
    execute_command(context, execution_args)


@then('the HTML report should contain clickable stack trace markers for failed scenarios')
def then_html_report_contains_clickable_stack_trace_markers(context):
    html_report_path = os.path.join(context.output_path, 'report.html')
    assert os.path.exists(html_report_path), f"HTML report not found at {html_report_path}"
    with open(html_report_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    # Use ' data-stack-trace' (leading space) to match the HTML attribute, not the JS selector [data-stack-trace]
    assert ' data-stack-trace' in html_content, \
        "Expected HTML report to contain 'data-stack-trace' HTML attribute on failed scenario error elements"
    # clickable-trace only appears inside rendered <pre> class attributes, never in JS or CSS
    assert 'clickable-trace' in html_content, \
        "Expected HTML report to contain 'clickable-trace' CSS class on failed scenario error elements"


@then('the HTML report should contain hidden stack trace content blocks')
def then_html_report_contains_stack_trace_content(context):
    html_report_path = os.path.join(context.output_path, 'report.html')
    assert os.path.exists(html_report_path), f"HTML report not found at {html_report_path}"
    with open(html_report_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    assert 'stack-trace-content' in html_content, \
        "Expected HTML report to contain hidden 'stack-trace-content' div blocks with full stack trace"
    assert 'Traceback (most recent call last)' in html_content, \
        "Expected stack trace content to include Python traceback header"


@then('the HTML report should contain the chained exception cause chain')
def then_html_report_contains_chained_exception_chain(context):
    html_report_path = os.path.join(context.output_path, 'report.html')
    assert os.path.exists(html_report_path), f"HTML report not found at {html_report_path}"
    with open(html_report_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    assert 'The above exception was the direct cause of the following exception' in html_content, \
        "Expected HTML report to contain Python's chained exception cause marker for chained exceptions"


@then('the HTML report should not contain stack trace markers')
def then_html_report_has_no_stack_trace_markers(context):
    html_report_path = os.path.join(context.output_path, 'report.html')
    assert os.path.exists(html_report_path), f"HTML report not found at {html_report_path}"
    with open(html_report_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    # ' data-stack-trace' (leading space) matches the HTML attribute only, not the JS selector [data-stack-trace]
    assert ' data-stack-trace' not in html_content, \
        "Expected passing-only HTML report to not render 'data-stack-trace' attribute on any scenario element"
    # clickable-trace only appears inside rendered <pre> class attributes, so a plain search is reliable
    assert 'clickable-trace' not in html_content, \
        "Expected passing-only HTML report to not render 'clickable-trace' CSS class on any scenario element"

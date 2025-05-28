import logging
import os
import sys
from pathlib import Path

from behave import given, then, when

# Add the project root to the path so we can import behavex modules
root_project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, root_project_path)

from behavex.outputs.formatters.allure_behavex_formatter import \
    AllureBehaveXFormatter


@given('I have an AllureBehaveXFormatter instance')
def step_impl(context):
    context.formatter = AllureBehaveXFormatter()


@when('I test the MIME type detection for various file extensions')
def step_impl(context):
    test_cases = [
        ('test.png', 'image/png'),
        ('test.jpg', 'image/jpeg'),
        ('test.jpeg', 'image/jpeg'),
        ('test.gif', 'image/gif'),
        ('test.pdf', 'application/pdf'),
        ('test.txt', 'text/plain'),
        ('test.csv', 'text/csv'),
        ('test.json', 'application/json'),
        ('test.xml', 'application/xml'),
        ('test.zip', 'application/zip'),
        ('test.mp4', 'video/mp4'),
        ('test.unknown', 'application/octet-stream'),
    ]

    context.mime_results = []
    for filename, expected_mime in test_cases:
        actual_mime = context.formatter._get_mime_type(filename)
        context.mime_results.append({
            'filename': filename,
            'expected': expected_mime,
            'actual': actual_mime,
            'matches': actual_mime == expected_mime
        })


@then('I should see correct MIME types returned for all supported formats')
def step_impl(context):
    failures = []
    for result in context.mime_results:
        if not result['matches']:
            failures.append(f"File '{result['filename']}': expected '{result['expected']}', got '{result['actual']}'")

    assert len(failures) == 0, f"MIME type detection failures: {failures}"


@when('I test error message sanitization with various inputs')
def step_impl(context):
    test_cases = [
        ('Simple error message', 'Simple error message'),
        ('A very long error message that exceeds fifty characters and should be truncated', 'A very long error message that exceeds fifty ch...'),
        ('Multi-line\nerror message\nwith newlines', 'Multi-line'),
        ('', 'Unknown Error'),
        (None, 'Unknown Error'),
        ('   \n  \t  ', 'Unknown Error'),
    ]

    context.sanitization_results = []
    for input_msg, expected_output in test_cases:
        actual_output = context.formatter._sanitize_error_message(input_msg)
        context.sanitization_results.append({
            'input': input_msg,
            'expected': expected_output,
            'actual': actual_output,
            'matches': actual_output == expected_output
        })


@then('I should see properly sanitized error messages')
def step_impl(context):
    failures = []
    for result in context.sanitization_results:
        if not result['matches']:
            failures.append(f"Input '{result['input']}': expected '{result['expected']}', got '{result['actual']}'")

    assert len(failures) == 0, f"Error message sanitization failures: {failures}"


@when('I test package name extraction from various file paths')
def step_impl(context):
    test_cases = [
        ('features/automated/user/login.feature', 'automated.user'),
        ('tests/features/manual/admin/users.feature', 'manual.admin'),
        ('features/api/products.feature', 'api'),
        ('simple.feature', 'default'),
        ('', 'default'),
        (None, 'default'),
        ('deep/nested/features/automated/module/submodule/test.feature', 'automated.module.submodule'),
    ]

    context.package_results = []
    for input_path, expected_package in test_cases:
        actual_package = context.formatter._get_package_from_path(input_path)
        context.package_results.append({
            'input': input_path,
            'expected': expected_package,
            'actual': actual_package,
            'matches': actual_package == expected_package
        })


@then('I should see correct package names extracted')
def step_impl(context):
    failures = []
    for result in context.package_results:
        if not result['matches']:
            failures.append(f"Path '{result['input']}': expected '{result['expected']}', got '{result['actual']}'")

    assert len(failures) == 0, f"Package name extraction failures: {failures}"


@when('I test table formatting with sample table data')
def step_impl(context):
    test_cases = [
        # Test case 1: Simple table
        (
            {
                'name': ['Alice', 'Bob'],
                'age': ['30', '25'],
                'city': ['New York', 'Los Angeles']
            },
            'name,age,city\nAlice,30,New York\nBob,25,Los Angeles\n'
        ),
        # Test case 2: Empty table
        ({}, ''),
        # Test case 3: Single column table
        (
            {'status': ['passed', 'failed']},
            'status\npassed\nfailed\n'
        ),
    ]

    context.table_results = []
    for input_table, expected_csv in test_cases:
        actual_csv = context.formatter._format_table_as_csv(input_table)
        # Normalize line endings for cross-platform compatibility
        actual_csv_normalized = actual_csv.replace('\r\n', '\n')
        context.table_results.append({
            'input': input_table,
            'expected': expected_csv,
            'actual': actual_csv_normalized,
            'matches': actual_csv_normalized == expected_csv
        })


@then('I should see properly formatted CSV output')
def step_impl(context):
    failures = []
    for result in context.table_results:
        if not result['matches']:
            failures.append(f"Table {result['input']}: expected '{result['expected']}', got '{result['actual']}'")

    assert len(failures) == 0, f"Table formatting failures: {failures}"


@when('I test step line extraction from various image filenames')
def step_impl(context):
    test_cases = [
        ('scenario_hash_123_0001500001.png', 15),
        ('another_hash_456_0007800002.jpg', 78),
        ('test_hash_0000300001.png', 3),
        ('invalid_format.png', None),
        ('no_numbers.jpg', None),
        ('', None),
    ]

    context.step_line_results = []
    for input_filename, expected_line in test_cases:
        actual_line = context.formatter._get_step_line_from_image(input_filename)
        context.step_line_results.append({
            'input': input_filename,
            'expected': expected_line,
            'actual': actual_line,
            'matches': actual_line == expected_line
        })


@then('I should see correct step line numbers extracted')
def step_impl(context):
    failures = []
    for result in context.step_line_results:
        if not result['matches']:
            failures.append(f"Filename '{result['input']}': expected '{result['expected']}', got '{result['actual']}'")

    assert len(failures) == 0, f"Step line extraction failures: {failures}"

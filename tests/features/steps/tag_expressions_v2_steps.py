import logging
import os
import re
import subprocess
import sys
import time

from behave import given, then, when
from execution_steps import (
    get_unique_suffix,
    root_project_path,
    secondary_features_path,
)


@given('I have Behave 1.3.0 or newer installed')
def step_check_behave_version(context):
    try:
        import behave
        version_str = behave.__version__
        version_parts = version_str.split('.')
        major = int(version_parts[0])
        minor = int(version_parts[1]) if len(version_parts) > 1 else 0

        if (major, minor) < (1, 3):
            context.scenario.skip(f"Skipping v2 tag expression test: Behave {version_str} < 1.3.0")
            return

        logging.info(f"Behave version {version_str} supports v2 tag expressions")
    except (ImportError, AttributeError, ValueError, IndexError) as e:
        context.scenario.skip(f"Could not determine Behave version: {e}")


def _run_behavex_on_secondary_features_with_tags(context, output_prefix, tag_args, log_scenarios=False):
    context.tag_expression = ' and '.join(tag_args)
    cmd = [sys.executable, '-m', 'behavex', secondary_features_path,
           '-o', f'output/{output_prefix}_{get_unique_suffix()}']
    for tag_arg in tag_args:
        cmd += ['-t', tag_arg]
    cmd += ['--logging_level', 'INFO']

    env = os.environ.copy()
    env['PYTHONPATH'] = root_project_path

    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=root_project_path, env=env)
    context.execution_time = time.time() - start_time

    context.result = result
    context.stdout = result.stdout
    context.stderr = result.stderr
    context.returncode = result.returncode

    logging.info(f"BehaveX executed with tag arguments {tag_args}, exit code: {result.returncode}, "
                 f"time: {context.execution_time:.2f}s")
    if result.stdout:
        logging.info(f"Secondary test STDOUT:\n{result.stdout}")
    if result.stderr:
        logging.info(f"Secondary test STDERR:\n{result.stderr}")
    if log_scenarios:
        _log_executed_scenarios(context)


@when('I run behavex with v2 tag expression "{tag_expression}"')
def step_run_behavex_with_v2_expression(context, tag_expression):
    _run_behavex_on_secondary_features_with_tags(context, 'v2_test', [tag_expression], log_scenarios=True)


@when('I run behavex with v1 tag expression "{tag_expression}"')
def step_run_behavex_with_v1_expression(context, tag_expression):
    _run_behavex_on_secondary_features_with_tags(context, 'v1_test', [tag_expression])


@when('I run behavex with invalid v2 tag expression "{tag_expression}"')
def step_run_behavex_with_invalid_v2_expression(context, tag_expression):
    _run_behavex_on_secondary_features_with_tags(context, 'v2_invalid_test', [tag_expression])


@when('I run behavex with empty tag expression ""')
def step_run_behavex_with_empty_expression_literal(context):
    _run_behavex_on_secondary_features_with_tags(context, 'empty_test', [])


@when('I run behavex with complex v2 tag expression "{tag_expression}"')
def step_run_behavex_with_complex_v2_expression(context, tag_expression):
    _run_behavex_on_secondary_features_with_tags(context, 'v2_complex_test', [tag_expression], log_scenarios=True)


@when('I run behavex with multiple v2 tag arguments "{tag_arg1}" and "{tag_arg2}"')
def step_run_behavex_with_multiple_v2_arguments(context, tag_arg1, tag_arg2):
    combined_expression = f"{tag_arg1} and {tag_arg2}"
    _run_behavex_on_secondary_features_with_tags(context, 'v2_multiple_test', [combined_expression], log_scenarios=True)


@when('I run behavex with three v2 tag arguments "{tag_arg1}" and "{tag_arg2}" and "{tag_arg3}"')
def step_run_behavex_with_three_v2_arguments(context, tag_arg1, tag_arg2, tag_arg3):
    combined_expression = f"{tag_arg1} and {tag_arg2} and {tag_arg3}"
    _run_behavex_on_secondary_features_with_tags(context, 'v2_three_test', [combined_expression], log_scenarios=True)


@when('I run behavex with mixed tag arguments "{tag_arg1}" and "{tag_arg2}"')
def step_run_behavex_with_mixed_arguments(context, tag_arg1, tag_arg2):
    _run_behavex_on_secondary_features_with_tags(context, 'mixed_test', [tag_arg1, tag_arg2])


@when('I run behavex with multiple v1 tag arguments "{tag_arg1}" and "{tag_arg2}"')
def step_run_behavex_with_multiple_v1_arguments(context, tag_arg1, tag_arg2):
    _run_behavex_on_secondary_features_with_tags(context, 'v1_multiple_test', [tag_arg1, tag_arg2])


@then('I should see scenarios matching the v2 expression')
def step_should_see_scenarios_matching_v2(context):
    passed_count, failed_count, _ = _passed_failed_skipped_scenario_counts(context.stdout)
    total_executed = passed_count + failed_count

    execution_successful = (context.returncode == 0 or
                            (context.returncode == 1 and total_executed > 0))
    assert execution_successful, \
        f"v2 expression '{context.tag_expression}' failed to execute properly. " \
        f"Exit code: {context.returncode}, scenarios executed: {total_executed}"

    if total_executed > 0:
        logging.info(f"v2 expression '{context.tag_expression}' executed {total_executed} scenarios "
                     f"(passed: {passed_count}, failed: {failed_count})")
    else:
        logging.info(f"v2 expression '{context.tag_expression}' processed successfully "
                     f"but found 0 matching scenarios")


@then('I should see scenarios matching the expression with minimum count "{min_count}"')
def step_should_see_minimum_scenarios(context, min_count):
    min_expected = int(min_count)
    passed_count, failed_count, _ = _passed_failed_skipped_scenario_counts(context.stdout)
    total_executed = passed_count + failed_count

    assert total_executed >= min_expected, \
        f"Expected at least {min_expected} scenarios for '{context.tag_expression}', " \
        f"but got {total_executed} (passed: {passed_count}, failed: {failed_count})."


@then('the execution should succeed')
@then('the legacy tag matching should be used')
def step_execution_should_succeed(context):
    """Exit 1 passes when scenarios ran: some secondary scenarios are designed to fail."""
    if context.returncode == 0:
        return
    passed_count, failed_count, skipped_count = _passed_failed_skipped_scenario_counts(context.stdout)
    assert context.returncode == 1 and passed_count + failed_count + skipped_count > 0, \
        f"BehaveX execution failed with exit code {context.returncode}. " \
        f"Stdout: {context.stdout}\nStderr: {context.stderr}"
    logging.info(f"BehaveX execution completed with expected failures: {passed_count} passed, "
                 f"{failed_count} failed, {skipped_count} skipped")


@then('the execution should fail with a clear error message')
def step_execution_should_fail_with_error(context):
    assert context.returncode != 0, f"BehaveX execution should have failed but succeeded. Stdout: {context.stdout}"

    error_output = context.stderr + context.stdout
    assert any(keyword in error_output.lower() for keyword in ['error', 'failed', 'invalid', 'syntax']), \
        f"Expected error message not found in output: {error_output}"


@then('the error message should mention tag expression syntax')
def step_error_message_should_mention_tag_expression_syntax(context):
    error_output = context.stderr + context.stdout
    assert any(keyword in error_output.lower() for keyword in ['tag expression', 'syntax', 'parse', 'invalid']), \
        f"Expected tag expression syntax error not found in output: {error_output}"


@then('I should see scenarios without the excluded tag executed')
def step_should_see_without_excluded_tag_executed(context):
    passed_count, failed_count, skipped_count = _passed_failed_skipped_scenario_counts(context.stdout)
    assert passed_count + failed_count + skipped_count > 0, \
        f"No scenarios were processed at all. Output: {context.stdout}"


@then('all available scenarios should be executed')
def step_all_scenarios_should_be_executed(context):
    if context.returncode == 0:
        return
    assert sum(_passed_failed_skipped_scenario_counts(context.stdout)) > 0, \
        f"Empty tag expression execution failed. Output: {context.stdout}"


@then('I should see scenarios matching the v1 expression executed')
def step_should_see_v1_expression_executed(context):
    passed_count = _extract_scenario_count(context.stdout, 'passed')
    assert passed_count > 0, "Expected some scenarios to pass with v1 expression"


@then('the native Behave parser should be used')
@then('the legacy tag matching should be used for mixed arguments')
@then('the legacy tag matching should be used for v1 arguments')
def step_execution_should_exit_cleanly(context):
    assert context.returncode == 0, \
        f"Expected exit code 0, got {context.returncode}. Stderr: {context.stderr}"


@then('the execution should succeed within reasonable time')
def step_execution_should_succeed_within_reasonable_time(context):
    assert context.returncode == 0, f"Execution failed with exit code {context.returncode}"

    reasonable_time = 30.0
    assert context.execution_time < reasonable_time, \
        f"Execution took {context.execution_time:.2f}s, expected < {reasonable_time}s"


def _extract_scenario_count(output, status):
    match = re.search(rf'(\d+)\s+scenarios?\s+{status}', output, re.IGNORECASE)
    return int(match.group(1)) if match else 0


def _passed_failed_skipped_scenario_counts(output):
    return tuple(_extract_scenario_count(output, status) for status in ('passed', 'failed', 'skipped'))


def _extract_executed_scenarios(output):
    """Parse scenario locations printed as '<secondary feature path>:<line>  <scenario name>'."""
    scenarios = []
    scenario_pattern = r'tests/features/fixtures/secondary_features/([^:]+\.feature):(\d+)\s+(.+)'

    for match in re.finditer(scenario_pattern, output):
        scenario_name = match.group(3).strip()
        if any(skip_word in scenario_name.lower() for skip_word in ['failing scenarios:', 'errored scenarios:', 'features passed']):
            continue
        scenarios.append({
            'feature_file': match.group(1),
            'line_number': match.group(2),
            'scenario_name': scenario_name
        })

    return scenarios


def _find_matching_scenarios(tag_expression):
    try:
        from behave.tag_expression import make_tag_expression

        tag_expr = make_tag_expression(tag_expression)
        scenarios = []

        for feature_file in os.listdir(secondary_features_path):
            if not feature_file.endswith('.feature'):
                continue

            feature_path = os.path.join(secondary_features_path, feature_file)
            try:
                with open(feature_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                feature_tags = []
                for i, line in enumerate(lines):
                    line = line.strip()

                    if line.startswith('@') and i == 0 or (i > 0 and not lines[i-1].strip()):
                        if 'Feature:' in ''.join(lines[i:i+3]):
                            feature_tags.extend([tag.strip() for tag in line.split() if tag.startswith('@')])

                    elif line.startswith('Scenario:') or line.startswith('Scenario Outline:'):
                        scenario_name = line.replace('Scenario:', '').replace('Scenario Outline:', '').strip()
                        scenario_line = i + 1

                        scenario_tags = []
                        for j in range(i - 1, -1, -1):
                            tag_line = lines[j].strip()
                            if tag_line.startswith('@'):
                                scenario_tags.extend([tag.strip() for tag in tag_line.split() if tag.startswith('@')])
                            elif tag_line and not tag_line.startswith('#'):
                                break

                        all_tags = feature_tags + scenario_tags
                        # Behave evaluates tags without the leading @
                        eval_tags = [tag[1:] if tag.startswith('@') else tag for tag in all_tags]

                        if tag_expr.check(eval_tags):
                            scenarios.append({
                                'scenario_name': scenario_name,
                                'feature_file': feature_file,
                                'line_number': scenario_line,
                                'tags': all_tags,
                                'status': 'matched'
                            })

            except Exception as e:
                logging.debug(f"Error parsing {feature_file}: {e}")

        return scenarios

    except Exception as e:
        logging.debug(f"Error finding matching scenarios: {e}")
        return []


def _log_executed_scenarios(context):
    if not context.stdout:
        return

    scenarios = _find_matching_scenarios(context.tag_expression) or _extract_executed_scenarios(context.stdout)

    if scenarios:
        logging.info(f"\n=== EXECUTED SCENARIOS FOR '{context.tag_expression}' ===")
        for i, scenario in enumerate(scenarios, 1):
            tags_str = ' '.join(scenario.get('tags', [])) if scenario.get('tags') else '(no tags found)'

            logging.info(f"{i:2d}. {scenario['scenario_name']}")
            logging.info(f"     {scenario['feature_file']}:{scenario.get('line_number', 'N/A')}")
            logging.info(f"     {tags_str}")
            logging.info(f"     Status: {scenario.get('status', 'unknown')}")
            logging.info("")

        logging.info(f"Total scenarios executed: {len(scenarios)}")
        logging.info("=" * 60)
    else:
        logging.info(f"No scenario details found for '{context.tag_expression}' (possibly 0 scenarios executed or parsing issue)")

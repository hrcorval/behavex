"""
Step definitions for execution summary validation testing - using existing BehaveX patterns
"""
import os
import re

from behave import given, then, when

# This file provides additional validation steps for execution summary testing
# It leverages the existing execution_steps.py infrastructure to avoid code duplication

def parse_execution_summary(stdout):
    """Parse execution summary from BehaveX stdout - helper function for validation"""
    summary = {
        'features': {},
        'scenarios': {},
        'steps': {}
    }

    lines = stdout.split('\n')

    for line in lines:
        line = line.strip()

        # Parse features line: "X features passed, Y failed, Z skipped"
        features_match = re.search(r'(\d+)\s+features?\s+passed,\s*(\d+)\s+failed(?:,\s*(\d+)\s+error)?(?:,\s*(\d+)\s+skipped)?(?:,\s*(\d+)\s+untested)?', line)
        if features_match:
            summary['features']['passed'] = int(features_match.group(1))
            summary['features']['failed'] = int(features_match.group(2))
            summary['features']['error'] = int(features_match.group(3) or 0)
            summary['features']['skipped'] = int(features_match.group(4) or 0)
            summary['features']['untested'] = int(features_match.group(5) or 0)
            continue

        # Parse scenarios line: "X scenarios passed, Y failed, Z skipped"
        scenarios_match = re.search(r'(\d+)\s+scenarios?\s+passed,\s*(\d+)\s+failed(?:,\s*(\d+)\s+error)?(?:,\s*(\d+)\s+skipped)?(?:,\s*(\d+)\s+untested)?', line)
        if scenarios_match:
            summary['scenarios']['passed'] = int(scenarios_match.group(1))
            summary['scenarios']['failed'] = int(scenarios_match.group(2))
            summary['scenarios']['error'] = int(scenarios_match.group(3) or 0)
            summary['scenarios']['skipped'] = int(scenarios_match.group(4) or 0)
            summary['scenarios']['untested'] = int(scenarios_match.group(5) or 0)
            continue

        # Parse steps line: "X steps passed, Y failed, Z skipped, W undefined"
        steps_match = re.search(r'(\d+)\s+steps\s+passed,\s*(\d+)\s+failed(?:,\s*(\d+)\s+error)?(?:,\s*(\d+)\s+skipped)?(?:,\s*(\d+)\s+untested)?(?:,\s*(\d+)\s+undefined)?', line)
        if steps_match:
            summary['steps']['passed'] = int(steps_match.group(1))
            summary['steps']['failed'] = int(steps_match.group(2))
            summary['steps']['error'] = int(steps_match.group(3) or 0)
            summary['steps']['skipped'] = int(steps_match.group(4) or 0)
            summary['steps']['untested'] = int(steps_match.group(5) or 0)
            summary['steps']['undefined'] = int(steps_match.group(6) or 0)
            continue

    return summary


@then('the execution summaries should be identical between single and parallel execution')
def step_summaries_should_be_identical(context):
    """Validate that single and parallel execution produce identical summaries"""
    import logging

    # This step can be used after running both single and parallel executions
    # to validate they produce the same console output format
    # Parse the current execution summary
    current_summary = parse_execution_summary(context.result.stdout)

    # Store or compare the summary
    if not hasattr(context, 'reference_summary'):
        context.reference_summary = current_summary
        logging.info(f"Stored reference summary: {current_summary}")
    else:
        # Compare with reference
        reference = context.reference_summary
        for category in ['features', 'scenarios', 'steps']:
            for status in reference[category]:
                expected = reference[category][status]
                actual = current_summary[category].get(status, 0)
                assert actual == expected, f"Summary mismatch in {category}.{status}: expected {expected}, got {actual}"

        logging.info("✅ Execution summaries are identical between single and parallel execution")


@when('I run the behavex command on "{feature_path}" with "{parallel_processes}" parallel processes and parallel scheme set as "{parallel_scheme}"')
def step_run_behavex_with_feature_path_and_parallel(context, feature_path, parallel_processes, parallel_scheme):
    """Run BehaveX with specific feature path and parallel settings"""
    import os

    from tests.features.steps.execution_steps import (execute_command,
                                                      get_random_number)

    context.output_path = os.path.join('output', 'output_{}'.format(get_random_number(6)))

    # Handle multiple feature paths separated by spaces
    feature_paths = feature_path.split()
    execution_args = ['behavex'] + feature_paths + ['-o', context.output_path, '--parallel-processes', parallel_processes, '--parallel-scheme', parallel_scheme]
    execute_command(context, execution_args)


@then('the summary should not show error categories when there are no errors')
def step_no_error_categories_when_no_errors(context):
    """Verify that error categories are not shown when count is 0"""
    stdout = context.result.stdout

    # Check that ", 0 error" is not shown in summary lines
    summary_lines = [line for line in stdout.split('\n') if any(word in line for word in ['passed', 'failed', 'skipped'])]

    for line in summary_lines:
        assert ', 0 error' not in line, f"Error category should be hidden when count is 0: {line}"

    import logging
    logging.info("✅ Error categories are properly hidden when counts are zero")

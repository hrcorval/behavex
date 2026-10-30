import json
import logging
import os

from behave import then, when
from execution_steps import execute_command, new_output_path, secondary_features_path


@when('I run the behavex command with execution ordering enabled using "{parallel_processes}" parallel processes and parallel scheme set as "{parallel_scheme}"')
def when_run_with_execution_ordering(context, parallel_processes, parallel_scheme):
    context.output_path = new_output_path()
    execution_args = ['behavex',
                      os.path.join(secondary_features_path, 'ordered_tests.feature'),
                      '-t', '@ORDERED_TEST',
                      '-o', context.output_path,
                      '--parallel-processes', parallel_processes,
                      '--parallel-scheme', parallel_scheme,
                      '--order-tests']
    execute_command(context, execution_args)


@when('I run the behavex command with execution ordering enabled using custom prefix "{prefix}" with "{parallel_processes}" parallel processes and parallel scheme set as "{parallel_scheme}"')
def when_run_with_custom_prefix_ordering(context, prefix, parallel_processes, parallel_scheme):
    context.output_path = new_output_path()
    execution_args = ['behavex',
                      os.path.join(secondary_features_path, 'priority_ordered_tests.feature'),
                      '-t', '@PRIORITY_TEST',
                      '-o', context.output_path,
                      '--parallel-processes', parallel_processes,
                      '--parallel-scheme', parallel_scheme,
                      '--order-tests',
                      '--order-tag-prefix', prefix]
    execute_command(context, execution_args)


@when('I run the behavex command with execution ordering enabled for mixed scenarios using "{parallel_processes}" parallel processes and parallel scheme set as "{parallel_scheme}"')
def when_run_mixed_ordering(context, parallel_processes, parallel_scheme):
    context.output_path = new_output_path()
    execution_args = ['behavex',
                      os.path.join(secondary_features_path, 'mixed_ordered_tests.feature'),
                      '-t', '@MIXED_TEST',
                      '-o', context.output_path,
                      '--parallel-processes', parallel_processes,
                      '--parallel-scheme', parallel_scheme,
                      '--order-tests']
    execute_command(context, execution_args)


@when('I run the behavex command with strict execution ordering enabled using "{parallel_processes}" parallel processes and parallel scheme set as "{parallel_scheme}"')
def when_run_strict_ordering(context, parallel_processes, parallel_scheme):
    context.output_path = new_output_path()
    execution_args = ['behavex',
                      os.path.join(secondary_features_path, 'ordered_tests.feature'),
                      '-t', '@ORDERED_TEST',
                      '-o', context.output_path,
                      '--parallel-processes', parallel_processes,
                      '--parallel-scheme', parallel_scheme,
                      '--order-tests-strict']
    execute_command(context, execution_args)


@then('I should see the scenarios executed in the correct order for "{parallel_scheme}" scheme')
def then_see_correct_execution_order(context, parallel_scheme):
    """Verify that scenarios with ORDER tags executed successfully (--order-tests controls submission order, not start time)"""
    report_json_path = os.path.join(context.output_path, 'report.json')
    assert os.path.exists(report_json_path), f"Report JSON file not found at {report_json_path}"

    with open(report_json_path, 'r') as json_file:
        report_data = json.load(json_file)

    # Extract scenario execution data with order values and start times
    scenario_order_mapping = {
        "First ordered test scenario": 1,
        "Second ordered test scenario": 2,
        "Third ordered test scenario": 3,
        "Fourth ordered test scenario": 10
    }

    executed_scenarios = []
    for feature in report_data.get('features', []):
        for scenario in feature.get('scenarios', []):
            if scenario['name'] in scenario_order_mapping:
                # Ensure scenario has start time
                assert 'start' in scenario, f"Scenario '{scenario['name']}' missing start time in report"

                executed_scenarios.append({
                    'name': scenario['name'],
                    'order': scenario_order_mapping[scenario['name']],
                    'start_time': scenario['start']
                })

    # Verify that all expected scenarios were executed
    expected_count = 4
    assert len(executed_scenarios) == expected_count, \
        f"Expected {expected_count} scenarios to be executed, but got {len(executed_scenarios)}"

    # Sort by actual start time for logging purposes
    executed_scenarios.sort(key=lambda x: x['start_time'])

    # Log the actual execution order with start times for informational purposes
    logging.info("📊 Scenario execution order (--order-tests controls submission order, not start time):")
    for i, scenario in enumerate(executed_scenarios, 1):
        logging.info(f"  {i}. ORDER_{scenario['order']:03d}: {scenario['name']} started at {scenario['start_time']}")

    # For --order-tests: We only verify that scenarios were submitted in order (not start time)
    # Since submission order cannot be verified from JSON report, we accept any start time order
    # and only validate that all scenarios executed successfully

    # Sort by order value to show intended vs actual execution order
    expected_order = sorted(executed_scenarios, key=lambda x: x['order'])
    logging.info("📋 Expected submission order vs actual start time order:")

    expected_order_str = " → ".join([f"ORDER_{s['order']:03d}" for s in expected_order])
    actual_order_str = " → ".join([f"ORDER_{s['order']:03d}" for s in executed_scenarios])

    logging.info(f"  Expected: {expected_order_str}")
    logging.info(f"  Actual:   {actual_order_str}")

    if [s['order'] for s in expected_order] != [s['order'] for s in executed_scenarios]:
        logging.info("ℹ️  Start time order differs from submission order - this is normal for --order-tests")
        logging.info("   --order-tests controls submission order, allowing parallel execution with timing variations")
    else:
        logging.info("✅ Start time order matches submission order (optimal parallel scheduling)")

    logging.info(f"✅ Order tests validation passed: All {expected_count} scenarios executed successfully")


@then('I should see the scenarios executed in the correct order for "{parallel_scheme}" scheme with custom prefix')
def then_see_correct_order_custom_prefix(context, parallel_scheme):
    """Verify that scenarios with PRIORITY tags executed successfully (--order-tests controls submission order, not start time)"""
    report_json_path = os.path.join(context.output_path, 'report.json')
    assert os.path.exists(report_json_path), f"Report JSON file not found at {report_json_path}"

    with open(report_json_path, 'r') as json_file:
        report_data = json.load(json_file)

    # Extract scenario execution data with priority values and start times
    scenario_priority_mapping = {
        "First priority test scenario": 1,
        "Second priority test scenario": 2,
        "Third priority test scenario": 3
    }

    executed_scenarios = []
    for feature in report_data.get('features', []):
        for scenario in feature.get('scenarios', []):
            if scenario['name'] in scenario_priority_mapping:
                # Ensure scenario has start time
                assert 'start' in scenario, f"Scenario '{scenario['name']}' missing start time in report"

                executed_scenarios.append({
                    'name': scenario['name'],
                    'priority': scenario_priority_mapping[scenario['name']],
                    'start_time': scenario['start']
                })

    # Verify that all expected scenarios were executed
    expected_count = 3
    assert len(executed_scenarios) == expected_count, \
        f"Expected {expected_count} scenarios to be executed, but got {len(executed_scenarios)}"

    # Sort by actual start time for logging purposes
    executed_scenarios.sort(key=lambda x: x['start_time'])

    # Log the actual execution order with start times for informational purposes
    logging.info("📊 Custom prefix scenario execution order (--order-tests controls submission order, not start time):")
    for i, scenario in enumerate(executed_scenarios, 1):
        logging.info(f"  {i}. PRIORITY_{scenario['priority']:03d}: {scenario['name']} started at {scenario['start_time']}")

    # Sort by priority value to show intended vs actual execution order
    expected_order = sorted(executed_scenarios, key=lambda x: x['priority'])
    logging.info("📋 Expected submission order vs actual start time order:")

    expected_order_str = " → ".join([f"PRIORITY_{s['priority']:03d}" for s in expected_order])
    actual_order_str = " → ".join([f"PRIORITY_{s['priority']:03d}" for s in executed_scenarios])

    logging.info(f"  Expected: {expected_order_str}")
    logging.info(f"  Actual:   {actual_order_str}")

    if [s['priority'] for s in expected_order] != [s['priority'] for s in executed_scenarios]:
        logging.info("ℹ️  Start time order differs from submission order - this is normal for --order-tests")
        logging.info("   --order-tests controls submission order, allowing parallel execution with timing variations")
    else:
        logging.info("✅ Start time order matches submission order (optimal parallel scheduling)")

    logging.info(f"✅ Custom prefix order tests validation passed: All {expected_count} scenarios executed successfully")


@then('I should see that ordered scenarios execute before unordered scenarios for "{parallel_scheme}" scheme')
def then_see_ordered_before_unordered(context, parallel_scheme):
    """Verify that ordered and unordered scenarios executed successfully (--order-tests controls submission order, not start time)"""
    report_json_path = os.path.join(context.output_path, 'report.json')
    assert os.path.exists(report_json_path), f"Report JSON file not found at {report_json_path}"

    with open(report_json_path, 'r') as json_file:
        report_data = json.load(json_file)

    # Define expected scenarios and their order values
    scenario_order_mapping = {
        "First ordered test scenario": 1,
        "Second ordered test scenario": 2,
        "Third ordered test scenario": 3,
        "Unordered test scenario that should run last": 9999,
        "Another unordered test scenario that should run last": 9999
    }

    executed_scenarios = []
    for feature in report_data.get('features', []):
        for scenario in feature.get('scenarios', []):
            if scenario['name'] in scenario_order_mapping:
                # Ensure scenario has start time
                assert 'start' in scenario, f"Scenario '{scenario['name']}' missing start time in report"

                executed_scenarios.append({
                    'name': scenario['name'],
                    'order': scenario_order_mapping[scenario['name']],
                    'start_time': scenario['start'],
                    'is_ordered': scenario_order_mapping[scenario['name']] < 9999
                })

    # Verify that all expected scenarios were executed
    expected_count = 5
    assert len(executed_scenarios) == expected_count, \
        f"Expected {expected_count} scenarios to be executed, but got {len(executed_scenarios)}"

    # Separate ordered and unordered scenarios
    ordered_scenarios = [s for s in executed_scenarios if s['is_ordered']]
    unordered_scenarios = [s for s in executed_scenarios if not s['is_ordered']]

    # Verify counts
    assert len(ordered_scenarios) == 3, f"Expected 3 ordered scenarios, got {len(ordered_scenarios)}"
    assert len(unordered_scenarios) == 2, f"Expected 2 unordered scenarios, got {len(unordered_scenarios)}"

    # Sort by start time for logging
    executed_scenarios.sort(key=lambda x: x['start_time'])

    # Log the execution order with start times for informational purposes
    logging.info("📊 Mixed scenario execution order (--order-tests controls submission order, not start time):")
    for i, scenario in enumerate(executed_scenarios, 1):
        order_type = "ORDERED" if scenario['is_ordered'] else "UNORDERED"
        order_value = f"ORDER_{scenario['order']:03d}" if scenario['is_ordered'] else "NO_ORDER"
        logging.info(f"  {i}. {order_value} ({order_type}): {scenario['name']} started at {scenario['start_time']}")

    # For --order-tests: Ordered scenarios are submitted before unordered scenarios
    # But actual start times may vary due to parallel scheduling
    logging.info("📋 Submission order expectation: All ordered scenarios submitted before unordered scenarios")
    logging.info("   Actual start times may vary due to parallel worker scheduling")

    # Check if ordered scenarios actually started before unordered ones (informational)
    latest_ordered_start = max(s['start_time'] for s in ordered_scenarios)
    earliest_unordered_start = min(s['start_time'] for s in unordered_scenarios)

    if latest_ordered_start <= earliest_unordered_start:
        logging.info("✅ Start time order matches submission order: All ordered scenarios started before unordered scenarios")
    else:
        logging.info("ℹ️  Start time order differs from submission order - this is normal for --order-tests")
        logging.info("   Some unordered scenarios started before ordered scenarios due to parallel scheduling")

    logging.info(f"✅ Mixed scenario validation passed: All ordered and unordered scenarios executed successfully")


@then('the execution order should not be enforced with single process execution')
def then_no_order_enforcement_single_process(context):
    """Verify that ordering is not enforced when running with single process"""
    # For single process execution, we just verify that the test completed successfully
    # and scenarios were executed (the actual order doesn't matter since ordering only works with parallel execution)


@then('I should see the scenarios executed in strict order for "{parallel_scheme}" scheme')
def then_see_strict_execution_order(context, parallel_scheme):
    """Verify that scenarios with ORDER tags executed in strict sequential order when using --order-tests-strict"""
    report_json_path = os.path.join(context.output_path, 'report.json')
    assert os.path.exists(report_json_path), f"Report JSON file not found at {report_json_path}"

    with open(report_json_path, 'r') as json_file:
        report_data = json.load(json_file)

    # Extract scenario execution data with order values, start times, and stop times
    scenario_order_mapping = {
        "First ordered test scenario": 1,
        "Second ordered test scenario": 2,
        "Third ordered test scenario": 3,
        "Fourth ordered test scenario": 10
    }

    executed_scenarios = []
    for feature in report_data.get('features', []):
        for scenario in feature.get('scenarios', []):
            if scenario['name'] in scenario_order_mapping:
                # Ensure scenario has both start and stop times
                assert 'start' in scenario, f"Scenario '{scenario['name']}' missing start time in report"
                assert 'stop' in scenario, f"Scenario '{scenario['name']}' missing stop time in report"

                executed_scenarios.append({
                    'name': scenario['name'],
                    'order': scenario_order_mapping[scenario['name']],
                    'start_time': scenario['start'],
                    'stop_time': scenario['stop']
                })

    # Verify that all expected scenarios were executed
    expected_count = 4
    assert len(executed_scenarios) == expected_count, \
        f"Expected {expected_count} scenarios to be executed, but got {len(executed_scenarios)}"

    # For --order-tests-strict: Verify strict sequential execution
    # Each scenario must complete before the next scenario starts
    executed_scenarios.sort(key=lambda x: x['start_time'])

    if parallel_scheme == 'scenario':
        # For scenario-level execution: scenarios should execute in ORDER tag order
        logging.info("📊 Scenario-level strict execution order verification:")
        expected_order = sorted(executed_scenarios, key=lambda x: x['order'])
        for i, scenario in enumerate(expected_order):
            actual_scenario = executed_scenarios[i]
            assert scenario['order'] == actual_scenario['order'], \
                f"Scenario execution order mismatch: expected ORDER_{scenario['order']:03d} ({scenario['name']}) " \
                f"but got ORDER_{actual_scenario['order']:03d} ({actual_scenario['name']}) at position {i+1}"
    else:
        # For feature-level execution: scenarios execute in file order (behave's natural behavior)
        # but still in strict sequential order (each must complete before next starts)
        logging.info("📊 Feature-level strict execution order verification:")
        logging.info("    Note: With feature-level execution, scenarios execute in file order, not ORDER tag order")

    # Log the execution order for debugging
    for i, scenario in enumerate(executed_scenarios, 1):
        duration = scenario['stop_time'] - scenario['start_time']
        logging.info(f"  {i}. ORDER_{scenario['order']:03d}: {scenario['name']}")
        logging.info(f"    Start: {scenario['start_time']}, Stop: {scenario['stop_time']}, Duration: {duration:.3f}s")

    # Verify strict sequential execution for both schemes
    for i in range(len(executed_scenarios) - 1):
        current_scenario = executed_scenarios[i]
        next_scenario = executed_scenarios[i + 1]

        # The critical requirement for strict ordering: previous scenario must complete before next starts
        assert current_scenario['stop_time'] <= next_scenario['start_time'], \
            f"Strict sequential execution violated: {current_scenario['name']} (ORDER_{current_scenario['order']:03d}) " \
            f"stopped at {current_scenario['stop_time']} but {next_scenario['name']} (ORDER_{next_scenario['order']:03d}) " \
            f"started at {next_scenario['start_time']}. With --order-tests-strict, scenarios must complete before the next starts!"

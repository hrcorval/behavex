import json
import logging
import multiprocessing
import os
import signal
import sys
import time
import traceback

from behave.configuration import Configuration
from behave.runner import Runner

from behavex import host_messages
from behavex.behave_args import set_behave_arguments
from behavex.conf_mgr import ConfigRun, get_param
from behavex.environment import extend_behave_hooks
from behavex.execution_singleton import ExecutionSingleton
from behavex.global_vars import global_vars
from behavex.outputs.report_json import generate_execution_info, get_environment_details
from behavex.outputs.report_utils import text
from behavex.outputs.report_xml import processing_xml_feature
from behavex.run_state import state
from behavex.utils import get_text, join_feature_reports


def init_multiprocessing(idQueue, parallel_delay):
    try:
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        # Spawned worker processes (macOS/Windows default) do not inherit sys.path.
        # Re-add the project root so that local packages resolve inside workers.
        cwd = os.getcwd()
        if cwd not in sys.path:
            sys.path.insert(0, cwd)
        # Retrieve one of the unique IDs
        worker_id = idQueue.get()
        # Use the unique ID to name the process
        multiprocessing.current_process().name = f'behave_worker-{worker_id}'
        # Add an initial delay to avoid all processes starting at the same time
        if isinstance(parallel_delay, int) and parallel_delay > 0:
            time.sleep(parallel_delay * worker_id / 1000.0)
    except Exception as e:
        logging.error(f"Exception in init_multiprocessing: {e}")
        raise


def execute_tests(
        features_path,
        feature_filename,
        feature_json_skeleton,
        scenarios_to_run_in_feature,
        scenario_line,
        multiprocess,
        config,
        lock,
        shared_removed_scenarios,
        host_queue=None):
    """
    Execute tests for the given feature or scenario.

    Args:
        features_path (str): Path to the features.
        feature_filename (str): Name of the feature file.
        feature_json_skeleton (str): JSON skeleton of the feature.
        scenarios_to_run_in_feature (int): Number of scenarios to run in the feature.
        scenario_line (int): Line of the scenario.
        multiprocess (bool): Whether to use multiprocessing.
        config (ConfigRun): Configuration object.
        lock (Lock): Multiprocessing lock.
        shared_removed_scenarios (dict): Shared dictionary of removed scenarios.

    Returns:
        tuple: Execution code and JSON report.
    """
    try:
        behave_args = None
        if host_queue is not None:
            host_queue = host_messages.HostQueueDeferringCtrlC(host_queue)
        state.host_queue = host_queue
        stdout_before_host_queue = sys.stdout
        if host_queue is not None:
            sys.stdout = host_messages.StdoutToHostQueue(host_queue, stdout_before_host_queue)
            # init_multiprocessing ignores Ctrl+C in workers; behave needs it to stop with the scenarios that ran
            signal.signal(signal.SIGINT, host_messages.stop_behave_on_first_ctrl_c)
        if multiprocess or host_queue is not None:
            ExecutionSingleton._instances[ConfigRun] = config
        extend_behave_hooks()
        try:
            # Execution ID is only important for multiprocessing so that
            # we can influence where output files end up
            execution_id = json.loads(feature_json_skeleton or '{}').get('id')
            behave_args = set_behave_arguments(features_path=features_path,
                                                multiprocess=multiprocess,
                                                execution_id=execution_id,
                                                feature=feature_filename,
                                                scenario_line=scenario_line,
                                                config=config)
        except Exception as exception:
            traceback.print_exc()
            print(exception)
        execution_code, generate_report, json_results_str = _launch_behave(behave_args)
        # print("pipenv run behave {} --> Execution Code: {} --> Generate Report: {}".format(" ".join(behave_args), execution_code, generate_report))
        if generate_report:
            try:
                json_output = json.loads(json_results_str)
            except (json.JSONDecodeError, ValueError) as e:
                logging.error(f"Failed to parse JSON results from _launch_behave: {e}")
                logging.error(f"Raw JSON string: {json_results_str}")
                json_output = {'environment': [], 'features': [], 'steps_definition': []}
            # Keep behave's results whenever it produced any, as single-process runs do
            if execution_code == 2 and not json_output.get('features') and feature_json_skeleton:
                skeleton_feature = json.loads(feature_json_skeleton)
                skeleton_feature['status'] = 'failed'
                if scenario_line:
                    for skeleton_scenario in skeleton_feature["scenarios"]:
                        if str(skeleton_scenario['line']) == str(scenario_line):
                            skeleton_scenario['status'] = 'failed'
                            skeleton_scenario['error_msg'] = get_text('scenario.execution_crashed')
                else:
                    skeleton_feature['error_msg'] = 'Execution crashed. No outputs could be generated.'
                    for skeleton_scenario in skeleton_feature["scenarios"]:
                        skeleton_scenario['status'] = 'failed'
                        skeleton_scenario['error_msg'] = get_text('feature.execution_crashed')
                json_output = {'environment': [], 'features': [skeleton_feature], 'steps_definition': []}
            if scenario_line:
                json_output['features'] = filter_feature_executed(json_output,
                                                                  text(feature_filename),
                                                                  scenario_line=scenario_line)
                if len(json_output['features']) == 0 or len(json_output['features'][0]['scenarios']) == 0:
                    # Adding scenario data if the test was removed from the execution (setting it as "Untested")
                    json_output['features'] = [json.loads(feature_json_skeleton)]
                try:
                    processing_xml_feature(json_output=json_output,
                                           scenario_line=scenario_line,
                                           feature_filename=feature_filename,
                                           scenarios_to_run_in_feature=scenarios_to_run_in_feature,
                                           lock=lock,
                                           shared_removed_scenarios=shared_removed_scenarios)
                except Exception as ex:
                    logging.exception("There was a problem processing the xml file: {}".format(ex))
        else:
            json_output = {'environment': [], 'features': [], 'steps_definition': []}
        return execution_code, join_feature_reports(json_output)
    except Exception as e:
        logging.error(f"Exception in execute_tests: {e}")
        raise
    finally:
        if host_queue is not None:
            sys.stdout.flush()
            sys.stdout = stdout_before_host_queue


def filter_feature_executed(json_output, filename, scenario_line):
    """
    Filter the executed feature from the JSON output.

    Args:
        json_output (dict): JSON output of the test execution.
        filename (str): Name of the feature file.
        scenario_line (str): Line of the scenario.
    """
    for feature in json_output.get('features', '')[:]:
        if feature.get('filename', '') == filename:
            mapping_scenarios = []
            for scenario in feature['scenarios']:
                if str(scenario['line']) == str(scenario_line):
                    mapping_scenarios.append(scenario)
            feature['scenarios'] = mapping_scenarios
            return [feature]
    return []


def _calculate_execution_code_from_runner(runner):
    """
    Calculate execution code based on Runner properties.

    This uses the efficient runner.context.failed boolean and runner.hook_failures
    instead of iterating through features/scenarios or parsing output text.

    Args:
        runner: The Runner instance after execution

    Returns:
        int: Execution code (0=success, 1=test failures, 2=errors)
    """
    try:
        # Special handling for dry runs - they should always return 0 unless aborted
        if get_param('dry_run'):
            # Only return error if explicitly aborted, otherwise dry runs are always successful
            if hasattr(runner, 'aborted') and runner.aborted:
                return 2  # Aborted execution
            return 0  # Dry runs are successful by definition (they don't actually run tests)

        # Check if runner was aborted first
        if hasattr(runner, 'aborted') and runner.aborted:
            return 2  # Aborted execution

        # Check for hook failures using runner.hook_failures (more reliable than text parsing)
        if hasattr(runner, 'hook_failures') and runner.hook_failures > 0:
            return 2  # Hook failures

        # Use context.failed boolean to determine if any tests failed
        if hasattr(runner, 'context') and runner.context:
            # A failing cleanup leaves context.failed unset; outside a scenario it fails none, so it cannot be muted
            if vars(runner.context).get('_unmutable_cleanup_failed'):
                return 2
            if vars(runner.context).get('_scenario_cleanup_failed'):
                return 1  # Scenario cleanup failures
            if hasattr(runner.context, 'failed'):
                if runner.context.failed:
                    return 1  # Test failures
                else:
                    return 0  # Success - all tests passed

        # Fallback if context or failed attribute not available
        return 0  # Assume success

    except Exception as ex:

        logging.warning(f"Error calculating execution code from runner: {ex}")
        return 1  # Default to failure on error


def _launch_behave(behave_args):
    """
    Launch Behave with the given arguments.

    Args:
        behave_args (list): List of arguments for Behave.

    Returns:
        tuple: Execution code, whether to generate a report, and JSON string of execution results.
    """
    generate_report = True
    execution_code = 0
    json_results_str = '{"environment": [], "features": [], "steps_definition": {}}'

    try:
        if behave_args is None:
            # Handle case where behave_args is None (e.g., argument parsing failed)
            logging.error("behave_args is None - argument parsing may have failed")
            execution_code = 2
            generate_report = True
            return execution_code, generate_report, json_results_str

        # Note: stdout_file logic removed since we get execution results directly from runner

        # Run behave using Runner class instead of behave_script.main()
        try:
            # Create configuration from command-line arguments
            config = Configuration(command_args=behave_args)

            # Ensure format is set (fallback to pretty if not specified via arguments)
            if not config.format:
                config.format = ['pretty']

            # Create runner instance
            runner = Runner(config)

            # Ensure line-buffered stdout so formatter output appears in real time on all
            # platforms (Linux/Windows block-buffer stdout when not a TTY by default)
            if 'null' not in (config.format or []) and hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(line_buffering=True)

            runner.run()

            # Calculate execution code using runner internal state
            execution_code = _calculate_execution_code_from_runner(runner)

            # Extract results directly from runner and serialize to JSON string
            try:
                # Check if runner has features and they contain data
                if runner and hasattr(runner, 'features') and runner.features:
                    feature_list = generate_execution_info(runner.features)
                    # A before_all failure aborts the run before any feature runs, leaving them 'untested';
                    # an interrupted run also aborts, but after some features ran
                    if (getattr(runner, 'aborted', False) and getattr(runner, 'hook_failures', 0) > 0
                            and all(feature_info['status'] in ('untested', 'skipped') for feature_info in feature_list)):
                        for feature_info in feature_list:
                            if feature_info['status'] == 'untested':
                                feature_info['status'] = 'error'
                    json_results = {
                        'environment': get_environment_details(),
                        'features': feature_list,
                        'steps_definition': global_vars.steps_definitions,
                    }
                    json_results_str = json.dumps(json_results)
                else:
                    # Fallback for cases where runner doesn't have features or features is empty
                    # This is common in behave 1.2.6 during dry runs
                    if get_param('dry_run'):
                        logging.info("Dry run mode: runner.features empty, this is expected in behave 1.2.6")
                    else:
                        logging.warning("Runner doesn't have features attribute or features is empty, using empty results")

                    json_results = {
                        'environment': get_environment_details(),
                        'features': [],
                        'steps_definition': global_vars.steps_definitions,
                    }
                    json_results_str = json.dumps(json_results)
            except Exception as json_ex:
                # Robust fallback for any JSON serialization issues
                logging.error(f"Error processing runner results: {json_ex}")
                json_results_str = json.dumps({
                    'environment': [],
                    'features': [],
                    'steps_definition': {}
                })

            # Note: stdout file existence check removed since we get execution status directly from runner
        except SystemExit as system_exit:
            # Handle SystemExit from crashing tests (e.g., exit() calls)
            # SystemExit from crashing tests should be treated as crash/interruption (code 2)
            # This ensures execution_interrupted_or_crashed = True in final exit code calculation
            execution_code = 2
            generate_report = True

            logging.info(f'SystemExit caught from crashing test (original code: {system_exit.code}), treating as crash (code 2)')
        except Exception as runner_ex:
            # Handle runner exception
            # Log the runner exception
            logging.exception('Error using Runner class, details: ')
            logging.exception(runner_ex)

            # Set appropriate execution code
            execution_code = 1
            generate_report = True
    except KeyboardInterrupt:
        execution_code = 1
        generate_report = False
    except Exception as ex:
        execution_code = 1
        generate_report = True
        logging.exception('Unexpected error executing behave steps: ')
        logging.exception(ex)
        traceback.print_exc()
    except:
        execution_code = 2
        generate_report = True

    # Note: stdout file merging removed since we get execution results directly from runner
    return execution_code, generate_report, json_results_str

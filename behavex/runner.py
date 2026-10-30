# -*- coding: utf-8 -*-

"""BehaveX - Production-grade test orchestration for Python BDD..

This module provides the main entry point for running BehaveX tests,
including setup, execution, and reporting.
"""

# pylint: disable=W0703

# __future__ has been added to maintain compatibility
from __future__ import absolute_import, print_function

# Standard library imports
import json
import logging
import multiprocessing
import os
import os.path
import platform
import sys
import time
import uuid
from tempfile import gettempdir
from typing import Optional

# Third-party imports
from behave.model import ScenarioOutline
from behave.runner import ConfigError

# Local imports
# noinspection PyUnresolvedReferences
import importlib.util

from behavex import conf_mgr
from behavex.arguments import BEHAVEX_ARGS, parse_arguments
from behavex.behave_args import as_non_option, behave_runner_after_setup_paths, single_behave_run_paths
from behavex.conf_mgr import ConfigRun, get_env, get_param
from behavex.context import BehaveXContext
from behavex.execution_singleton import ExecutionSingleton
from behavex.global_vars import global_vars
from behavex.dispatch import (launch_by_feature, launch_by_scenario, run_in_one_behave_process,
                              shut_down_worker_pool, shut_down_worker_pool_after_ctrl_c, start_worker_pool)
from behavex.outputs.formatter_manager import (DEFAULT_FORMATTER_DIR,
                                               FormatterManager)
from behavex.outputs.report_utils import (get_overall_status,
                                          match_for_execution,
                                          pretty_print_time)
from behavex.outputs.report_xml import get_feature_results_tmp_file_path
from behavex.run_state import state
from behavex.step_definition_lookup import find_undefined_step_texts
from behavex.utils import (IncludeNameMatch, IncludePathsMatch, MatchInclude,
                           cleanup_folders, configure_logging,
                           copy_bootstrap_html_generator,
                           expand_paths, explore_features, generate_reports,
                           get_feature_and_scenario_line, get_json_results, get_logging_level,
                           get_name_filters,
                           get_scenario_tags,
                           get_scenarios_instances, join_feature_reports, join_scenario_reports,
                           print_env_variables, print_parallel,
                           set_behave_tags, set_env_variable,
                           set_environ_config, set_system_paths)

EXIT_OK = 0
EXIT_ERROR = 1
ERROR_OR_UNDEFINED_STATUSES = ('error', 'undefined')

os.environ.setdefault('EXECUTION_CODE', '1')
match_include = None

_features_path_before_first_run: Optional[str] = None


include_path_match = None
include_name_match = None


def main():
    """BehaveX starting point.

    Parses command-line arguments and initiates the test run.
    """
    args = sys.argv[1:]
    exit_code = 1  # Default to error
    try:
        exit_code = run(args)
    except SystemExit as e:
        # Handle cases where scenarios call exit() directly
        # A str code is a reason already printed, as utils.expand_paths does
        exit_code = e.code if isinstance(e.code, int) else 1
        # Ensure we print the exit code even when scenarios crash
        print('Exit code: {}'.format(exit_code))
    except Exception as e:
        # Handle unexpected exceptions
        print(f'Unexpected error: {e}')
        exit_code = 1
        print('Exit code: {}'.format(exit_code))

    try:
        exit(exit_code)
    except:
        # force exit
        sys.exit(exit_code)

def run(args):
    """Run BehaveX with the given arguments.

    Args:
        args (list): Command-line arguments.

    Returns:
        int: Exit code indicating success or failure.
    """
    state.run_id = str(uuid.uuid4())
    args_parsed = _prepare_run(args)
    if args_parsed is None:
        return EXIT_ERROR
    set_system_paths()
    if get_param('no_report'):
        os.makedirs(get_env('TEMP'), exist_ok=True)
    else:
        cleanup_folders()
        copy_bootstrap_html_generator()
    if state.run_active:
        # A BehaveXRunner host keeps its logging configuration; the workers log per scenario
        os.makedirs(get_env('logs'), exist_ok=True)
    else:
        configure_logging(args_parsed)
    return launch_behavex()


def discover(args, check_steps=False):
    """Return (scenario, undefined step texts) for each scenario run(args) would execute, without
    running anything or writing files. Returns None when run(args) would stop on its rerun_failures file.
    """
    if _prepare_run(args) is None:
        return None
    set_behave_tags(write_tags_file=False)
    features = _explore_scenarios(os.environ['FEATURES_PATH'])
    scenarios = [scenario for _, scenario, _ in _select_scenarios(features)]
    if not check_steps:
        return [(scenario, []) for scenario in scenarios]
    return list(zip(scenarios, find_undefined_step_texts(features, scenarios)))


def _prepare_run(args):
    """Set the run's process state (config, env vars, filters) without writing to the filesystem.

    Returns the parsed arguments, or None when the rerun_failures file is missing or empty.
    """
    global match_include
    global include_path_match
    global include_name_match
    global _features_path_before_first_run
    global _bhx_user_environment_module
    # Singletons, env vars and global_vars from a previous in-process run would leak into this one
    for singleton_class in (ConfigRun, MatchInclude, IncludePathsMatch, IncludeNameMatch):
        ExecutionSingleton._instances.pop(singleton_class, None)
    if _features_path_before_first_run is None:
        _features_path_before_first_run = os.environ.get('FEATURES_PATH', '')
    os.environ['FEATURES_PATH'] = _features_path_before_first_run
    for env_var in ('RERUN_FAILURES', 'BHX_SHARED_CONTEXT'):
        os.environ.pop(env_var, None)
    global_vars.__init__()
    _bhx_user_environment_module = None
    args_parsed = parse_arguments(args)
    set_environ_config(args_parsed)
    ConfigRun().set_args(args_parsed)
    execution_code, rerun_list = setup_running_failures(args_parsed)
    if execution_code == EXIT_ERROR:
        return None
    if rerun_list:
        paths = ",".join(rerun_list).replace('\n', '')
        os.environ['FEATURES_PATH'] = paths
        global_vars.rerun_failures = True
    else:
        # Handle paths parameter
        if len(get_param('paths')) > 0:
            paths = ",".join(expand_paths(get_param('paths'))).replace('\n', '')
            os.environ['FEATURES_PATH'] = paths

        # Handle include_paths parameter
        if len(get_param('include_paths')) > 0:
            include_paths = ",".join(expand_paths(get_param('include_paths'))).replace('\n', '')
            features_path = os.environ.get('FEATURES_PATH', '')
            if features_path == '' or not os.path.exists(features_path):
                os.environ['FEATURES_PATH'] = include_paths
            else:
                os.environ['FEATURES_PATH'] = features_path + ',' + include_paths
    features_path = os.environ.get('FEATURES_PATH')
    if features_path == '' or features_path is None:
        os.environ['FEATURES_PATH'] = 'features'
    for features_path_entry in os.environ['FEATURES_PATH'].split(','):
        pure_feature_path = get_feature_and_scenario_line(features_path_entry)[0]
        if not os.path.exists(pure_feature_path):
            message = 'Specified path was not found: {}'.format(pure_feature_path)
            print('\n' + message)
            sys.exit(message)
    _set_env_variables(args_parsed)
    match_include = MatchInclude()
    include_path_match = IncludePathsMatch()
    include_name_match = IncludeNameMatch()
    return args_parsed


def setup_running_failures(args_parsed):
    """Setup the environment for rerunning failed tests.

    Args:
        args_parsed (Namespace): Parsed command-line arguments.

    Returns:
        tuple: Exit code and list of paths to rerun.
    """
    failures_path = args_parsed.rerun_failures
    if failures_path:
        failures_path = os.path.normpath(failures_path)
        if not os.path.isabs(failures_path):
            failures_path = os.path.abspath(failures_path)
        if os.path.exists(failures_path):
            set_env_variable('RERUN_FAILURES', args_parsed.rerun_failures)
            with open(failures_path, 'r') as failures_file:
                content = failures_file.read()
                if not content.strip():
                    print('\nThere are no failing test scenarios to run.')
                    return EXIT_ERROR, None
                return EXIT_OK, content.split(",")
        else:
            print('\nThe specified failing scenarios filename was not found: {}'.format(failures_path))
            return EXIT_ERROR, None
    else:
        return EXIT_OK, None


def launch_behavex():
    """Launch the BehaveX test execution in the specified parallel mode.

    Returns:
        int: Exit code indicating success or failure.
    """
    json_reports = []
    execution_codes = []
    results = None
    features_path = os.environ.get('FEATURES_PATH', '')
    parallel_scheme = get_param('parallel_scheme')
    if get_param('dry_run'):
        parallel_processes = 1
        show_progress_bar = False
    else:
        parallel_processes = get_param('parallel_processes')
        parallel_processes = 1 if parallel_processes <= 1 else parallel_processes
        show_progress_bar = get_param('show_progress_bar')
    state.is_parallel_run = (
        True
        if parallel_processes > 1 and not get_param('dry_run')
        else False
    )
    if state.is_parallel_run:
        _warn_parallel_incompatible_params()
    set_behave_tags()
    bhx_context = BehaveXContext()
    # environment.py is loaded before Behave's PathManager is active, so CWD may
    # not be in sys.path yet.  Add it early so local imports in environment.py work.
    cwd = os.getcwd()
    if cwd not in sys.path:
        sys.path.insert(0, cwd)
    # behave skips every hook on a dry run, so the worker hooks follow suit
    run_worker_hooks = not get_param('dry_run')
    if run_worker_hooks and not _call_bhx_hook('before_all_workers', bhx_context):
        _call_bhx_hook('after_all_workers', bhx_context)
        _write_overall_status('failed', EXIT_ERROR)
        print('Exit code: {}'.format(EXIT_ERROR))
        return EXIT_ERROR
    shared_data = bhx_context._to_dict()
    if shared_data:
        os.environ['BHX_SHARED_CONTEXT'] = json.dumps(shared_data)
    scenario = False
    notify_missing_features(features_path)
    updated_features_list = _explore_scenarios(features_path)
    parallel_scheme = '' if not state.is_parallel_run else parallel_scheme
    manager = multiprocessing.Manager()
    # shared variable to track scenarios that should be run but seems to be removed from execution (using scenarios.remove)
    shared_removed_scenarios = manager.dict()
    lock = manager.Lock()
    start_worker_pool(manager, parallel_processes)
    global_vars.execution_start_time = time.time()
    totals = {"features": {"passed": 0, "failed": 0, "error": 0, "skipped": 0, "untested": 0},
              "scenarios": {"passed": 0, "failed": 0, "error": 0, "skipped": 0, "untested": 0}}
    failures = []  # Initialize before try block to ensure it's always defined
    merged_json = None
    # a single behave process prints its own summary, but none runs when nothing matched
    print_summary = state.is_parallel_run
    try:
        config = ConfigRun()
        all_paths = single_behave_run_paths(features_path, updated_features_list)
        if all_paths is not None:
            # Executing without parallel processes
            if get_param('dry_run'):
                print('Obtaining information about the reporting scope...')
            if len(all_paths) > 0:
                execute_tests_kwargs = dict(features_path=all_paths,
                                            feature_filename=None,
                                            feature_json_skeleton=None,
                                            scenarios_to_run_in_feature=None,
                                            scenario_line=None,
                                            multiprocess=False,
                                            config=config,
                                            lock=None,
                                            shared_removed_scenarios=None)
                execution_codes, json_reports = run_in_one_behave_process(execute_tests_kwargs, manager)
            else:
                execution_codes, json_reports = (0, [{'environment': [], 'features': [], 'steps_definition': []}])
                print_summary = not get_param('dry_run')
        elif parallel_scheme == 'scenario':
            execution_codes, json_reports = launch_by_scenario(_select_scenarios(updated_features_list),
                                                            lock,
                                                            shared_removed_scenarios,
                                                            show_progress_bar)
            scenario = True
        elif parallel_scheme == 'feature':
            execution_codes, json_reports = launch_by_feature(updated_features_list,
                                                            lock,
                                                            show_progress_bar)
        merged_json = shut_down_worker_pool_and_write_merged_report(
            json_reports, scenario)

        if get_param('dry_run'):
            print_parallel('execution.dry_run.completed', get_env('OUTPUT'))

        remove_temporary_files(parallel_processes, json_reports)

        failing_non_muted_tests = False
        # TODO: Replace logs below with test execution logs when an unexpected error occurs
        # behave_log_file = os.path.join(output_folder, 'behavex', 'logs', str(scenario['id_feature']), 'behave.log')
        # behave_log_file = os.path.join(output_folder, 'behavex', 'logs', str(json_test_configuration['id']), 'behave.log')
        results = merged_json if get_param('no_report') else get_json_results()
        if results:
            for feature in results['features']:
                filename = feature['filename']
                if feature['status'] == 'failed':
                    totals['features']['failed'] += 1
                elif feature['status'] in ERROR_OR_UNDEFINED_STATUSES:
                    totals['features']['error'] += 1
                elif feature['status'] == 'passed':
                    totals['features']['passed'] += 1
                elif feature['status'] == 'untested':
                    totals['features']['untested'] += 1
                else:
                    totals['features']['skipped'] += 1
                    totals['scenarios']['skipped'] += len(feature['scenarios'])
                    continue
                for scenario in feature['scenarios']:
                    if scenario['status'] == 'failed' or scenario['status'] in ERROR_OR_UNDEFINED_STATUSES:
                        totals['scenarios']['failed'] += 1
                        failures.append('{}:{}'.format(filename, scenario['line']))
                        if 'MUTE' not in scenario['tags']:
                            failing_non_muted_tests = True
                    elif scenario['status'] == 'passed':
                        totals['scenarios']['passed'] += 1
                    elif scenario['status'] == 'untested':
                        totals['scenarios']['untested'] += 1
                    else:
                        totals['scenarios']['skipped'] += 1
            if failures and not get_param('no_report'):
                failures_file_path = os.path.join(get_env('OUTPUT'), global_vars.report_filenames['report_failures'])
                with open(failures_file_path, 'w') as failures_file:
                    failures_file.write(','.join(failures))
        # Calculates final exit code. execution_codes is 2 if an execution exception arises
        if isinstance(execution_codes, list):
            execution_failed = True if sum(execution_codes) > 0 else False
            execution_interrupted_or_crashed = True if any([code == 2 for code in execution_codes]) else False
        else:
            execution_failed = True if execution_codes > 0 else False
            execution_interrupted_or_crashed = True if execution_codes == 2 else False
        # Treat as error when execution failed but no scenario actually ran (e.g. ImportError during step loading)
        no_scenarios_ran = (
            totals['scenarios']['passed'] == 0
            and totals['scenarios']['failed'] == 0
            and totals['scenarios']['error'] == 0
        )
        exit_code = (EXIT_ERROR if (execution_failed and (failing_non_muted_tests or no_scenarios_ran)) or execution_interrupted_or_crashed else EXIT_OK)
    except KeyboardInterrupt:
        shut_down_worker_pool_after_ctrl_c(manager)
        exit_code = EXIT_ERROR
    finally:
        state.active_executor = None
        state.last_run_results = merged_json.get('features', []) if isinstance(merged_json, dict) else []
        if not state.is_parallel_run:
            state.fire_report_progress({'features': state.last_run_results}, state.progress_reported)
        state.is_parallel_run = False
        if run_worker_hooks and not _call_bhx_hook('after_all_workers', bhx_context):
            exit_code = EXIT_ERROR
    _write_overall_status('failed' if exit_code == EXIT_ERROR else get_overall_status(merged_json), exit_code)
    if print_summary:
        print_execution_summary(totals, failures, results)  # failures initialized above
    if results and results['features'] and not get_param('formatter') and not get_param('no_report'):
        print('\nHTML output report is located at: {}'.format(os.path.join(get_env('OUTPUT'), "report.html")))
    if get_param('no_report'):
        print('\nTemporary assets (logs, evidence, images) are located at: {}'.format(get_env('LOGS')))
    print('Exit code: {}'.format(exit_code))
    return exit_code


def print_execution_summary(totals, failures, results):
    """Print execution summary including failing scenarios and count totals.

    Args:
        totals (dict): Dictionary containing execution totals by type
        failures (list): List of failing scenario identifiers
        results (dict): Full results dictionary with feature/scenario details
    """
    untested_features = totals['features']['untested']
    untested_scenarios = totals['scenarios']['untested']
    error_features = totals['features']['error']
    error_scenarios = totals['scenarios']['error']

    untested_features_msg = ', {} untested'.format(untested_features) if untested_features > 0 else ''
    untested_scenarios_msg = ', {} untested'.format(untested_scenarios) if untested_scenarios > 0 else ''
    error_features_msg = ', {} error'.format(error_features) if error_features > 0 else ''
    error_scenarios_msg = ', {} error'.format(error_scenarios) if error_scenarios > 0 else ''

    # Print failing scenarios before summary (same format as behave single execution)
    if failures and results:
        # Collect failed and errored scenarios with their details
        failed_scenarios = []
        errored_scenarios = []

        # Group failures by status type
        for feature in results['features']:
            filename = feature['filename']
            for scenario in feature['scenarios']:
                scenario_key = f"{filename}:{scenario['line']}"
                if scenario_key in failures:
                    scenario_line = f"  {filename}:{scenario['line']}  {scenario['name']}"
                    if scenario['status'] == 'failed':
                        failed_scenarios.append(scenario_line)
                    elif scenario['status'] in ERROR_OR_UNDEFINED_STATUSES:
                        errored_scenarios.append(scenario_line)

        # Print errored scenarios first (if any)
        if errored_scenarios:
            print("\nErrored scenarios:")
            for scenario_line in errored_scenarios:
                print(scenario_line)

        # Print failed scenarios (if any)
        if failed_scenarios:
            print("\nFailing scenarios:")
            for scenario_line in failed_scenarios:
                print(scenario_line)

        print()  # Empty line before summary

    def plural_char(n): return 's' if n != 1 else ''
    print('\n{} feature{} passed, {} failed{}, {} skipped{}'.format(totals['features']['passed'],
                                                                      plural_char(totals['features']['passed']),
                                                                      totals['features']['failed'],
                                                                      error_features_msg,
                                                                      totals['features']['skipped'],
                                                                      untested_features_msg))
    print('{} scenario{} passed, {} failed{}, {} skipped{}'.format(totals['scenarios']['passed'],
                                                                    plural_char(totals['scenarios']['passed']),
                                                                    totals['scenarios']['failed'],
                                                                    error_scenarios_msg,
                                                                    totals['scenarios']['skipped'],
                                                                    untested_scenarios_msg))
    # Calculate steps summary
    steps_totals = {"passed": 0, "failed": 0, "error": 0, "skipped": 0, "untested": 0, "undefined": 0}
    if results and results['features']:
        for feature in results['features']:
            for scenario in feature['scenarios']:
                for step in scenario.get('steps', []):
                    step_status = step.get('status', 'skipped')
                    if step_status == 'undefined':
                        steps_totals['undefined'] += 1
                    elif step_status in steps_totals:
                        steps_totals[step_status] += 1
                    else:
                        steps_totals['skipped'] += 1

    untested_steps_msg = ', {} untested'.format(steps_totals['untested']) if steps_totals['untested'] > 0 else ''
    undefined_steps_msg = ', {} undefined'.format(steps_totals['undefined']) if steps_totals['undefined'] > 0 else ''
    error_steps_msg = ', {} error'.format(steps_totals['error']) if steps_totals['error'] > 0 else ''
    print('{} steps passed, {} failed{}, {} skipped{}{}'.format(steps_totals['passed'],
                                                                steps_totals['failed'],
                                                                error_steps_msg,
                                                                steps_totals['skipped'],
                                                                untested_steps_msg,
                                                                undefined_steps_msg))
    print('Took: {}'.format(pretty_print_time(global_vars.execution_end_time - global_vars.execution_start_time)))


def notify_missing_features(features_path):
    """Notify if any features are missing in the specified path.

    Args:
        features_path (str): Path to the features.
    """
    if global_vars.rerun_failures:
        all_paths = features_path.split(",")
        for path in all_paths:
            include_path = path.partition(':')[0]
            if not os.path.exists(os.path.normpath(include_path)):
                print_parallel('path.not_found', os.path.realpath(include_path))


def _explore_scenarios(features_path):
    features_list = {}
    for path in features_path.split(','):
        features_list[path] = explore_features(path)
    return create_scenario_line_references(features_list)


def create_scenario_line_references(features):
    """Create references for scenario lines in the features.

    Args:
        features (dict): Dictionary of features and their scenarios.

    Returns:
        dict: Updated features with scenario line references.
    """
    updated_features = {}
    for feature_path, scenarios in features.items():
        for scenario in scenarios:
            if global_vars.rerun_failures or ".feature:" in feature_path:
                if feature_path not in updated_features:
                    updated_features[feature_path] = []
                if isinstance(scenario, ScenarioOutline):
                    for scenario_outline_instance in scenario.scenarios:
                        outline_scenario_line = get_feature_and_scenario_line(scenario_outline_instance.name)[1]
                        if outline_scenario_line and scenario_outline_instance.line == int(outline_scenario_line):
                            if scenario_outline_instance not in updated_features[feature_path]:
                                updated_features[feature_path].append(scenario_outline_instance)
                            break
                else:
                    scenario_line = get_feature_and_scenario_line(feature_path)[1]
                    if scenario_line and scenario.line == int(scenario_line):
                        if scenario not in updated_features[feature_path]:
                            updated_features[feature_path].append(scenario)
            else:
                updated_features_path = scenario.feature.filename
                if updated_features_path not in updated_features:
                    updated_features[updated_features_path] = []
                if isinstance(scenario, ScenarioOutline):
                    for scenario_outline_instance in scenario.scenarios:
                        if scenario_outline_instance not in updated_features[updated_features_path]:
                            updated_features[updated_features_path].append(scenario_outline_instance)
                else:
                    if scenario not in updated_features[updated_features_path]:
                        updated_features[updated_features_path].append(scenario)
    return updated_features


def _select_scenarios(features):
    """Yield (features_path, scenario, scenario_tags) for each scenario the run executes."""
    for features_path, scenarios in features.items():
        for scenario in get_scenarios_instances(scenarios):
            if include_path_match(scenario.filename, scenario.line) and include_name_match(scenario.name):
                scenario_tags = get_scenario_tags(scenario)
                if match_for_execution(scenario_tags):
                    yield features_path, scenario, scenario_tags


def shut_down_worker_pool_and_write_merged_report(json_reports, scenario=False):
    merged_json = None
    output = os.path.join(get_env('OUTPUT'))
    shut_down_worker_pool()
    if type(json_reports) is list:
        if scenario:
            json_reports = join_scenario_reports(json_reports)
        merged_json = join_feature_reports(json_reports)
    else:
        merged_json = json_reports
    if global_vars.progress_bar_instance:
        global_vars.progress_bar_instance.finish()
    if not get_param('no_report'):
        path_info = os.path.join(output, global_vars.report_filenames['report_json'])
        with open(path_info, 'w') as file_info:
            file_info.write(json.dumps(merged_json))
        generate_reports(merged_json)
    return merged_json


def remove_temporary_files(parallel_processes, json_reports):
    """
    Remove temporary files created during the test execution.

    Args:
        parallel_processes (int): Number of parallel processes.
        json_reports (list): List of JSON reports.
    """
    path_info = os.path.join(
        os.path.join(get_env('OUTPUT'), global_vars.report_filenames['report_json'])
    )
    if os.path.exists(path_info):
        with open(path_info, 'r') as json_file:
            results_json = json.load(json_file)
            if 'features' and results_json['features']:
                return

    for i in range(parallel_processes):
        result_temp = os.path.join(gettempdir(), 'result{}.tmp'.format(i + 1))
        if os.path.exists(result_temp):
            try:
                os.remove(result_temp)
            except Exception as remove_ex:
                print(remove_ex)
        # Note: stdout file cleanup removed since we no longer generate these files

    # Note: stdout file cleanup removed since we no longer generate these files
    if not state.run_active:
        logger = logging.getLogger()
        logger.propagate = False
        for handler in logging.root.handlers:
            logger.removeHandler(handler)
        for handler in logger.handlers:
            logger.removeHandler(handler)
        logging._handlers = []
        console_log = logging.StreamHandler(sys.stdout)
        console_log.setLevel(get_logging_level())
        logger.addHandler(console_log)
    # removing any pending temporary files
    if type(json_reports) is not list:
        json_reports = [json_reports]
    for json_report in json_reports:
        if 'features' in json_report and json_report['features']:
            feature_tmp_file_path = get_feature_results_tmp_file_path(json_report['features'][0]['filename'])
            if os.path.exists(feature_tmp_file_path):
                try:
                    os.remove(feature_tmp_file_path)
                except Exception as remove_ex:
                    print(remove_ex)


def _write_overall_status(overall_status, exit_code):
    if get_param('no_report'):
        return
    status_path = os.path.join(get_env('OUTPUT'), global_vars.report_filenames['report_overall'])
    with open(status_path, 'w') as status_file:
        status_file.write(json.dumps({'status': overall_status, 'exit_code': exit_code,
                                      'stopped': state.stopped, 'run_id': state.run_id}))


def _find_user_environment_path() -> Optional[str]:
    """Return the environment.py behave loads for FEATURES_PATH, or None if there is none."""
    paths = [as_non_option(path.strip()) for path in os.environ.get('FEATURES_PATH', '').split(',') if path.strip()]
    try:
        behave_runner = behave_runner_after_setup_paths(paths)
    except ConfigError:
        return None
    env_file = os.path.join(behave_runner.base_dir, behave_runner.config.environment_file)
    return env_file if os.path.isfile(env_file) else None


_bhx_user_environment_module = None


def _call_bhx_hook(hook_name: str, *args) -> bool:
    """Load the user's environment.py (cached) and call hook_name if defined.

    Returns False when the hook raised, after reporting it the way behave reports a HOOK-ERROR.
    """
    global _bhx_user_environment_module
    if _bhx_user_environment_module is None:
        env_path = _find_user_environment_path()
        if not env_path:
            return True
        spec = importlib.util.spec_from_file_location('bhx_user_environment', env_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _bhx_user_environment_module = module
    hook_fn = getattr(_bhx_user_environment_module, hook_name, None)
    if not callable(hook_fn):
        return True
    try:
        hook_fn(*args)
    except Exception as ex:
        print(f'HOOK-ERROR in {hook_name}: {type(ex).__name__}: {ex}')
        return False
    return True


def _set_env_variables(args):
    """
    Set environment variables based on the given arguments.

    Args:
        args (Namespace): Parsed command-line arguments.
    """
    output_folder = os.path.normpath(get_env('output'))
    if os.path.isabs(output_folder):
        set_env_variable('OUTPUT', output_folder)
    else:
        set_env_variable('OUTPUT', os.path.abspath(output_folder))
    _store_tags_to_env_variable(get_param('tags'))
    if get_param('include_paths'):
        set_env_variable('INCLUDE_PATHS', get_param('include_paths'))
    if get_param('include'):
        set_env_variable('INCLUDE', get_param('include'))
    if get_param('name'):
        set_env_variable('NAME', '|'.join(get_name_filters()))
    if get_param('formatter'):
        formatter_outdir = get_param('formatter_outdir', '')
        formatter_spec = get_param('formatter')

        # If no formatter output directory is specified, use the default
        if not formatter_outdir:
            formatter_outdir = DEFAULT_FORMATTER_DIR

        # Special handling for custom formatters with default settings
        if formatter_outdir == DEFAULT_FORMATTER_DIR and formatter_spec:
            # Try to dynamically get the formatter's preferred output directory
            custom_formatter_dir = FormatterManager.get_formatter_output_dir(formatter_spec)
            if custom_formatter_dir:
                # Use the formatter's preferred directory to maintain consistency
                set_env_variable('LOGS', os.path.join(get_env('output'), custom_formatter_dir))
            else:
                # Fallback to default formatter directory
                set_env_variable('LOGS', os.path.join(get_env('output'), formatter_outdir))
        else:
            set_env_variable('LOGS', os.path.join(get_env('output'), formatter_outdir))
    else:
        set_env_variable('LOGS', os.path.join(get_env('output'), 'outputs', 'logs'))
    for arg in BEHAVEX_ARGS[4:]:
        set_env_variable(arg.upper(), get_param(arg))

    set_env_variable('TEMP', os.path.join(get_env('output'), 'temp'))
    if get_param('no_report'):
        set_env_variable('NO_REPORT', True)
        set_env_variable('LOGS', os.path.join(gettempdir(), 'bhx_logs'))
        set_env_variable('TEMP', os.path.join(gettempdir(), 'bhx_temp'))
    set_env_variable('LOGGING_LEVEL', get_logging_level())
    if platform.system() == 'Windows':
        set_env_variable('HOME', os.path.abspath('.\\'))
    set_env_variable('DRY_RUN', get_param('dry_run'))
    print_env_variables(
        [
            'HOME',
            'CONFIG',
            'OUTPUT',
            'TAGS',
            'PARALLEL_SCHEME',
            'PARALLEL_PROCESSES',
            'FEATURES_PATH',
            'TEMP',
            'LOGS',
            'LOGGING_LEVEL'
        ]
    )


def _store_tags_to_env_variable(tags):
    """
    Store tags to the environment variable.

    Args:
        tags (list): List of tags.
    """
    config = conf_mgr.get_config()
    tags_skip = config['test_run']['tags_to_skip']
    if isinstance(tags_skip, str) and tags_skip:
        tags_skip = [tags_skip]
    else:
        tags_skip = tags_skip
    # Normalize to list: CLI gives a list, config file may give a str for single
    # values (configobj list-type validation fails for single entries without commas).
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(',') if t.strip()]
    elif tags is None:
        tags = []
    tags_skip = [tag for tag in tags_skip if tag not in tags]
    exclusion_tags = ['~@{0}'.format(tag) for tag in tags_skip]
    tags = tags + exclusion_tags if tags else exclusion_tags
    # set_env_variable skips empty values, so clear directly or repeated in-process runs accumulate tags
    ConfigRun().set_env('tags', '')
    os.environ.pop('TAGS', None)
    if tags:
        set_env_variable('TAGS', ';'.join(tags))


_PARALLEL_INCOMPATIBLE_PARAMS = [
    (
        'stop',
        'stops only the worker process that hits the first failure; other workers keep running. '
        'Use serial execution (--parallel-processes 1) if you need fail-fast behaviour.',
    ),
    (
        'wip',
        'WIP mode may cause individual workers to fail when no @wip scenarios are assigned to them. '
        'Apply the @WIP tag via --tags instead.',
    ),
]


def _warn_parallel_incompatible_params():
    """Emit warnings for config/CLI params that do not work correctly in parallel mode."""
    for param, reason in _PARALLEL_INCOMPATIBLE_PARAMS:
        if get_param(param):
            print(f"WARNING: Parameter '{param}' is not compatible with parallel execution: {reason}")



if __name__ == '__main__':
    main()

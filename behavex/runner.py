# -*- coding: utf-8 -*-

"""BehaveX - Agile test wrapper on top of Behave (BDD).

This module provides the main entry point for running BehaveX tests,
including setup, execution, and reporting.
"""

# pylint: disable=W0703

# __future__ has been added to maintain compatibility
from __future__ import absolute_import, print_function

import codecs
import copy
import json
import logging.config
import multiprocessing
import os
import os.path
import platform
import re
import signal
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor
from multiprocessing.managers import DictProxy
from tempfile import gettempdir

from behave import __main__ as behave_script
from behave.model import Feature, Scenario, ScenarioOutline

# noinspection PyUnresolvedReferences
import behavex.outputs.report_json
from behavex import conf_mgr
from behavex.arguments import BEHAVE_ARGS, BEHAVEX_ARGS, parse_arguments
from behavex.conf_mgr import ConfigRun, get_env, get_param, set_env
from behavex.environment import extend_behave_hooks
from behavex.execution_singleton import ExecutionSingleton
from behavex.global_vars import global_vars
from behavex.outputs import report_xml
from behavex.outputs.report_json import generate_execution_info
from behavex.outputs.report_utils import (get_overall_status,
                                          match_for_execution,
                                          pretty_print_time, text,
                                          try_operate_descriptor)
from behavex.progress_bar import ProgressBar
from behavex.utils import (IncludeNameMatch, IncludePathsMatch, MatchInclude,
                           cleanup_folders, configure_logging,
                           copy_bootstrap_html_generator,
                           create_execution_complete_callback_function,
                           explore_features, generate_reports,
                           get_json_results, get_logging_level,
                           get_scenario_tags, get_text, join_feature_reports,
                           join_scenario_reports, len_scenarios,
                           print_env_variables, print_parallel,
                           set_behave_tags, set_env_variable,
                           set_environ_config, set_system_paths)

EXIT_OK = 0
EXIT_ERROR = 1
EXECUTION_BLOCKED_MSG = (
    'Some of the folders or files are being used by another '
    'program. Please, close them and try again...'
)

os.environ.setdefault('EXECUTION_CODE', '1')
match_include = None
include_path_match = None
include_name_match = None
scenario_lines = {}


def main():
    """BehaveX starting point.

    Parses command-line arguments and initiates the test run.
    """
    args = sys.argv[1:]
    exit_code = run(args)
    exit(exit_code)


def run(args):
    """Run BehaveX with the given arguments.

    Args:
        args (list): Command-line arguments.

    Returns:
        int: Exit code indicating success or failure.
    """
    global match_include
    global include_path_match
    global include_name_match
    args_parsed = parse_arguments(args)
    set_environ_config(args_parsed)
    ConfigRun().set_args(args_parsed)
    execution_code, rerun_list = setup_running_failures(args_parsed)
    if rerun_list:
        paths = ",".join(rerun_list)
        os.environ['FEATURES_PATH'] = paths
        global_vars.rerun_failures = True
        if execution_code == EXIT_ERROR:
            return EXIT_ERROR
    else:
        if len(get_param('paths')) > 0:
            for path in get_param('paths'):
                if not os.path.exists(path):
                    print('\nSpecified path was not found: {}'.format(path))
                    exit()
            paths = ",".join(get_param('paths'))
            os.environ['FEATURES_PATH'] = paths
        if len(get_param('include_paths')) > 0:
            for path in get_param('paths'):
                if not os.path.exists(path):
                    print('\nSpecified path was not found: {}'.format(path))
                    exit()
            paths = ",".join(get_param('include_paths'))
            features_path = os.environ.get('FEATURES_PATH')
            if features_path == '' or features_path is None:
                os.environ['FEATURES_PATH'] = paths
            else:
                os.environ['FEATURES_PATH'] = features_path + ',' + paths
    features_path = os.environ.get('FEATURES_PATH')
    if features_path == '' or features_path is None:
        os.environ['FEATURES_PATH'] = os.path.join(os.getcwd(), 'features')
    _set_env_variables(args_parsed)
    set_system_paths()
    cleanup_folders()
    copy_bootstrap_html_generator()
    configure_logging(args_parsed)
    match_include = MatchInclude()
    include_path_match = IncludePathsMatch()
    include_name_match = IncludeNameMatch()

    return launch_behavex()


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
                if not content:
                    print('\nThere are no failing test scenarios to run.')
                    return EXIT_ERROR, None
                return EXIT_OK, content.split(",")
        else:
            print('\nThe specified failing scenarios filename was not found: {}'.format(failures_path))
            return EXIT_ERROR, None
    else:
        return EXIT_OK, None


def init_multiprocessing(idQueue):
    """Initialize multiprocessing by ignoring SIGINT signals."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    # Retrieve one of the unique IDs
    worker_id = idQueue.get()
    # Use the unique ID to name the process
    multiprocessing.current_process().name = f'behave_worker-{worker_id}'


def launch_behavex():
    """Launch the BehaveX test execution in the specified parallel mode.

    Returns:
        int: Exit code indicating success or failure.
    """
    json_reports = []
    execution_codes = []
    results = None
    config = conf_mgr.get_config()
    features_path = os.environ.get('FEATURES_PATH')
    parallel_scheme = get_param('parallel_scheme')
    if get_param('dry_run'):
        parallel_processes = 1
        show_progress_bar = False
    else:
        parallel_processes = get_param('parallel_processes')
        parallel_processes = 1 if parallel_processes <= 1 else parallel_processes
        show_progress_bar = get_param('show_progress_bar')
    multiprocess = (
        True
        if get_param('parallel_processes') > 1 and not get_param('dry_run')
        else False
    )
    set_behave_tags()
    scenario = False
    notify_missing_features(features_path)
    features_list = {}
    for path in features_path.split(','):
        features_list[path] = explore_features(path)
    updated_features_list = create_scenario_line_references(features_list)
    parallel_scheme = '' if not multiprocess else parallel_scheme
    manager = multiprocessing.Manager()
    # shared variable to track scenarios that should be run but seems to be removed from execution (using scenarios.remove)
    shared_removed_scenarios = manager.dict()
    lock = manager.Lock()
    # Create a queue containing unique IDs from 0 to the number of parallel processes - 1
    # These IDs will be attributed to the process when they will be initialized
    idQueue = manager.Queue()
    for i in range(parallel_processes):
        idQueue.put(i)
    process_pool = ProcessPoolExecutor(max_workers=parallel_processes,
                                       initializer=init_multiprocessing,
                                       initargs=(idQueue,))
    global_vars.execution_start_time = time.time()
    try:
        config = ConfigRun()
        if parallel_processes == 1 or get_param('dry_run'):
            # Executing without parallel processes
            if get_param('dry_run'):
                print('Obtaining information about the reporting scope...')
            if global_vars.rerun_failures:
                all_paths = features_path.split(",")
            else:
                all_paths = [key for key in updated_features_list]
            execution_codes, json_reports = execute_tests(features_path=all_paths,
                                                          feature_filename=None,
                                                          feature_json_skeleton=None,
                                                          scenario_name=None,
                                                          multiprocess=False,
                                                          config=config,
                                                          lock=None,
                                                          shared_removed_scenarios=None)
        elif parallel_scheme == 'scenario':
            execution_codes, json_reports = launch_by_scenario(updated_features_list,
                                                               process_pool,
                                                               lock,
                                                               shared_removed_scenarios,
                                                               show_progress_bar)
            scenario = True
        elif parallel_scheme == 'feature':
            execution_codes, json_reports = launch_by_feature(updated_features_list,
                                                              process_pool,
                                                              lock,
                                                              show_progress_bar)
        wrap_up_process_pools(process_pool, json_reports, scenario)
        time_end = global_vars.execution_end_time

        if get_param('dry_run'):
            msg = '\nDry run completed. Please, see the report in {0}' ' folder.\n\n'
            print(msg.format(get_env('OUTPUT')))

        remove_temporary_files(parallel_processes, json_reports)

        failing_non_muted_tests = False
        # TODO: Replace logs below with test execution logs when an unexpected error occurs
        # behave_log_file = os.path.join(output_folder, 'behavex', 'logs', str(scenario['id_feature']), 'behave.log')
        # behave_log_file = os.path.join(output_folder, 'behavex', 'logs', str(json_test_configuration['id']), 'behave.log')
        results = get_json_results()
        totals = {"features": {"passed": 0, "failed": 0, "skipped": 0, "untested": 0},
                  "scenarios": {"passed": 0, "failed": 0, "skipped": 0, "untested": 0}}
        processed_feature_filenames = []
        if results:
            failures = {}
            for feature in results['features']:
                processed_feature_filenames.append(feature['filename'])
                filename = feature['filename']
                failures[filename] = []
                if feature['status'] == 'failed':
                    totals['features']['failed'] += 1
                elif feature['status'] == 'passed':
                    totals['features']['passed'] += 1
                elif feature['status'] == 'untested':
                    totals['features']['untested'] += 1
                else:
                    totals['features']['skipped'] += 1
                    totals['scenarios']['skipped'] += len(feature['scenarios'])
                    continue
                for scenario in feature['scenarios']:
                    if scenario['status'] == 'failed':
                        totals['scenarios']['failed'] += 1
                        failures[filename].append(scenario['name'])
                        if 'MUTE' not in scenario['tags']:
                            failing_non_muted_tests = True
                    elif scenario['status'] == 'passed':
                        totals['scenarios']['passed'] += 1
                    elif scenario['status'] == 'untested':
                        totals['scenarios']['untested'] += 1
                    else:
                        totals['scenarios']['skipped'] += 1
            if failures:
                failures_file_path = os.path.join(get_env('OUTPUT'), global_vars.report_filenames['report_failures'])
                with open(failures_file_path, 'w') as failures_file:
                    parameters = create_test_list(failures)
                    failures_file.write(parameters)
        # Calculates final exit code. execution_codes is 1 only if an execution exception arises
        if isinstance(execution_codes, list):
            execution_failed = True if sum(execution_codes) > 0 else False
            execution_interrupted_or_crashed = True if any([code == 2 for code in execution_codes]) else False
        else:
            execution_failed = True if execution_codes > 0 else False
            execution_interrupted_or_crashed = True if execution_codes == 2 else False
        exit_code = (EXIT_ERROR if (execution_failed and failing_non_muted_tests) or execution_interrupted_or_crashed else EXIT_OK)
    except KeyboardInterrupt:
        print('Caught KeyboardInterrupt, terminating workers')
        process_pool.shutdown(wait=False, cancel_futures=True)
        exit_code = 1
    if multiprocess:
        untested_features = totals['features']['untested']
        untested_scenarios = totals['scenarios']['untested']
        untested_features_msg = ', {} untested'.format(untested_features) if untested_features > 0 else ''
        untested_scenarios_msg = ', {} untested'.format(untested_scenarios) if untested_scenarios > 0 else ''
        def plural_char(n): return 's' if n != 1 else ''
        print('\n{} feature{} passed, {} failed, {} skipped{}'.format(totals['features']['passed'],
                                                                        plural_char(totals['features']['passed']),
                                                                        totals['features']['failed'],
                                                                        totals['features']['skipped'],
                                                                        untested_features_msg))
        print('{} scenario{} passed, {} failed, {} skipped{}'.format(totals['scenarios']['passed'],
                                                                       plural_char(totals['scenarios']['passed']),
                                                                       totals['scenarios']['failed'],
                                                                       totals['scenarios']['skipped'],
                                                                       untested_scenarios_msg))
        # TODO: print steps execution summary ('{} steps passed, {} failed, {} skipped{}, {} untested')
        print('Took: {}'.format(pretty_print_time(global_vars.execution_end_time - global_vars.execution_start_time)))
    if results and results['features']:
        print('\nHTML output report is located at: {}'.format(os.path.join(get_env('OUTPUT'), "report.html")))
    print('Exit code: {}'.format(exit_code))
    return exit_code


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


def create_test_list(test_list):
    """Create a list of tests to run.

    Args:
        test_list (dict): Dictionary of features and their scenarios.

    Returns:
        str: Comma-separated list of test paths.
    """
    paths = []
    sce_lines = get_env('scenario_lines')
    for feature, scenarios in test_list.items():
        for scenario_name in scenarios:
            paths.append('{}:{}'.format(feature, sce_lines[feature][scenario_name]))
    return ','.join(paths)


def create_scenario_line_references(features):
    """Create references for scenario lines in the features.

    Args:
        features (dict): Dictionary of features and their scenarios.

    Returns:
        dict: Updated features with scenario line references.
    """
    sce_lines = {}
    updated_features = {}
    for feature_path, scenarios in features.items():
        for scenario in scenarios:
            scenario_filename = text(scenario.filename)
            if scenario_filename not in sce_lines:
                sce_lines[scenario_filename] = {}
            if global_vars.rerun_failures or ".feature:" in feature_path:
                feature_without_scenario_line = feature_path.split(":")[0]
                if feature_without_scenario_line not in updated_features:
                    updated_features[feature_without_scenario_line] = []
                if isinstance(scenario, ScenarioOutline):
                    for scenario_outline_instance in scenario.scenarios:
                        if scenario_outline_instance.line == int(feature_path.split(":")[1]):
                            if scenario_outline_instance not in updated_features[feature_without_scenario_line]:
                                updated_features[feature_without_scenario_line].append(scenario_outline_instance)
                            sce_lines[scenario_filename][scenario_outline_instance.name] = scenario_outline_instance.line
                            break
                else:
                    if scenario.line == int(feature_path.split(":")[1]):
                        if scenario not in updated_features[feature_without_scenario_line]:
                            updated_features[feature_without_scenario_line].append(scenario)
                        sce_lines[scenario_filename][scenario.name] = scenario.line
            else:
                updated_features_path = scenario.feature.filename
                if updated_features_path not in updated_features:
                    updated_features[updated_features_path] = []
                if isinstance(scenario, ScenarioOutline):
                    for scenario_outline_instance in scenario.scenarios:
                        sce_lines[scenario_filename][scenario_outline_instance.name] = scenario_outline_instance.line
                        if scenario_outline_instance not in updated_features[updated_features_path]:
                            updated_features[updated_features_path].append(scenario_outline_instance)
                else:
                    sce_lines[scenario_filename][scenario.name] = scenario.line
                    if scenario not in updated_features[updated_features_path]:
                        updated_features[updated_features_path].append(scenario)
    set_env('scenario_lines', sce_lines)
    return updated_features


def launch_by_feature(features,
                      process_pool,
                      lock,
                      show_progress_bar):
    """Launch tests by feature in parallel.

    Args:
        features (dict): Dictionary of features and their scenarios.
        process_pool (ProcessPoolExecutor): Process pool executor.
        lock (Lock): Multiprocessing lock.
        show_progress_bar (bool): Whether to show the progress bar.

    Returns:
        tuple: Execution codes and JSON reports.
    """
    json_reports = []
    execution_codes = []
    serial_features = []
    parallel_features = []
    for features_path in features:
        feature = features[features_path][0].feature
        if 'SERIAL' in feature.tags:
            serial_features.append({"feature_filename": feature.filename,
                                    "feature_json_skeleton": _get_feature_json_skeleton(feature)})
        else:
            parallel_features.append({"feature_filename": feature.filename,
                                      "feature_json_skeleton": _get_feature_json_skeleton(feature)})
    if show_progress_bar:
        total_features = len(serial_features) + len(parallel_features)
        global_vars.progress_bar_instance = _get_progress_bar_instance(parallel_scheme="feature",
                                                                       total_elements=total_features)
        if global_vars.progress_bar_instance:
            global_vars.progress_bar_instance.start()
    if serial_features:
        print_parallel('feature.serial_execution')
        for serial_feature in serial_features:
            execution_code, map_json = execute_tests(features_path=None,
                                                     feature_filename=serial_feature["feature_filename"],
                                                     feature_json_skeleton=serial_feature["feature_json_skeleton"],
                                                     scenario_name=None,
                                                     multiprocess=True,
                                                     config=ConfigRun(),
                                                     lock=None,
                                                     shared_removed_scenarios=None)
            json_reports += [map_json]
            execution_codes.append(execution_code)
            if global_vars.progress_bar_instance:
                global_vars.progress_bar_instance.update()
    print_parallel('feature.running_parallels')
    for parallel_feature in parallel_features:
        feature_filename = parallel_feature["feature_filename"]
        feature_json_skeleton = parallel_feature["feature_json_skeleton"]
        future = process_pool.submit(execute_tests,
                                     features_path=None,
                                     feature_filename=feature_filename,
                                     feature_json_skeleton=feature_json_skeleton,
                                     scenario_name=None,
                                     multiprocess=True,
                                     config=ConfigRun(),
                                     lock=lock,
                                     shared_removed_scenarios=None)
        future.add_done_callback(create_execution_complete_callback_function(
            execution_codes,
            json_reports,
            global_vars.progress_bar_instance,
        ))
    return execution_codes, json_reports


def launch_by_scenario(features,
                       process_pool,
                       lock,
                       shared_removed_scenarios,
                       show_progress_bar):
    """Launch tests by scenario in parallel.

    Args:
        features (dict): Dictionary of features and their scenarios.
        process_pool (ProcessPoolExecutor): Process pool executor.
        lock (Lock): Multiprocessing lock.
        shared_removed_scenarios (dict): Shared dictionary of removed scenarios.
        show_progress_bar (bool): Whether to show the progress bar.

    Returns:
        tuple: Execution codes and JSON reports.
    """
    json_reports = []
    execution_codes = []
    parallel_scenarios = {}
    serial_scenarios = {}
    duplicated_scenarios = {}
    total_scenarios = 0
    features_with_empty_scenario_descriptions = []
    for features_path, scenarios in features.items():
        for scenario in scenarios:
            if include_path_match(scenario.filename, scenario.line) \
                    and include_name_match(scenario.name):
                scenario_tags = get_scenario_tags(scenario)
                if match_for_execution(scenario_tags):
                    if scenario.name == "":
                        features_with_empty_scenario_descriptions.append(scenario.filename)
                    feature_json_skeleton = _get_feature_json_skeleton(scenario)
                    scenario_information = {"feature_filename": scenario.feature.filename,
                                            "feature_json_skeleton": feature_json_skeleton,
                                            "scenario_name": scenario.name}
                    if 'SERIAL' in scenario_tags:
                        for key, list_scenarios in serial_scenarios.items():
                            if scenario_information in list_scenarios:
                                duplicated_scenarios.setdefault(key, []).append(scenario.name)
                        serial_scenarios.setdefault(features_path, []).append(scenario_information)
                        total_scenarios += 1
                    else:
                        for key, list_scenarios in parallel_scenarios.items():
                            if scenario_information in list_scenarios:
                                duplicated_scenarios.setdefault(key, []).append(scenario.name)
                        parallel_scenarios.setdefault(features_path, []).append(scenario_information)
                        total_scenarios += 1
    if show_progress_bar:
        global_vars.progress_bar_instance = _get_progress_bar_instance(parallel_scheme="scenario",
                                                                       total_elements=total_scenarios)
        if global_vars.progress_bar_instance:
            global_vars.progress_bar_instance.start()
    if duplicated_scenarios:
        print_parallel('scenario.duplicated_scenarios',
                       json.dumps(duplicated_scenarios, indent=4))
        exit(1)
    if features_with_empty_scenario_descriptions:
        print_parallel('feature.empty_scenario_descriptions',
                       '\n* '.join(features_with_empty_scenario_descriptions))
        exit(1)
    if serial_scenarios:
        print_parallel('scenario.serial_execution')
        for features_path, scenarios_in_feature in serial_scenarios.items():
            for scen_info in scenarios_in_feature:
                execution_code, json_report = execute_tests(features_path=features_path,
                                                            feature_filename=scen_info["feature_filename"],
                                                            feature_json_skeleton=scen_info["feature_json_skeleton"],
                                                            scenario_name=scen_info["scenario_name"],
                                                            multiprocess=True,
                                                            config=ConfigRun(),
                                                            lock=None,
                                                            shared_removed_scenarios=shared_removed_scenarios)
                execution_codes.append(execution_code)
                json_reports.append(json_report)
                if global_vars.progress_bar_instance:
                    global_vars.progress_bar_instance.update()
    if parallel_scenarios:
        print_parallel('scenario.running_parallels')
        for features_path in parallel_scenarios.keys():
            for scenario_information in parallel_scenarios[features_path]:
                feature_filename = scenario_information["feature_filename"]
                feature_json_skeleton = scenario_information["feature_json_skeleton"]
                scenario_name = scenario_information["scenario_name"]
                future = process_pool.submit(execute_tests,
                                             features_path=features_path,
                                             feature_filename=feature_filename,
                                             feature_json_skeleton=feature_json_skeleton,
                                             scenario_name=scenario_name,
                                             multiprocess=True,
                                             config=ConfigRun(),
                                             lock=lock,
                                             shared_removed_scenarios=shared_removed_scenarios
                                             )
                future.add_done_callback(create_execution_complete_callback_function(
                    execution_codes,
                    json_reports,
                    global_vars.progress_bar_instance
                ))
    return execution_codes, json_reports


def execute_tests(
        features_path,
        feature_filename,
        feature_json_skeleton,
        scenario_name,
        multiprocess,
        config,
        lock,
        shared_removed_scenarios):
    """
    Execute tests for the given feature or scenario.

    Args:
        features_path (str): Path to the features.
        feature_filename (str): Name of the feature file.
        feature_json_skeleton (str): JSON skeleton of the feature.
        scenario_name (str): Name of the scenario.
        multiprocess (bool): Whether to use multiprocessing.
        config (ConfigRun): Configuration object.
        lock (Lock): Multiprocessing lock.
        shared_removed_scenarios (dict): Shared dictionary of removed scenarios.

    Returns:
        tuple: Execution code and JSON report.
    """
    behave_args = None
    if multiprocess:
        ExecutionSingleton._instances[ConfigRun] = config
    extend_behave_hooks()
    try:
        # Execution ID is only important for multiprocessing so that
        # we can influence where output files end up
        execution_id = json.loads(feature_json_skeleton or '{}').get('id')
        behave_args = _set_behave_arguments(features_path=features_path,
                                            multiprocess=multiprocess,
                                            execution_id=execution_id,
                                            feature=feature_filename,
                                            scenario=scenario_name,
                                            config=config)
    except Exception as exception:
        traceback.print_exc()
        print(exception)
    execution_code, generate_report = _launch_behave(behave_args)
    # print("pipenv run behave {} --> Execution Code: {} --> Generate Report: {}".format(" ".join(behave_args), execution_code, generate_report))
    if generate_report:
        # print execution code
        if execution_code == 2:
            if feature_json_skeleton:
                json_output = {'environment': [],
                               'features': [json.loads(feature_json_skeleton)],
                               'steps_definition': []}
                for skeleton_feature in json_output["features"]:
                    if scenario_name:
                        for skeleton_scenario in skeleton_feature["scenarios"]:
                            if scenario_name_matching(scenario_name, skeleton_scenario['name']):
                                skeleton_scenario['status'] = 'failed'
                                skeleton_scenario['error_msg'] = get_text('scenario.execution_crashed')
                    else:
                        skeleton_feature['status'] = 'failed'
                        skeleton_feature['error_msg'] = 'Execution crashed. No outputs could be generated.'
                        for skeleton_scenario in skeleton_feature["scenarios"]:
                            skeleton_scenario['status'] = 'failed'
                            skeleton_scenario['error_msg'] = get_text('feature.execution_crashed')
            else:
                json_output = {'environment': [], 'features': [], 'steps_definition': []}
        else:
            json_output = dump_json_results()
        if scenario_name:
            json_output['features'] = filter_feature_executed(json_output,
                                                              text(feature_filename),
                                                              scenario_name)
            if len(json_output['features']) == 0 or len(json_output['features'][0]['scenarios']) == 0:
                # Adding scenario data if the test was removed from the execution (setting it as "Untested")
                json_output['features'] = [json.loads(feature_json_skeleton)]
            try:
                processing_xml_feature(json_output=json_output,
                                       scenario=scenario_name,
                                       feature_filename=feature_filename,
                                       lock=lock,
                                       shared_removed_scenarios=shared_removed_scenarios)
            except Exception as ex:
                logging.exception("There was a problem processing the xml file: {}".format(ex))
    else:
        json_output = {'environment': [], 'features': [], 'steps_definition': []}
    return execution_code, join_feature_reports(json_output)


def filter_feature_executed(json_output, filename, scenario_name):
    """
    Filter the executed feature from the JSON output.

    Args:
        json_output (dict): JSON output of the test execution.
        filename (str): Name of the feature file.
        scenario_name (str): Name of the scenario.
    """
    for feature in json_output.get('features', '')[:]:
        if feature.get('filename', '') == filename:
            mapping_scenarios = []
            for scenario in feature['scenarios']:
                if scenario_name_matching(scenario_name, scenario['name']):
                    mapping_scenarios.append(scenario)
            feature['scenarios'] = mapping_scenarios
            return [feature]
    return []


def _launch_behave(behave_args):
    """
    Launch Behave with the given arguments.

    Args:
        behave_args (list): List of arguments for Behave.

    Returns:
        tuple: Execution code and whether to generate a report.
    """
    # Save tags configuration to report only selected scenarios
    # Check for tags in config file
    generate_report = True
    try:
        stdout_file = behave_args[behave_args.index('--outfile') + 1]
        execution_code = behave_script.main(behave_args)
        if not os.path.exists(stdout_file):
            # Code 2 means the execution crashed and test was not properly executed
            execution_code = 2
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
    if os.path.exists(stdout_file):
        with open(os.path.join(get_env('OUTPUT'), 'merged_behave_outputs.log'), 'a+') as behave_log_file:
            behave_log_file.write(open(stdout_file, 'r').read())
        os.remove(stdout_file)
    return execution_code, generate_report


def wrap_up_process_pools(process_pool,
                          json_reports,
                          scenario=False):
    """
    Wrap up the process pools and generate the final report.

    Args:
        process_pool (ProcessPoolExecutor): Process pool executor.
        json_reports (list): List of JSON reports.
        scenario (bool): Whether the execution was by scenario.
    """
    merged_json = None
    output = os.path.join(get_env('OUTPUT'))
    try:
        process_pool.shutdown(wait=True)
    except Exception as ex:
        process_pool.shutdown(wait=False, cancel_futures=True)
    if type(json_reports) is list:
        if scenario:
            json_reports = join_scenario_reports(json_reports)
        merged_json = join_feature_reports(json_reports)
    else:
        merged_json = json_reports
    if global_vars.progress_bar_instance:
        global_vars.progress_bar_instance.finish()
    status_info = os.path.join(output, global_vars.report_filenames['report_overall'])
    with open(status_info, 'w') as file_info:
        over_status = {'status': get_overall_status(merged_json)}
        file_info.write(json.dumps(over_status))
    path_info = os.path.join(output, global_vars.report_filenames['report_json'])
    with open(path_info, 'w') as file_info:
        file_info.write(json.dumps(merged_json))
    if get_param('dry_run'):
        print('Generating outputs...')
    generate_reports(merged_json)


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

        path_stdout = os.path.join(gettempdir(), 'stdout{}.txt'.format(i + 1))
        if os.path.exists(path_stdout):
            try:
                os.chmod(path_stdout, 511)  # nosec
                os.remove(path_stdout)
            except Exception as remove_ex:
                print(remove_ex)

    name = multiprocessing.current_process().name.split('-')[-1]
    stdout_file = os.path.join(gettempdir(), 'std{}2.txt'.format(name))
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
    if os.path.exists(stdout_file):
        os.chmod(stdout_file, 511)  # nosec
        if not os.access(stdout_file, os.W_OK):
            os.remove(stdout_file)
    # removing any pending temporary files
    if type(json_reports) is not list:
        json_reports = [json_reports]
    for json_report in json_reports:
        if 'features' in json_report and json_report['features']:
            feature_name = os.path.join(
                get_env('OUTPUT'), u'{}.tmp'.format(json_report['features'][0]['name'])
            )
            if os.path.exists(feature_name):
                try:
                    os.remove(feature_name)
                except Exception as remove_ex:
                    print(remove_ex)


def processing_xml_feature(json_output, scenario, feature_filename, lock=None, shared_removed_scenarios=None):
    """
    Process the XML feature and update the JSON output.

    Args:
        json_output (dict): JSON output of the test execution.
        scenario (Scenario): Scenario object.
        feature_filename (str): Name of the feature file.
        lock (Lock): Multiprocessing lock.
        shared_removed_scenarios (dict): Shared dictionary of removed scenarios.
    """
    if lock:
        lock.acquire()
    try:
        feature_contains_scenarios = True if (json_output['features'] and
                                              'scenarios' in json_output['features'][0] and
                                              json_output['features'][0]["scenarios"]) else False
        if type(shared_removed_scenarios) == DictProxy and not feature_contains_scenarios:
            # Assuming the scenario was removed from the execution (using scenarios.remove) as it is not in execution
            if feature_filename not in shared_removed_scenarios:
                shared_removed_scenarios[feature_filename] = 1
            else:
                shared_removed_scenarios[feature_filename] += 1
        if feature_contains_scenarios:
            reported_scenarios = json_output['features'][0]['scenarios']
            executed_scenarios = []
            for reported_scenario in reported_scenarios:
                reported_name = reported_scenario['name']
                if reported_name == scenario or ('@' in reported_name and
                                                 scenario_name_matching(scenario, reported_name)):
                    executed_scenarios.append(reported_scenario)
            json_output['features'][0]['scenarios'] = executed_scenarios
            feature_name = os.path.join(
                get_env('OUTPUT'), u'{}.tmp'.format(os.path.basename(feature_filename))
            )
            processed_feature_data = json_output['features'][0]
            processed_feature_data['scenarios'] = executed_scenarios
            if os.path.exists(feature_name):
                for _ in range(0, 10):
                    try:
                        processed_feature_data = json.load(open(feature_name, 'r'))
                        with open(feature_name, 'w') as feature_file:
                            for executed_scenario in executed_scenarios:
                                processed_feature_data['scenarios'].append(executed_scenario)
                            json.dump(processed_feature_data, feature_file)
                        break
                    except Exception as ex:
                        logging.debug(ex)
                        logging.debug('Retrying reading from {}'.format(feature_name))
                        time.sleep(1)
            else:
                with codecs.open(feature_name, 'w', 'utf8') as feature_file:
                    json.dump(processed_feature_data, feature_file)
            # calculate the total number of scenarios that should be executed
            removed_scenarios = 0
            if shared_removed_scenarios and feature_filename in shared_removed_scenarios:
                removed_scenarios = shared_removed_scenarios[feature_filename]
            total_scenarios = len_scenarios(feature_filename) - removed_scenarios
            if len(processed_feature_data['scenarios']) == total_scenarios:
                try:
                    report_xml.export_feature_to_xml(processed_feature_data, False)
                except Exception as ex:
                    traceback.print_exc()
                    print(ex)
                finally:
                    path_tmp = u'{}.tmp'.format(feature_name[:-4])
                    os.remove(path_tmp)
    except Exception as ex:
        raise ex
    finally:
        if lock:
            lock.release()


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
    _store_tags_to_env_variable(args.tags)
    if get_param('include_paths'):
        set_env_variable('INCLUDE_PATHS', get_param('include_paths'))
    if get_param('include'):
        set_env_variable('INCLUDE', get_param('include'))
    if get_param('name'):
        set_env_variable('NAME', args.name)
    for arg in BEHAVEX_ARGS[4:]:
        set_env_variable(arg.upper(), get_param(arg))

    set_env_variable('TEMP', os.path.join(get_env('output'), 'temp'))
    set_env_variable('LOGS', os.path.join(get_env('output'), 'outputs', 'logs'))
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
    tags = tags if tags is not None else []
    tags_skip = [tag for tag in tags_skip if tag not in tags]
    tags = tags + ['~@{0}'.format(tag) for tag in tags_skip] if tags else []
    if tags:
        for tag in tags:
            if get_env('TAGS'):
                set_env_variable('TAGS', get_env('tags') + ';' + tag)
            else:
                set_env_variable('TAGS', tag)
    else:
        set_env_variable('TAGS', '')


def _set_behave_arguments(features_path, multiprocess, execution_id=None, feature=None, scenario=None, config=None):
    """
    Set the arguments for Behave framework based on the given parameters.

    Args:
        features_path (str): Path to the features.
        multiprocess (bool): Whether to use multiprocessing.
        execution_id (str): Execution ID.
        feature (Feature): Feature object.
        scenario (Scenario): Scenario object.
        config (ConfigRun): Configuration object.

    Returns:
        list: List of arguments to be used when executing Behave.
    """
    arguments = []
    output_folder = config.get_env('OUTPUT')
    if multiprocess:
        if not feature:
            arguments.append(features_path)
        else:
            arguments.append(feature)
        arguments.append('--no-summary')
        if scenario:
            outline_examples_in_name = re.findall('<[\\S]*>', scenario)
            pattern = "(.?--.?@\\d+.\\d+\\s*\\S*)"
            if bool(re.search(pattern, scenario)):
                scenario_outline_compatible = '^{}$'.format(re.escape(scenario))
            else:
                scenario_outline_compatible = '^{}{}?$'.format(re.escape(scenario), pattern)
            if outline_examples_in_name:
                for example_name in outline_examples_in_name:
                    escaped_example_name = re.escape(example_name)
                    scenario_outline_compatible = scenario_outline_compatible.replace(escaped_example_name, "[\\S ]*")
            arguments.append('--name')
            arguments.append("{}".format(scenario_outline_compatible))
        worker_id = multiprocessing.current_process().name.split('-')[-1]

        arguments.append('--outfile')
        arguments.append(os.path.join(gettempdir(), 'stdout{}.txt'.format(worker_id)))

        arguments.append('-D')
        arguments.append(f'worker_id={worker_id}')
    else:
        if type(features_path) is list:
            for feature_path in features_path:
                arguments.append(feature_path)
        else:
            arguments.append(features_path)
        if get_param('dry_run'):
            arguments.append('--no-summary')
        else:
            arguments.append('--summary')
        arguments.append('--junit-directory')
        arguments.append(output_folder)
        arguments.append('--outfile')
        arguments.append(os.path.join(output_folder, 'behave', 'behave.log'))
        arguments.append('-D')
        arguments.append(f'worker_id=0')
    arguments.append('--no-skipped')
    arguments.append('--no-junit')
    run_wip_tests = False
    if get_env('tags'):
        tags = get_env('tags').split(';')
        for tag in tags:
            arguments.append('--tags')
            arguments.append(tag)
            if tag.upper() in ['WIP', '@WIP']:
                run_wip_tests = True
    if not run_wip_tests:
        arguments.append('--tags')
        arguments.append('~@WIP')
    arguments.append('--tags')
    arguments.append('~@MANUAL')
    args_sys = config.args
    set_args_captures(arguments, args_sys)
    if args_sys.no_snippets:
        arguments.append('--no-snippets')
    for arg in BEHAVE_ARGS:
        value_arg = getattr(args_sys, arg) if hasattr(args_sys, arg) else False
        if arg == 'include':
            if multiprocess or not value_arg:
                continue
            else:
                features_path = os.path.abspath(os.environ['FEATURES_PATH'])
                value_arg = value_arg.replace(features_path, 'features').replace(
                    '\\', '\\\\'
                )
        if arg == 'define' and value_arg:
            for key_value in value_arg:
                arguments.append('--define')
                arguments.append(key_value)
        if value_arg and arg not in BEHAVEX_ARGS and arg != 'define':
            arguments.append('--{}'.format(arg.replace('_', '-')))
            if value_arg and not isinstance(value_arg, bool):
                arguments.append(value_arg)
                if arguments == 'logging_level':
                    set_env_variable(arg, value_arg)
                else:
                    os.environ[arg] = str(value_arg)
    return arguments


def _get_feature_json_skeleton(behave_element):
    """
    Get the JSON skeleton for the given feature or scenario.

    Args:
        behave_element (Feature or Scenario): Behave element.

    Returns:
        str: JSON skeleton of the feature.
    """
    if type(behave_element) is Feature:
        feature = behave_element
    elif type(behave_element) is Scenario:
        feature = copy.copy(behave_element.feature)
        feature.scenarios = [behave_element]
    else:
        raise Exception("No feature or scenario to process...")
    execution_info = generate_execution_info([feature])
    return json.dumps(execution_info[0]) if execution_info else {}


def _get_progress_bar_instance(parallel_scheme, total_elements):
    """
    Get the progress bar instance.

    Args:
        parallel_scheme (str): Parallel scheme (feature or scenario).
        total_elements (int): Total number of elements.

    Returns:
        ProgressBar: Progress bar instance.
    """
    try:
        config = conf_mgr.get_config()
        print_updates_in_new_lines = True if config['progress_bar']['print_updates_in_new_lines'] else False
        progress_bar_prefix = "Executed {}s".format(parallel_scheme)
        progress_bar_instance = ProgressBar(progress_bar_prefix,
                                            total_elements,
                                            print_updates_in_new_lines=print_updates_in_new_lines)
    except Exception as ex:
        print("There was an error creating the progress bar: {}".format(ex))
        return None
    return progress_bar_instance


def set_args_captures(args, args_sys):
    """
    Set the capture arguments for Behave.

    Args:
        args (list): List of arguments.
        args_sys (Namespace): Parsed command-line arguments.
    """
    for default_arg in ['capture', 'capture_stderr', 'logcapture']:
        if not getattr(args_sys, 'no_{}'.format(default_arg)):
            args.append('--no-{}'.format(default_arg.replace('_', '-')))


def scenario_name_matching(abstract_scenario_name, scenario_name):
    """
    Check if the scenario name matches the abstract scenario name (as the scenario might represent a Scenario Outline, with example parameters in name).

    Args:
        abstract_scenario_name (str): Abstract scenario name
        scenario_name (str): Scenario name to map against the abstract scenario name.

    Returns:
        bool: Whether the scenario name matches the abstract scenario name.
    """
    outline_examples_in_name = re.findall('<\\S*>', abstract_scenario_name)
    scenario_outline_compatible = '^{}(.--.@\\d+.\\d+\\s*\\S*)?$'.format(re.escape(abstract_scenario_name))
    for example_name in outline_examples_in_name:
        escaped_example_name = re.escape(example_name)
        scenario_outline_compatible = scenario_outline_compatible.replace(escaped_example_name, "[\\S ]*")
    pattern = re.compile(scenario_outline_compatible)
    return pattern.match(scenario_name)


def dump_json_results():
    """
    Dump the JSON results of the test execution.

    Returns:
        dict: JSON output of the test execution.
    """
    if multiprocessing.current_process().name == 'MainProcess':
        path_info = os.path.join(
            os.path.abspath(get_env('OUTPUT')),
            global_vars.report_filenames['report_json'],
        )
    else:
        process_name = multiprocessing.current_process().name.split('-')[-1]
        path_info = os.path.join(gettempdir(), 'result{}.tmp'.format(process_name))

    def _load_json():
        """this function load from file"""
        with open(path_info, 'r') as info_file:
            json_output_file = info_file.read()
            json_output_converted = json.loads(json_output_file)
        return json_output_converted

    json_output = {'environment': [], 'features': [], 'steps_definition': []}
    if os.path.exists(path_info):
        json_output = try_operate_descriptor(path_info, _load_json, return_value=True)
    return json_output


if __name__ == '__main__':
    main()

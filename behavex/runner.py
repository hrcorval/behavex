# -*- coding: utf-8 -*-

"""BehaveX - Agile test wrapper on top of Behave (BDD)."""

# pylint: disable=W0703

# __future__ has been added to maintain compatibility
from __future__ import absolute_import, print_function

import codecs
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
import copy
import traceback
from operator import itemgetter
from tempfile import gettempdir

from behave import __main__ as behave_script
from behave.model import ScenarioOutline, Scenario, Feature

# noinspection PyUnresolvedReferences
import behavex.outputs.report_json
from behavex import conf_mgr
from behavex.arguments import BEHAVE_ARGS, BEHAVEX_ARGS, parse_arguments
from behavex.conf_mgr import ConfigRun, get_env, get_param, set_env
from behavex.environment import extend_behave_hooks
from behavex.execution_singleton import ExecutionSingleton
from behavex.global_vars import global_vars
from behavex.outputs import report_xml
from behavex.outputs.report_utils import (
    get_overall_status,
    match_for_execution,
    pretty_print_time,
    text,
    try_operate_descriptor,
)
from behavex.utils import (
    IncludeNameMatch,
    IncludePathsMatch,
    MatchInclude,
    cleanup_folders,
    configure_logging,
    copy_bootstrap_html_generator,
    create_partial_function_append,
    explore_features,
    generate_reports,
    get_json_results,
    get_logging_level,
    join_feature_reports,
    join_scenario_reports,
    len_scenarios,
    print_env_variables,
    print_parallel,
    set_behave_tags,
    set_env_variable,
    set_environ_config,
    set_system_paths,
    get_scenario_tags,
)
from behavex.outputs.report_json import generate_execution_info


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
    """BehaveX starting point."""
    args = sys.argv[1:]
    exit_code = run(args)
    exit(exit_code)


def run(args):
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
    if os.environ.get('FEATURES_PATH') == '':
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


def init_multiprocessing():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def launch_behavex():
    """Launch the BehaveX test execution in the specified parallel mode."""
    json_reports = []
    execution_codes = []
    time_init = time.time()
    features_path = os.environ.get('FEATURES_PATH')
    parallel_scheme = get_param('parallel_scheme')
    parallel_processes = get_param('parallel_processes')
    multiprocess = (
        True
        if get_param('parallel_processes') > 1 and not get_param('dry_run')
        else False
    )
    if not multiprocess:
        parallel_scheme = ''
    set_behave_tags()
    scenario = False
    notify_missing_features(features_path)
    features_list = {}
    for path in features_path.split(','):
        features_list[path] = explore_features(path)
    updated_features_list = create_scenario_line_references(features_list)
    manager = multiprocessing.Manager()
    lock = manager.Lock()
    # shared variable to track scenarios that should be run but seems to be removed from execution (using scenarios.remove)
    shared_removed_scenarios = manager.dict()
    process_pool = multiprocessing.Pool(parallel_processes, initializer=init_multiprocessing(), initargs=(lock,))
    try:
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
                                                          scenario_name=None,
                                                          multiprocess=False,
                                                          config=ConfigRun())
        elif parallel_scheme == 'scenario':
            execution_codes, json_reports = launch_by_scenario(
                updated_features_list, process_pool, lock, shared_removed_scenarios
            )
            scenario = True
        elif parallel_scheme == 'feature':
            execution_codes, json_reports = launch_by_feature(
                updated_features_list, process_pool
            )
        wrap_up_process_pools(process_pool, json_reports, multiprocess, scenario)
        time_end = time.time()

        if get_param('dry_run'):
            msg = '\nDry run completed. Please, see the report in {0}' ' folder.\n\n'
            print(msg.format(get_env('OUTPUT')))

        remove_temporary_files(parallel_processes, json_reports)

        results = get_json_results()
        failing_non_muted_tests = False
        totals = {"features": {"passed": 0, "failed": 0, "skipped": 0},
                  "scenarios": {"passed": 0, "failed": 0, "skipped": 0}}
        if results:
            failures = {}
            for feature in results['features']:
                if feature['status'] == 'failed':
                    totals['features']['failed'] += 1
                    filename = feature['filename']
                    failures[filename] = []
                elif feature['status'] == 'passed':
                    totals['features']['passed'] += 1
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
                    else:
                        totals['scenarios']['skipped'] += 1
            if failures:
                failures_file_path = os.path.join(get_env('OUTPUT'), global_vars.report_filenames['report_failures'])
                with open(failures_file_path, 'w') as failures_file:
                    parameters = create_test_list(failures)
                    failures_file.write(parameters)
        # Calculates final exit code. execution_codes is 1 only if an execution exception arises
        if isinstance(execution_codes, list):
            execution_exception = True if sum(execution_codes) > 0 else False
        else:
            execution_exception = True if execution_codes > 0 else False
        exit_code = (
            EXIT_ERROR if execution_exception or failing_non_muted_tests else EXIT_OK
        )
    except KeyboardInterrupt:
        print('Caught KeyboardInterrupt, terminating workers')
        process_pool.terminate()
        process_pool.join()
        exit_code = 1
    if multiprocess:
        plural_char = lambda n: 's' if n != 1 else ''
        print('\n{} feature{} passed, {} failed, {} skipped (*)'.format(totals['features']['passed'],
                                                                        plural_char(totals['features']['passed']),
                                                                        totals['features']['failed'],
                                                                        totals['features']['skipped']))
        print('{} scenario{} passed, {} failed, {} skipped (*)'.format(totals['scenarios']['passed'],
                                                                       plural_char(totals['scenarios']['passed']),
                                                                       totals['scenarios']['failed'],
                                                                       totals['scenarios']['skipped']))
        print('Took: {}'.format(pretty_print_time(time_end - time_init)))
    if results and results['features']:
        print('\nHTML output report is located at: {}'.format(os.path.join(get_env('OUTPUT'), "report.html")))
    print('Exit code: {}'.format(exit_code))
    return exit_code


def notify_missing_features(features_path):
    if global_vars.rerun_failures:
        all_paths = features_path.split(",")
        for path in all_paths:
            include_path = path.partition(':')[0]
            if not os.path.exists(os.path.normpath(include_path)):
                print_parallel('path.not_found', os.path.realpath(include_path))


def create_test_list(test_list):
    paths = []
    sce_lines = get_env('scenario_lines')
    for feature, scenarios in test_list.items():
        for scenario_name in scenarios:
            paths.append('{}:{}'.format(feature, sce_lines[feature][scenario_name]))
    return ','.join(paths)


def create_scenario_line_references(features):
    sce_lines = {}
    updated_features = {}
    for feature_path, scenarios in features.items():
        for scenario in scenarios:
            scenario_filename = text(scenario.filename)
            if scenario_filename not in sce_lines:
                sce_lines[scenario_filename] = {}
            scenario_lines = sce_lines[scenario_filename]
            if global_vars.rerun_failures or ".feature:" in feature_path:
                feature_without_scenario_line = feature_path.split(":")[0]
                if feature_without_scenario_line not in updated_features:
                    updated_features[feature_without_scenario_line] = []
                if isinstance(scenario, ScenarioOutline):
                    for scenario_outline_instance in scenario.scenarios:
                        if scenario_outline_instance.line == int(feature_path.split(":")[1]):
                            if scenario_outline_instance not in updated_features[feature_without_scenario_line]:
                                updated_features[feature_without_scenario_line].append(scenario_outline_instance)
                            scenario_lines[scenario_outline_instance.name] = scenario_outline_instance.line
                            break
                else:
                    if scenario.line == int(feature_path.split(":")[1]):
                        if scenario not in updated_features[feature_without_scenario_line]:
                            updated_features[feature_without_scenario_line].append(scenario)
                        scenario_lines[scenario.name] = scenario.line
            else:
                updated_features_path = scenario.feature.filename
                if updated_features_path not in updated_features:
                    updated_features[updated_features_path] = []
                if isinstance(scenario, ScenarioOutline):
                    for scenario_outline_instance in scenario.scenarios:
                        scenario_lines[scenario_outline_instance.name] = scenario_outline_instance.line
                        if scenario_outline_instance not in updated_features[updated_features_path]:
                            updated_features[updated_features_path].append(scenario_outline_instance)
                else:
                    scenario_lines[scenario.name] = scenario.line
                    if scenario not in updated_features[updated_features_path]:
                        updated_features[updated_features_path].append(scenario)
    set_env('scenario_lines', sce_lines)
    return updated_features


def launch_by_feature(features, process_pool):
    json_reports = []
    execution_codes = []
    serial_features = []
    parallel_features = []
    for features_path in features:
        feature = features[features_path][0].feature
        if 'SERIAL' in feature.tags:
            serial_features.append(feature.filename)
        else:
            parallel_features.append({"feature_filename": feature.filename,
                                      "feature_json_skeleton": _get_feature_json_skeleton(feature)})
    if serial_features:
        print_parallel('feature.serial_execution')
        for feature_filename in serial_features:
            execution_code, map_json = execute_tests(None, feature_filename, None, None, True, config=ConfigRun())
            json_reports += [map_json]
            execution_codes.append(execution_code)
    print_parallel('feature.running_parallels')
    for parallel_feature in parallel_features:
        feature_filename = parallel_feature["feature_filename"]
        feature_json_skeleton = parallel_feature["feature_json_skeleton"]
        process_pool.apply_async(
            execute_tests,
            (None, feature_filename, feature_json_skeleton, None, True, ConfigRun()),
            callback=create_partial_function_append(execution_codes, json_reports),
        )
    return execution_codes, json_reports


def launch_by_scenario(features, process_pool, lock, shared_removed_scenarios):
    json_reports = []
    execution_codes = []
    parallel_scenarios = {}
    serial_scenarios = {}
    duplicated_scenarios = {}
    features_with_empty_scenario_descriptions = []
    for features_path, scenarios in features.items():
        for scenario in scenarios:
            # noinspection PyCallingNonCallable
            if include_path_match(scenario.filename, scenario.line) \
                    and include_name_match(scenario.name):
                scenario_tags = get_scenario_tags(scenario, include_example_tags=True)
                if match_for_execution(scenario_tags):
                    if scenario.name == "":
                        features_with_empty_scenario_descriptions.append(scenario.filename)
                    feature_json_skeleton = _get_feature_json_skeleton(scenario)
                    scenario_information = {"feature_filename": scenario.feature.filename,
                                            "feature_json_skeleton": feature_json_skeleton,
                                            "scenario_name": scenario.name}
                    if 'SERIAL' in scenario_tags:
                        for key in serial_scenarios.keys():
                            if scenario_information in serial_scenarios[key]:
                                if key not in duplicated_scenarios:
                                    duplicated_scenarios[key] = []
                                duplicated_scenarios[key].append(scenario.name)
                        if features_path not in serial_scenarios:
                            serial_scenarios[features_path] = []
                        if scenario_information not in serial_scenarios[features_path]:
                            serial_scenarios[features_path].append(scenario_information)
                    else:
                        for key in parallel_scenarios.keys():
                            if scenario_information in parallel_scenarios[key]:
                                if key not in duplicated_scenarios:
                                    duplicated_scenarios[key] = []
                                duplicated_scenarios[key].append(scenario.name)
                        if features_path not in parallel_scenarios:
                            parallel_scenarios[features_path] = []
                        if parallel_scenarios not in parallel_scenarios[features_path]:
                            parallel_scenarios[features_path].append(scenario_information)
    if duplicated_scenarios:
        print_parallel('scenario.duplicated_scenarios', json.dumps(duplicated_scenarios, indent=4))
        exit(1)
    if features_with_empty_scenario_descriptions:
        print_parallel('feature.empty_scenario_descriptions', '\n* '.join(features_with_empty_scenario_descriptions))
        exit(1)
    if serial_scenarios:
        print_parallel('scenario.serial_execution')
        for features_path, scenarios_in_feature in serial_scenarios.items():
            json_serial_reports = [
                execute_tests(features_path=features_path,
                              feature_filename=scenario_information["feature_filename"],
                              feature_json_skeleton=scenario_information["feature_json_skeleton"],
                              scenario_name=scenario_information["scenario_name"],
                              config=ConfigRun(),
                              shared_removed_scenarios=shared_removed_scenarios)
                for scenario_information in scenarios_in_feature
            ]
            # execution_codes and json_reports are forced to be of type a list.
            execution_codes += list(map(itemgetter(0), json_serial_reports))
            json_reports += list(map(itemgetter(1), json_serial_reports))

    print_parallel('scenario.running_parallels')
    for features_path in parallel_scenarios.keys():
        for scenario_information in parallel_scenarios[features_path]:
            feature_filename = scenario_information["feature_filename"]
            feature_json_skeleton = scenario_information["feature_json_skeleton"]
            scenario_name = scenario_information["scenario_name"]
            process_pool.apply_async(
                execute_tests,
                args=(features_path, feature_filename, feature_json_skeleton, scenario_name,
                      True, ConfigRun(), lock, shared_removed_scenarios),
                callback=create_partial_function_append(execution_codes, json_reports),
            )
    return execution_codes, json_reports


def execute_tests(features_path, feature_filename=None, feature_json_skeleton=None, scenario_name=None,
                  multiprocess=True, config=None, lock=None, shared_removed_scenarios=None):
    behave_args = None
    if multiprocess:
        ExecutionSingleton._instances[ConfigRun] = config
    extend_behave_hooks()
    try:
        behave_args = _set_behave_arguments(features_path, multiprocess, feature_filename, scenario_name, config)
    except Exception as exception:
        traceback.print_exc()
        print(exception)
    execution_code, generate_report = _launch_behave(behave_args)
    # print("pipenv run behave {} --> Execution Code: {} --> Generate Report: {}".format(" ".join(behave_args), execution_code, generate_report))
    if generate_report:
        if execution_code == 2:
            if feature_json_skeleton:
                json_output = {'environment': [], 'features': [json.loads(feature_json_skeleton)], 'steps_definition': []}
            else:
                json_output = {'environment': [], 'features': [], 'steps_definition': []}
        else:
            json_output = dump_json_results()
        if scenario_name:
            json_output['features'] = filter_feature_executed(
                json_output, text(feature_filename), scenario_name
            )
            try:
                processing_xml_feature(json_output, scenario_name, feature_filename, lock, shared_removed_scenarios)
            except Exception as ex:
                logging.exception(ex)
    else:
        json_output = {'environment': [], 'features': [], 'steps_definition': []}
    return execution_code, join_feature_reports(json_output)


def filter_feature_executed(json_output, filename, scenario_name):
    for feature in json_output.get('features', '')[:]:
        if feature.get('filename', '') == filename:
            mapping_scenarios = []
            for scenario in feature['scenarios']:
                if scenario_name_matching(scenario_name, scenario['name']):
                    mapping_scenarios.append(scenario)
            feature['scenarios'] = mapping_scenarios
            return [feature]


def _launch_behave(behave_args):
    # Save tags configuration to report only selected scenarios
    # Check for tags in config file
    generate_report = True
    try:
        stdout_file = behave_args[behave_args.index('--outfile') + 1]
        if os.path.exists(stdout_file):
            os.remove(stdout_file)
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
    return execution_code, generate_report


def wrap_up_process_pools(process_pool, json_reports, multi_process, scenario=False):
    merged_json = None
    output = os.path.join(get_env('OUTPUT'))
    try:
        process_pool.close()
        process_pool.join()
        if type(json_reports) is list:
            if scenario:
                json_reports = join_scenario_reports(json_reports)
            merged_json = join_feature_reports(json_reports)
        else:
            merged_json = json_reports
    except KeyboardInterrupt:
        process_pool.terminate()
        process_pool.join()
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
    if lock:
        lock.acquire()
    try:
        feature_contains_scenarios = True if (json_output['features'] and
                                              'scenarios' in json_output['features'][0] and
                                              json_output['features'][0]["scenarios"]) else False
        if shared_removed_scenarios is not None and not feature_contains_scenarios:
            # Assuming the scenario was removed from the execution (using scenarios.remove) as it is not in current execution
            if feature_filename not in shared_removed_scenarios:
                shared_removed_scenarios[feature_filename] = 1
            else:
                shared_removed_scenarios[feature_filename] += 1
        if feature_contains_scenarios:
            reported_scenarios = json_output['features'][0]['scenarios']
            executed_scenario = []
            for reported_scenario in reported_scenarios:
                reported_name = reported_scenario['name']
                if reported_name == scenario or ('@' in reported_name and scenario_name_matching(scenario, reported_name)):
                    executed_scenario.append(reported_scenario)
            json_output['features'][0]['scenarios'] = executed_scenario
            feature_name = os.path.join(
                get_env('OUTPUT'), u'{}.tmp'.format(os.path.basename(feature_filename))
            )
            processed_feature_data = json_output['features'][0]
            processed_feature_data['scenarios'] = executed_scenario
            if os.path.exists(feature_name):
                for _ in range(0, 10):
                    try:
                        processed_feature_data = json.load(open(feature_name, 'r'))
                        with open(feature_name, 'w') as feature_file:
                            for scen in executed_scenario:
                                processed_feature_data['scenarios'].append(scen)
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
            total_scenarios = len_scenarios(feature_filename)-removed_scenarios
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
            'LOGGING_LEVEL',
        ]
    )


def _store_tags_to_env_variable(tags):
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


def _set_behave_arguments(features_path, multiprocess, feature=None, scenario=None, config=None):
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
        name = multiprocessing.current_process().name.split('-')[-1]
        arguments.append('--outfile')
        arguments.append(os.path.join(gettempdir(), 'stdout{}.txt'.format(name)))
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
    """ This function returns json report skeleton for the feature associated to a scenario."""
    if type(behave_element) is Feature:
        feature = behave_element
    elif type(behave_element) is Scenario:
        feature = copy.copy(behave_element.feature)
        feature.scenarios = [behave_element]
    else:
        raise Exception("No feature or scenario to process...")
    json_skeleton = json.dumps(generate_execution_info([feature])[0])
    return json_skeleton


def set_args_captures(args, args_sys):
    for default_arg in ['capture', 'capture_stderr', 'logcapture']:
        if not getattr(args_sys, 'no_{}'.format(default_arg)):
            args.append('--no-{}'.format(default_arg.replace('_', '-')))


def scenario_name_matching(abstract_scenario_name, scenario_name):
    outline_examples_in_name = re.findall('<\\S*>', abstract_scenario_name)
    scenario_outline_compatible = '^{}(.--.@\\d+.\\d+\\s*\\S*)?$'.format(re.escape(abstract_scenario_name))
    for example_name in outline_examples_in_name:
        escaped_example_name = re.escape(example_name)
        scenario_outline_compatible = scenario_outline_compatible.replace(escaped_example_name, "[\\S ]*")
    pattern = re.compile(scenario_outline_compatible)
    return pattern.match(scenario_name)


def dump_json_results():
    """ Do reporting. """
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

    json_output = {'environment': '', 'features': [], 'steps_definition': ''}
    if os.path.exists(path_info):
        json_output = try_operate_descriptor(path_info, _load_json, return_value=True)
    return json_output


if __name__ == '__main__':
    main()

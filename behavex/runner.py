# -*- coding: utf-8 -*-

"""BehaveX - Agile test wrapper on top of Behave (BDD)."""

# pylint: disable=W0703

# __future__ has been added to maintain compatibility
from __future__ import absolute_import, print_function

import codecs
import json
import logging.config
import multiprocessing as lib_multiprocessing
import os
import os.path
import platform
import re
import sys
import time
import traceback
from operator import itemgetter
from tempfile import gettempdir

from behave import __main__ as behave_script

from behavex import conf_mgr
from behavex.arguments import BEHAVE_ARGS, BEHAVEX_ARGS, parse_arguments
from behavex.conf_mgr import ConfigRun, Singleton, get_env, get_param, set_env
from behavex.outputs import report_xml
from behavex.outputs.report_json import OVERALL_STATUS_FILE
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
    check_environment_file,
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
)

EXIT_OK = 0
EXIT_ERROR = 1
EXECUTION_BLOCKED_MSG = (
    'Some of the folders or files are being used by another '
    'program. Please, close them and try again...'
)

FWK_PATH = os.environ.get('BEHAVEX_PATH')
INFO_FILE = 'report.json'

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
    """Perform all the required actions in order to do the test execution."""
    global match_include
    global include_path_match
    global include_name_match
    args_parsed = parse_arguments(args)
    if not os.path.isdir(os.environ.get('FEATURES_PATH')):
        print('\n"features" folder was not found in current path...')
        exit()
    set_environ_config(args_parsed)
    ConfigRun().set_args(args_parsed)
    _set_env_variables(args_parsed)
    execution_code = setup_running_failures(args_parsed)
    if execution_code == EXIT_ERROR:
        return EXIT_ERROR
    set_system_paths()

    cleanup_folders()
    copy_bootstrap_html_generator()
    configure_logging(args_parsed)
    check_environment_file()
    match_include = MatchInclude()
    include_path_match = IncludePathsMatch()
    include_name_match = IncludeNameMatch()

    return launch_behavex()


def setup_running_failures(args_parsed):
    """
    Set the variable INCLUDE_PATHS with output set on failures.txt
      if the variable RUN_FAILURES is set to True.

    :param args_parsed:
    :return: EXIT_OK|EXIT_ERROR
    """
    if args_parsed.run_failures:
        set_env_variable('RUN_FAILURES', args_parsed.run_failures)
        failures_path = os.path.join(get_env('OUTPUT'), 'failures.txt')

        if not os.path.exists(failures_path):
            print('\nThere are no failing test scenarios to run.')
            return EXIT_ERROR
        with open(failures_path, 'r') as failures_file:
            content = failures_file.read()
            if not content:
                print('\nThere are no failing test scenarios to run.')
                return EXIT_ERROR
            set_env_variable('INCLUDE_PATHS', content.split())
            return EXIT_OK


def launch_behavex():
    """Launch the BehaveX test execution in the specified parallel mode."""
    json_reports = None
    execution_codes = None
    time_init = time.time()
    features_path = os.environ.get('FEATURES_PATH')
    parallel_element = get_param('parallel_element')
    parallel_processes = get_param('parallel_processes')
    multiprocess = True if get_param('parallel_processes') > 1 else False
    if not multiprocess:
        parallel_element = ''
    set_behave_tags()
    scenario = False
    notify_missing_features()
    features_list = explore_features(features_path)
    create_scenario_line_references(features_list)
    process_pool = lib_multiprocessing.Pool(parallel_processes)
    if parallel_processes == 1:
        # when it is not multiprocessing
        if get_param('dry_run'):
            print('Obtaining information about the reporting scope...')
        execution_codes, json_reports = execute_tests(
            [True], multiprocessing=False, config=ConfigRun()
        )
    elif parallel_element == 'scenario':
        execution_codes, json_reports = launch_by_scenario(features_list, process_pool)
        scenario = True
    elif parallel_element == 'feature':
        execution_codes, json_reports = launch_by_feature(features_list, process_pool)
    wrap_up_process_pools(process_pool, json_reports, multiprocess, scenario)
    time_end = time.time()

    if get_param('dry_run'):
        msg = '\nDry run completed. Please, see the report in {0}' ' folder.\n\n'
        print(msg.format(get_env('OUTPUT')))
    if multiprocess:
        print_parallel(
            '\nTotal execution time: {}'.format(
                pretty_print_time(time_end - time_init)
            ),
            no_chain=True,
        )

    remove_temporary_files(parallel_processes)

    results = get_json_results()
    failing_non_muted_tests = False
    if results:
        failures = {}
        for feature in results['features']:
            if feature['status'] == 'failed':
                filename = feature['filename']
                failures[filename] = []
            else:
                continue
            for scenario in feature['scenarios']:
                if scenario['status'] == 'failed':
                    failures[filename].append(scenario['name'])
                    if 'MUTE' not in scenario['tags']:
                        failing_non_muted_tests = True
        if failures:
            failures_file_path = os.path.join(get_env('OUTPUT'), 'failures.txt')
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
    print('Exit code: {}'.format(exit_code))
    return exit_code


def notify_missing_features():
    """
    Print the paths of .feature files that do not exist.
    """
    include_paths = get_env('include_paths', [])
    for path in include_paths:
        include_path = path.partition(':')[0]
        if not os.path.exists(os.path.normpath(include_path)):
            print_parallel('path.not_found', os.path.realpath(include_path))


def create_test_list(test_list):
    """
    :param test_list:
    :return: Dictionary containing the feature paths
            and line number of scenarios to run again
    """
    paths = []
    sce_lines = get_env('scenario_lines')
    for feature, scenarios in test_list.items():
        for scenario_name in scenarios:
            paths.append('{}:{}'.format(feature, sce_lines[feature][scenario_name]))
    return ' '.join(paths)


def create_scenario_line_references(features):
    """
    create a dictionary with name scenario as key and the value content the first number
    line where  the scenario is defined. this result will is stored a global
    variable scenario_lines

    :param features: The json with information of the results execution
    :return: None
    """
    sce_lines = {}
    for feature in features:
        sce_lines[text(feature.filename)] = {}
        feature_lines = sce_lines[text(feature.filename)]
        for scenario in feature.scenarios:
            if scenario.keyword == u'Scenario':
                feature_lines[scenario.name] = scenario.line
            else:
                for scenario_multiline in scenario.scenarios:
                    feature_lines[scenario_multiline.name] = scenario_multiline.line
    set_env('scenario_lines', sce_lines)


def launch_by_feature(features, process_pool):
    """
    Split the test execution in multiple behave instances (processes) to
    generate_gallery parallel test executions.
    In this case, parallelism is performed at feature level, meaning that each
    parallel behave instance will pick up a feature, and the scenarios in
    each feature file will be executed sequentially
    :param features: List containing all features
    :param process_pool: The process pool
    :return: json with json executions
    """
    json_reports = []
    execution_codes = []
    serial = [feature.filename for feature in features if 'SERIAL' in feature.tags]

    features_dict = {
        feature.filename: feature
        for feature in features
        if feature.filename not in serial
    }
    if serial:
        print_parallel('feature.serial_execution')
        execution_code, map_json = execute_tests(serial, config=ConfigRun())
        json_reports += [map_json]
        execution_codes.append(execution_code)

    print_parallel('feature.running_parallels')

    for filename in features_dict.items():

        process_pool.apply_async(
            execute_tests,
            ([filename], None, True, ConfigRun()),
            callback=create_partial_function_append(execution_codes, json_reports),
        )

    return execution_codes, json_reports


def launch_by_scenario(features, process_pool):
    """
    Split the test execution in multiple behave instances (processes) to
    generate_gallery parallel test executions.
    In this case, parallelism is performed at scenario level, meaning that each
    parallel behave instance will pick up a scenario and execute it.
    As soon as the execution finishes, another scenario will be picked up to run
    :param features: List containing all features
    :param process_pool: The process pool
    :return: json with json executions
    """
    serial_scenarios = []
    json_reports = []
    filenames = []
    execution_codes = []

    for feature in features:
        for scenario in feature.scenarios:
            if include_path_match(
                feature.filename, scenario.line
            ) and include_name_match(scenario.name):
                scenario.tags += feature.tags
                if 'SERIAL' in scenario.tags:
                    serial_scenarios.append((feature.filename, scenario.name))
                else:
                    filenames.append(([feature.filename], scenario.name))
    if serial_scenarios:
        print_parallel('scenario.serial_execution')
        json_serial_reports = [
            execute_tests([feature], scenario, config=ConfigRun())
            for feature, scenario in serial_scenarios
        ]
        # execution_codes and json_reports are forced to be lists now.
        execution_codes += list(map(itemgetter(0), json_serial_reports))
        json_reports += list(map(itemgetter(1), json_serial_reports))

    print_parallel('scenario.running_parallels')
    for filename, scenario_name in filenames:
        process_pool.apply_async(
            execute_tests,
            (filename, scenario_name, True, ConfigRun()),
            callback=create_partial_function_append(execution_codes, json_reports),
        )

    return execution_codes, json_reports


def execute_tests(list_features, scenario=None, multiprocessing=True, config=None):
    """
    Trigger one process with behave
    :param list_features: List of the feature
    :param scenario: if the parallel-element is scenario
    :param multiprocessing: if is running in parallel
    :param config: configuration file

    :return:
    """
    args = None
    json_reports = []
    paths = config.get_env('include_paths', [])
    execution_codes, generate_report = [], False
    if multiprocessing:
        Singleton._instances[ConfigRun] = config
    for feature in list_features:
        try:
            args = _set_behave_arguments(
                multiprocessing, feature, scenario, paths, config
            )
        except Exception as exception:
            traceback.print_exc()
            print(exception)
        execution_codes, generate_report = _launch_behave(args)
        if generate_report:
            json_output = dump_json_results()
        else:
            json_output = {'environment': [], 'features': [], 'steps_definition': []}
        if scenario:
            json_output['features'] = filter_feature_executed(
                json_output, text(list_features[0]), scenario
            )
            try:
                processing_xml_feature(json_output, scenario)
            except Exception as ex:
                logging.exception(ex)
        json_reports.append(json_output)

    return execution_codes, join_feature_reports(json_reports)


def filter_feature_executed(json_output, filename, scenario_name):
    """
    Filter the info feature about that is executed and delete the others features.

    :param json_output:
    :param filename:
    :param scenario_name:
    :return:
    """
    for feature in json_output.get('features', '')[:]:
        if feature.get('filename', '') == filename:
            mapping_scenarios = []
            for scenario in feature['scenarios']:
                pattern = re.compile('{}(.--.@\\d+.\\d+)?'.format(scenario_name))
                if pattern.match(scenario['name']):
                    mapping_scenarios.append(scenario)
            feature['scenarios'] = mapping_scenarios
            return [feature]


def _launch_behave(args):
    """
    Run the test cases using Behave testing framework.
    Configuration is passed through command line parameters.
    :param args: string list for passing to behave
    :return:
    """
    # Save tags configuration to report only selected scenarios
    # Check for tags in config file
    generate_report = True
    execution_code = 0
    try:
        behave_script.main(args)
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
    """
    Close process pool and generate_gallery outputs
    :param process_pool: process pool
    :param json_reports: list of the json that result of the execution
    :param multi_process: Boolean indicating if execution is running in parallel
    :param scenario: True or False if the param element is scenario
    :return: None
    """
    merged_json = None
    output = os.path.join(get_env('OUTPUT'))
    try:
        if multi_process:
            process_pool.close()
            process_pool.join()
            if scenario:
                json_reports = join_scenario_reports(json_reports)
            merged_json = join_feature_reports(json_reports)
        else:
            merged_json = json_reports
    except KeyboardInterrupt:
        process_pool.terminate()
        process_pool.join()
    status_info = os.path.join(output, OVERALL_STATUS_FILE)

    with open(status_info, 'w') as file_info:
        over_status = {'status': get_overall_status(merged_json)}
        file_info.write(json.dumps(over_status))
    path_info = os.path.join(output, 'report.json')
    if get_env('include_paths'):
        filter_by_paths(merged_json)
    with open(path_info, 'w') as file_info:
        file_info.write(json.dumps(merged_json))
    if get_param('dry_run'):
        print('Generating outputs...')
    generate_reports(merged_json)


def filter_by_paths(merged_json_reports):
    """
    filter information about features that has executed.

    :param merged_json_reports:
    :return: None
    """
    sce_lines = get_env('scenario_lines')
    if not sce_lines:
        return
    for feature in merged_json_reports['features']:
        filters = []
        for index, scenario in enumerate(feature['scenarios'][:]):
            line = sce_lines[feature['filename']][scenario['name']]
            if (
                (
                    IncludePathsMatch()(feature['filename'], line)
                    and MatchInclude()(feature['filename'])
                )
                and match_for_execution(scenario['tags'])
                and IncludeNameMatch()(scenario['name'])
            ):
                filters.append(index)
        feature['scenarios'] = [
            scenario
            for index, scenario in enumerate(feature['scenarios'])
            if index in filters
        ]
        merged_json_reports['features'] = [
            feature
            for feature in merged_json_reports['features']
            if feature['scenarios']
        ]


def remove_temporary_files(parallel_processes):
    """
    Remove files generated for multiprocessing
    :param parallel_processes: quantity of processes
    """
    path_info = os.path.join(os.path.join(get_env('OUTPUT'), 'report.json'))
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

    name = lib_multiprocessing.current_process().name.split('-')[-1]
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


def processing_xml_feature(json_output, scenario):
    """
    Processing json to generate_gallery an xml per feature when execution is completed
    :param json_output: The output json of the partial feature execution
    :param scenario: The scenario name to process
    :return:
    """
    if json_output['features'] and 'scenarios' in json_output['features'][0]:

        scenarios_old = json_output['features'][0]['scenarios']
        scenario_executed = [
            scen
            for scen in scenarios_old
            if scen['name'] == scenario
            or (scen['name'].startswith(scenario) and '@' in scen['name'])
        ]
        json_output['features'][0]['scenarios'] = scenario_executed
        feature_name = os.path.join(
            get_env('OUTPUT'), u'{}.tmp'.format(json_output['features'][0]['name'])
        )
        feature_old = json_output['features'][0]
        feature_old['scenarios'] = scenario_executed
        if os.path.exists(feature_name):
            for _ in range(0, 10):
                try:
                    feature_old = json.load(open(feature_name, 'r'))
                    with open(feature_name, 'w') as feature_file:
                        for scen in scenario_executed:
                            feature_old['scenarios'].append(scen)
                        json.dump(feature_old, feature_file)
                    break
                except Exception as ex:
                    logging.debug(ex)
                    logging.debug('Retrying reading from {}'.format(feature_name))
                    time.sleep(1)
        else:
            with codecs.open(feature_name, 'w', 'utf8') as feature_file:
                # feature_old['scenarios'] = scenarios_old
                json.dump(feature_old, feature_file)
        # We calculate the quantity of the scenario that should executing
        scenarios_total = len_scenarios(feature_old['filename'])
        if len(feature_old['scenarios']) == scenarios_total:
            try:
                report_xml.export_feature_to_xml(feature_old, False)
            except Exception as ex:
                traceback.print_exc()
                print(ex)
            finally:
                path_tmp = u'{}.tmp'.format(feature_name[:-4])
                os.remove(path_tmp)


def _set_env_variables(args):
    """Setting arguments as environment variables, in order to
        use them when executing actions in a separate process.
        Also, CONFIG env variable is set in init module, as it
        is used when initializing several framework modules
         :param args: the args provider from console
    :param args: the args parsing
    :return:
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
        if platform.system() == 'Windows':
            set_env_variable(
                'INCLUDE', json.dumps(get_param('include').replace('/', '\\'))
            )
        else:
            set_env_variable('INCLUDE', get_param('include'))
    if get_param('include'):
        set_env_variable('INCLUDE', json.loads(get_param('include')))
    if get_param('name'):
        set_env_variable('NAME', args.name)
    for arg in BEHAVEX_ARGS[4:]:
        set_env_variable(arg.upper(), get_param(arg))

    set_env_variable('TEMP', os.path.join(get_env('output'), 'temp'))
    set_env_variable('LOGS', os.path.join(get_env('output'), 'outputs', 'logs'))
    if get_param('logging_level'):
        set_env_variable('logging_level', get_param('logging_level'))
    if platform.system() == 'Windows':
        set_env_variable('HOME', os.path.abspath('.\\'))
    set_env_variable('DRY_RUN', get_param('dry_run'))
    print_env_variables(
        [
            'HOME',
            'CONFIG',
            'OUTPUT',
            'TAGS',
            'PARALLEL_ELEMENT',
            'PARALLEL_PROCESSES',
            'TEMP',
            'LOGS',
            'LOGGING_LEVEL',
        ]
    )


def _store_tags_to_env_variable(tags):
    """
    Process execution tags and store them into an environment variable
    :param tags: Execution tags list
    :return:
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
        # TODO: review this logic
        for tag in tags:
            if get_param('tags'):
                set_env_variable('TAGS', ';'.join(get_param('tags')) + ';' + tag)
            else:
                set_env_variable('TAGS', tag)
    else:
        set_env_variable('TAGS', '')


def _set_behave_arguments(
    multiprocessing, feature=None, scenario=None, paths=None, config=None
):
    """
    Recreate command line arguments in order to
    call behave framework with the expected values
    :param multiprocessing: if the mode is in parallel
    :param feature: The specific feature to run if parallel element is feature
     or scenario
    :param scenario: The specific name of the scenario if parallel element is
     scenario
    :return:
    """
    arguments = []
    output_folder = config.get_env('OUTPUT')
    if multiprocessing:
        arguments.append(feature)
        arguments.append('--no-summary')
        if scenario:
            arguments.append('--name')
            arguments.append('{}(.?--.?@\\d*.\\d*\\s*)?$'.format(scenario))
        name = lib_multiprocessing.current_process().name.split('-')[-1]
        arguments.append('--outfile')
        arguments.append(os.path.join(gettempdir(), 'stdout{}.txt'.format(name)))
    else:
        set_paths_argument(arguments, paths)
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
            if multiprocessing or not value_arg:
                continue
            else:
                features_path = os.path.abspath(os.environ['FEATURES_PATH'])
                value_arg = value_arg.replace(features_path, 'features').replace(
                    '\\', '\\\\'
                )
        if arg == 'define':
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


def set_args_captures(args, args_sys):
    """
    Set the arguments related with capture outputs arguments.

    :param args:
    :param args_sys:
    :return:
    """
    for default_arg in ['capture', 'capture_stderr', 'logcapture']:
        if not getattr(args_sys, 'no_{}'.format(default_arg)):
            args.append('--no-{}'.format(default_arg.replace('_', '-')))


def set_paths_argument(args, paths):
    """
    Set args iterating with the values of paths

    :param args:
    :param paths:
    :return: None
    """
    if paths:
        for path in paths:
            args.append(os.path.realpath(path))


def dump_json_results():
    """ Do reporting. """
    if lib_multiprocessing.current_process().name == 'MainProcess':
        path_info = os.path.join(os.path.abspath(get_env('OUTPUT')), 'report.json')
    else:
        process_name = lib_multiprocessing.current_process().name.split('-')[-1]
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

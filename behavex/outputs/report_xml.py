# -*- coding: utf-8 -*-
"""
/*
* BehaveX - Production-grade test orchestration for Python BDD.
*/
"""
# __future__ has been added in order to maintain compatibility
from __future__ import absolute_import

import codecs
import json
import logging
import os
import re
import time
import traceback
from multiprocessing.managers import DictProxy

try:
    from behave.model_core import Status
except ImportError:
    from behave.model import Status



from behavex.conf_mgr import get_env, get_param
from behavex.global_vars import global_vars
from behavex.outputs.jinja_mgr import TemplateHandler
from behavex.outputs.report_utils import (get_save_function, get_string_hash,
                                          match_for_execution,
                                          retry_file_operation,
                                          status_with_hook_errors_as_error, text)
from behavex.utils import get_all_feature_scenarios, get_scenario_tags, len_scenarios


def generate_junit_xml_filename(filename):
    """Generate JUnit XML report filename from feature file path.

    Args:
        filename (str): Path to the feature file

    Returns:
        str: JUnit XML filename in format TESTS-<name>.xml
    """
    if not filename:
        return 'TESTS-default.xml'

    # Normalize path for the current OS and replace backslashes for consistency
    normalized_path = os.path.normpath(filename).replace('\\', '/')
    path_parts = normalized_path.split('/')

    # Find 'features' directory
    if 'features' in path_parts:
        features_idx = path_parts.index('features')
        # Use everything after 'features'
        name_parts = path_parts[features_idx + 1:]
    else:
        # Fallback: use all parts but filter out empty ones and drive letters
        name_parts = [part for part in path_parts if part and ':' not in part]

    # Remove .feature extension from the last part
    if name_parts and name_parts[-1].endswith('.feature'):
        name_parts[-1] = name_parts[-1][:-8]  # Remove '.feature'

    # Join with dots, filter out empty parts
    name = '.'.join(part for part in name_parts if part)

    return f'TESTS-{name or "default"}.xml'


def _export_feature_to_xml(feature, isobject=True):
    def get_scenarios(feature_):
        def flatter_scenarios(scenarios_list):
            return sum(
                (
                    [scenario] if scenario.type == 'scenario' else scenario._scenarios
                    for scenario in scenarios_list
                ),
                [],
            )
        scenarios = flatter_scenarios(get_all_feature_scenarios(feature_)) if isobject else feature_['scenarios']
        return scenarios

    def get_status(scenario_):
        if hasattr(scenario_, 'status'):
            if status_with_hook_errors_as_error(scenario_.status.name) == 'error':
                return Status.failed
            return scenario_.status
        else:
            status = scenario_['status']
            if 'untested' in status:
                return Status.untested
            elif 'failed' in status:
                return Status.failed
            elif 'error' in status:
                return Status.failed  # Treat error scenarios as failed for XML reports
            elif 'skipped' in status:
                return Status.skipped
            elif 'passed' in status:
                return Status.passed
            else:
                return Status.skipped  # Default fallback for unrecognized statuses

    scenarios = [
        scenario
        for scenario in get_scenarios(feature)
        if (match_for_execution(get_scenario_tags(scenario)) and not (get_status(scenario) == Status.skipped and get_env('RERUN_FAILURES')))
    ]

    skipped = [scenario for scenario in scenarios if get_status(scenario) == Status.skipped]
    failures = [
        scenario
        for scenario in scenarios
        if get_status(scenario) == Status.failed or get_status(scenario) == Status.untested
    ]
    muted = [
        scenario
        for scenario in scenarios
        if any(i in ['MUTE'] for i in get_scenario_tags(scenario))
    ]

    muted_failed = [scenario for scenario in muted if get_status(scenario) == Status.failed]

    summary = {
        'time': sum(
            scenario.duration if isobject else scenario['duration']
            for scenario in scenarios
        ),
        'tests': len(scenarios),
        'failures': len(failures) - len(muted_failed),
        'skipped': len(skipped) + len(muted_failed),
    }
    parameters_template = {
        'feature': feature,
        'summary': summary,
        'skipped': skipped,
        'failures': failures,
        'scenarios': scenarios,
        'muted': muted_failed,
    }

    template_handler = TemplateHandler(global_vars.jinja_templates_path)
    output_text = template_handler.render_template(
        global_vars.jinja_templates['xml']
        if isobject
        else global_vars.jinja_templates['xml_json'],
        parameters_template,
    )
    output_text = output_text.replace('status="Status.', 'status="')

    filename = feature.filename if isobject else feature['filename']
    filename = text(filename)

    # Generate XML filename using the helper function
    xml_filename = generate_junit_xml_filename(filename)

    junit_path = os.path.join(get_env('OUTPUT'), 'behave')

    path_output = os.path.join(junit_path, xml_filename)

    retry_file_operation(
        path_output, get_save_function(path_output, output_text)
    )


def export_feature_to_xml(feature, isobject=True):
    _export_feature_to_xml(feature, isobject)


def get_feature_results_tmp_file_path(feature_filename):
    feature_tmp_dir = get_env('TEMP') if get_param('no_report') else get_env('OUTPUT')
    return os.path.join(feature_tmp_dir, u'{}.tmp'.format(get_string_hash(os.path.abspath(feature_filename))))


def processing_xml_feature(json_output, scenario_line, feature_filename,
                           scenarios_to_run_in_feature=None, lock=None,
                           shared_removed_scenarios=None):
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
                if reported_scenario['line'] == scenario_line:
                    executed_scenarios.append(reported_scenario)
            json_output['features'][0]['scenarios'] = executed_scenarios
            feature_tmp_file_path = get_feature_results_tmp_file_path(feature_filename)
            processed_feature_data = json_output['features'][0]
            processed_feature_data['scenarios'] = executed_scenarios
            if os.path.exists(feature_tmp_file_path):
                for _ in range(0, 10):
                    try:
                        processed_feature_data = json.load(open(feature_tmp_file_path, 'r'))
                        with open(feature_tmp_file_path, 'w') as feature_file:
                            for executed_scenario in executed_scenarios:
                                processed_feature_data['scenarios'].append(executed_scenario)
                            json.dump(processed_feature_data, feature_file)
                        break
                    except Exception as ex:
                        logging.debug(ex)
                        logging.debug('Retrying reading from {}'.format(feature_tmp_file_path))
                        time.sleep(1)
            else:
                with codecs.open(feature_tmp_file_path, 'w', 'utf8') as feature_file:
                    json.dump(processed_feature_data, feature_file)
            # calculate the total number of scenarios that should be executed
            removed_scenarios = 0
            if shared_removed_scenarios and feature_filename in shared_removed_scenarios:
                removed_scenarios = shared_removed_scenarios[feature_filename]
            if scenarios_to_run_in_feature is None:
                total_scenarios = len_scenarios(feature_filename) - removed_scenarios
            else:
                total_scenarios = scenarios_to_run_in_feature - removed_scenarios
            if len(processed_feature_data['scenarios']) == total_scenarios:
                try:
                    if not get_param('no_report'):
                        export_feature_to_xml(processed_feature_data, False)
                except Exception as ex:
                    traceback.print_exc()
                    print(ex)
                finally:
                    os.remove(feature_tmp_file_path)
    finally:
        if lock:
            lock.release()

# -*- coding: utf-8 -*-
"""
/*
* BehaveX - Agile test wrapper on top of Behave (BDD)
*/
"""
# __future__ has been added in order to maintain compatibility
from __future__ import absolute_import

import os
import re

from behave.model_core import Status

from behavex.conf_mgr import get_env
from behavex.global_vars import global_vars
from behavex.outputs.jinja_mgr import TemplateHandler
from behavex.outputs.report_utils import (get_save_function,
                                          match_for_execution,
                                          retry_file_operation, text)
from behavex.utils import get_scenario_tags


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
        scenarios = flatter_scenarios(feature_.scenarios) if isobject else feature_['scenarios']
        return scenarios

    def get_status(scenario_):
        if hasattr(scenario_, 'status'):
            return scenario_.status
        else:
            status = scenario_['status']
            if 'untested' in status:
                return Status.untested
            elif 'failed' in status:
                return Status.failed
            elif 'skipped' in status:
                return Status.skipped
            elif 'passed' in status:
                return Status.passed

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
    exp = re.compile('\\\\|/')
    filename = feature.filename if isobject else feature['filename']
    filename = text(filename)
    name = u'.'.join(exp.split(filename.partition('features')[2][1:-8]))
    junit_path = os.path.join(get_env('OUTPUT'), 'behave')
    path_output = os.path.join(junit_path, u'TESTS-' + name + u'.xml')

    retry_file_operation(
        path_output + '.xml', get_save_function(path_output, output_text)
    )


def export_feature_to_xml(feature, isobject=True):
    _export_feature_to_xml(feature, isobject)

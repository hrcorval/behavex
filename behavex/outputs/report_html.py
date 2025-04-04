# -*- coding: utf-8 -*-
"""
/*
* BehaveX - Agile test wrapper on top of Behave (BDD)
*/
"""
from __future__ import absolute_import

import os
import time
from collections import OrderedDict

import csscompressor
import minify_html

from behavex.conf_mgr import get_env
from behavex.global_vars import global_vars
from behavex.outputs.jinja_mgr import TemplateHandler
from behavex.outputs.report_utils import (gather_steps_with_definition,
                                          get_environment_details,
                                          get_save_function,
                                          retry_file_operation)


def generate_report(output, joined=None, report=None):
    environment_details = get_environment_details()
    features = output['features']
    steps_definition = output['steps_definition']
    all_scenarios = sum((feature['scenarios'] for feature in features), [])
    features.sort(key=lambda feature: feature['name'])
    metrics_variables = get_metrics_variables(all_scenarios)
    html = export_result_to_html(
        environment_details, features, metrics_variables, steps_definition, joined, report
    )
    content_to_file = {'report.html': html}
    _create_files_report(content_to_file)


def _create_manifest(relative, page):
    parameters_template = {'relative': relative, 'page': page}
    template_handler = TemplateHandler(global_vars.jinja_templates_path)
    output_text = template_handler.render_template(
        global_vars.jinja_templates['manifest'], parameters_template
    )
    folder = os.path.join(get_env('OUTPUT'), 'outputs', 'bootstrap', 'manifest')
    if not os.path.exists(folder):
        os.makedirs(folder)
    file_manifest = os.path.join(folder, page.replace('html', 'manifest'))

    retry_file_operation(
        file_manifest, execution=get_save_function(file_manifest, output_text)
    )


def _create_files_report(content_to_file):
    for name_file, content in content_to_file.items():
        if name_file == 'report.html':
            layout_path = os.path.join(
                os.path.dirname(__file__),
                'bootstrap',
                'css',
                'behavex.css',
            )
            layout_file = open(layout_path, 'r')
            layout_min_path = os.path.join(
                get_env('OUTPUT'), 'outputs', 'bootstrap', 'css', 'behavex.min.css'
            )
            _create_manifest('../', name_file)
            with open(layout_min_path, 'w') as layout_min:
                layout_min.write(csscompressor.compress(layout_file.read()))
            path_file = os.path.join(get_env('OUTPUT'), name_file)
        else:
            path_file = os.path.join(get_env('OUTPUT'), 'outputs', name_file)
            _create_manifest('', name_file)
        try:
            content = minify_html.minify(
                content,
                allow_noncompliant_unquoted_attribute_values=True,
                allow_optimal_entities=True,
                allow_removing_spaces_between_attributes=True,

                # Keep structure intact
                keep_closing_tags=False,
                keep_comments=False,
                keep_html_and_head_opening_tags=False,
                keep_input_type_text_attr=False,
                keep_ssi_comments=False,

                # Don't minify any code
                minify_css=True,
                minify_doctype=True,
                # minify_js=True,

                # Preserve template syntax
                preserve_brace_template_syntax=False,
                preserve_chevron_percent_template_syntax=False,

                # Don't remove any important structural elements
                remove_bangs=True,
                remove_processing_instructions=True
            )
        # pylint: disable= W0703
        except Exception as ex:
            print(ex)
        retry_file_operation(path_file, get_save_function(path_file, content))


def get_metrics_variables(scenarios):
    skipped = sum(
        scenario['status'] not in ['passed', 'failed'] for scenario in scenarios
    )
    passed = sum(scenario['status'] == 'passed' for scenario in scenarios)
    failed = sum(scenario['status'] == 'failed' for scenario in scenarios)
    scenario_auto = [
        scenario
        for scenario in scenarios
        if not ('MANUAL' in scenario['tags'] or 'WIP' in scenario['tags'])
    ]

    muted = [
        scenario
        for scenario in scenarios
        if any(i in ['MUTE'] for i in scenario['tags'])
        and scenario['status'] == 'failed'
    ]
    parameters_template = {
        'skipped': skipped,
        'passed': passed,
        'failed': failed,
        'not_automated': len(scenarios) - len(scenario_auto),
        'total': len(scenarios) or 1,
        'muted': len(muted),
    }
    return parameters_template


def export_result_to_html(
    environment_details, features, metrics_variables, steps_definition, joined=None, report=None
):
    totals, summary = export_to_html_table_summary(features)
    tags, scenarios = get_value_filters(features)
    steps_summary = gather_steps_with_definition(features, steps_definition)
    execution_start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(global_vars.execution_start_time))
    execution_end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(global_vars.execution_end_time))
    parameters_template = {
        'features': features,
        'steps': steps_summary,
        'fields_total': totals,
        'summary': summary,
        'joined': joined,
        'report': report,
        'tags': list(tags),
        'scenarios': scenarios,
        'execution_details': {'parallel_processes': os.getenv('PARALLEL_PROCESSES', '1'),
                              'parallel_scheme': os.getenv('PARALLEL_SCHEME', 'scenario')},
        'environment_details': environment_details,
        'execution_times': {'execution_start_time': execution_start_time,
                            'execution_end_time': execution_end_time,
                            'total_execution_time': global_vars.execution_end_time - global_vars.execution_start_time}
    }
    parameters_template.update(metrics_variables)
    template_handler = TemplateHandler(global_vars.jinja_templates_path)
    output_text = template_handler.render_template(
        global_vars.jinja_templates['main'], parameters_template
    )
    return output_text


def get_value_filters(features):
    tags = {
        tag
        for feature in features
        for scenario in feature['scenarios']
        for tag in scenario['tags']
    }

    scenarios = [
        (scenario['name'], '{}-{}'.format(feature['id'], scenario['id_hash']))
        for feature in features
        for scenario in feature['scenarios']
    ]

    return tags, scenarios


def export_to_html_table_summary(features):
    list_fields = [
        'Feature',
        'Total',
        'Executed',
        'Passed',
        'Failed',
        'Skipped',
        'Execution Status',
        'Pass Rate',
        'Duration',
    ]

    tuples_fields = [(field, 0) for field in list_fields]
    fields = OrderedDict(tuples_fields)
    fields_total = OrderedDict([('Totals', 'Totals')] + tuples_fields[1:])

    summary = {}
    for feature in features:
        fields.update({field: 0 for field in list_fields[1:6]})
        muted = 0
        for scenario in feature['scenarios']:
            fields['Total'] += 1
            if any(i in ['MUTE'] for i in scenario['tags']):
                muted += 1
            if scenario['status'] == 'passed':
                fields['Executed'] += 1
                fields['Passed'] += 1
            elif scenario['status'] == 'failed':
                fields['Executed'] += 1
                fields['Failed'] += 1
            else:
                fields['Skipped'] += 1

        fields_total.update(
            {field: fields_total[field] + fields[field] for field in list_fields[1:6]}
        )

        fields_total['Duration'] += feature['duration']
        if fields['Total'] == 0:
            fields['Total'] = 1

        fields['Execution Status'] = '%.2f' % (
            (float(fields['Executed']) / fields['Total']) * 100
        )

        fields['Pass Rate'] = '%.2f' % (
            (float(fields['Passed']) / fields['Total']) * 100
        )

        fields['Duration'] = feature['duration']
        summary[feature['name']] = fields.copy()
        summary[feature['name']]['muted'] = muted

    if len(features) > 0 and fields_total['Total'] > 0:
        fields_total['Execution Status'] = '%.2f' % (
            (float(fields_total['Executed']) / fields_total['Total']) * 100
        )

        fields_total['Pass Rate'] = '%.2f' % (
            (float(fields_total['Passed']) / fields_total['Total']) * 100
        )

    return fields_total, summary

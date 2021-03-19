# -*- encoding: utf-8 -*
"""
/*
* BehaveX - Agile test wrapper on top of Behave (BDD)
*/

Then module generate_gallery the files for report in html format.

VARIABLES:
    - MANIFEST_TEMPLATE
    - FWK_DIR
    - TEMPLATE_DIR
    - CONFIG
    - TEST_REPORT_TEMPLATE
    - STEP_TEMPLATE_DEFINITION
    - METRICS_TEMPLATE
    - TAGS_TEMPLATE
    - T_HANDLER

FUNCTIONS:
    - generate_report
    - _create_manifest
    - _create_files_report
    - export_step_to_html
    - export_result_to_html
    - get_value_filters
    - export_to_html_table_summary
"""
# __future__ has been added in order to maintain compatibility
from __future__ import absolute_import

import os
from collections import OrderedDict

import csscompressor
import htmlmin

from behavex import conf_mgr
from behavex.conf_mgr import get_env
from behavex.reports.report_utils import (
    gather_steps_with_definition,
    get_save_function,
    get_total_steps,
    try_operate_descriptor,
)
from behavex.reports.template_handler import TemplateHandler

MANIFEST_TEMPLATE = "manifest.jinja2"

FWK_DIR = os.environ.get("BEHAVEX_PATH")
TEMPLATE_DIR = os.path.join(FWK_DIR, "reports", "templates")
CONFIG = conf_mgr.get_config()

TEST_REPORT_TEMPLATE = "report.jinja2"
STEP_TEMPLATE_DEFINITION = "steps.jinja2"
T_HANDLER = TemplateHandler(TEMPLATE_DIR)


def generate_report(output, joined=None, report=None):
    """Generate reports in html format"""
    environment = output["environment"]
    features = output["features"]
    steps_definition = output["steps_definition"]
    all_scenarios = sum((feature["scenarios"] for feature in features), [])
    features.sort(key=lambda feature: feature["name"])
    metrics_variables = get_metrics_variables(all_scenarios, joined, report)
    html = export_result_to_html(
        environment, features, metrics_variables, joined, report
    )
    step = export_step_to_html(features, steps_definition, joined, report)
    content_to_file = {"report.html": html, "steps.html": step}
    _create_files_report(content_to_file)


def _create_manifest(relative, page):
    """Create file manifest from template"""
    parameters_template = {"relative": relative, "page": page}
    output_text = T_HANDLER.render_template(MANIFEST_TEMPLATE, parameters_template)
    folder = os.path.join(get_env("OUTPUT"), "reports", "bootstrap", "manifest")
    if not os.path.exists(folder):
        os.makedirs(folder)
    file_manifest = os.path.join(folder, page.replace("html", "manifest"))

    try_operate_descriptor(
        file_manifest, execution=get_save_function(file_manifest, output_text)
    )


def _create_files_report(content_to_file):
    """Create files for report html"""
    for name_file, content in content_to_file.items():
        if name_file == "report.html":
            layout_path = os.path.join(
                os.path.dirname(__file__),
                "utils/bootstrap-3.3.7-dist",
                "css",
                "layout.css",
            )
            layout_file = open(layout_path, "r")
            layout_min_path = os.path.join(
                get_env("OUTPUT"), "reports", "bootstrap", "css", "layout.min.css"
            )
            _create_manifest("../", name_file)
            with open(layout_min_path, "w") as layout_min:
                layout_min.write(csscompressor.compress(layout_file.read()))
            path_file = os.path.join(get_env("OUTPUT"), name_file)

        else:
            path_file = os.path.join(get_env("OUTPUT"), "reports", name_file)
            _create_manifest("", name_file)
        try:
            content = htmlmin.minify(
                input=content,
                remove_comments=False,
                remove_empty_space=False,
                remove_all_empty_space=False,
                reduce_empty_attributes=True,
                reduce_boolean_attributes=False,
                remove_optional_attribute_quotes=True,
                keep_pre=False,
                pre_tags=(u"pre", u"textarea"),
                pre_attr="pre",
            )
        # pylint: disable= W0703
        except Exception as ex:
            print(ex)
        try_operate_descriptor(path_file, get_save_function(path_file, content))


def get_metrics_variables(scenarios, joined=None, report=None):
    """Processing variable for generating metrics in charts"""
    skipped = sum(
        scenario["status"] not in ["passed", "failed"] for scenario in scenarios
    )
    passed = sum(scenario["status"] == "passed" for scenario in scenarios)
    failed = sum(scenario["status"] == "failed" for scenario in scenarios)
    scenario_auto = [
        scenario
        for scenario in scenarios
        if not ("MANUAL" in scenario["tags"] or "WIP" in scenario["tags"])
    ]

    to_be_fixed = [
        scenario
        for scenario in scenarios
        if any(i in ["TEST_TO_FIX", "BUG_TO_FIX"] for i in scenario["tags"])
        and scenario["status"] == "failed"
    ]
    parameters_template = {
        "skipped": skipped,
        "passed": passed,
        "failed": failed,
        "not_automated": len(scenarios) - len(scenario_auto),
        "total": len(scenarios) or 1,
        "to_be_fixed": len(to_be_fixed),
    }
    return parameters_template


def export_step_to_html(features, steps_definition=None, joined=None, report=None):
    """Generate file steps.html with step of the all scenarios"""
    steps_summary = gather_steps_with_definition(features, steps_definition)
    total = get_total_steps(steps_summary)

    # steps_summary.keys() has been forced to be list type
    parameter_template = {
        "steps": steps_summary,
        "steps_sorted": sorted(list(steps_summary.keys()), key=lambda x: x.lower()),
        "joined": joined,
        "report": report,
        "total": total,
    }

    output_text = T_HANDLER.render_template(
        STEP_TEMPLATE_DEFINITION, parameter_template
    )

    return output_text


def export_result_to_html(
    environment, features, metrics_variables, joined=None, report=None
):
    """Create test_result.html file with feature information"""
    totals, summary = export_to_html_table_summary(features)
    tags, scenarios = get_value_filters(features)
    parameters_template = {
        "environments": environment,
        "features": features,
        "fields_total": totals,
        "summary": summary,
        "joined": joined,
        "report": report,
        "tags": list(tags),
        "scenarios": scenarios,
    }
    parameters_template.update(metrics_variables)
    output_text = T_HANDLER.render_template(TEST_REPORT_TEMPLATE, parameters_template)

    return output_text


def get_value_filters(features):
    """Processing data feature  for generate_gallery the filters"""
    tags = {
        tag
        for feature in features
        for scenario in feature["scenarios"]
        for tag in scenario["tags"]
    }

    scenarios = [
        (scenario["name"], "{}-{}".format(feature["id"], scenario["id_hash"]))
        for feature in features
        for scenario in feature["scenarios"]
    ]

    return tags, scenarios


def export_to_html_table_summary(features):
    """Generate summary for report html"""
    list_fields = [
        "Feature",
        "Total",
        "Executed",
        "Passed",
        "Failed",
        "Skipped",
        "Execution Status",
        "Pass Rate",
        "Duration",
    ]

    tuples_fields = [(field, 0) for field in list_fields]
    fields = OrderedDict(tuples_fields)
    fields_total = OrderedDict([("Totals", "Totals")] + tuples_fields[1:])

    summary = {}
    for feature in features:
        fields.update({field: 0 for field in list_fields[1:6]})
        to_be_fixed = 0
        for scenario in feature["scenarios"]:
            fields["Total"] += 1
            if any(i in ["TEST_TO_FIX", "BUG_TO_FIX"] for i in scenario["tags"]):
                to_be_fixed += 1
            if scenario["status"] == "passed":
                fields["Executed"] += 1
                fields["Passed"] += 1
            elif scenario["status"] == "failed":
                fields["Executed"] += 1
                fields["Failed"] += 1
            else:
                fields["Skipped"] += 1

        fields_total.update(
            {field: fields_total[field] + fields[field] for field in list_fields[1:6]}
        )

        fields_total["Duration"] += feature["duration"]
        if fields["Total"] == 0:
            fields["Total"] = 1

        fields["Execution Status"] = "%.2f" % (
            (float(fields["Executed"]) / fields["Total"]) * 100
        )

        fields["Pass Rate"] = "%.2f" % (
            (float(fields["Passed"]) / fields["Total"]) * 100
        )

        fields["Duration"] = feature["duration"]
        summary[feature["name"]] = fields.copy()
        summary[feature["name"]]["to_be_fixed"] = to_be_fixed

    if len(features) > 0:
        fields_total["Execution Status"] = "%.2f" % (
            (float(fields_total["Executed"]) / fields_total["Total"]) * 100
        )

        fields_total["Pass Rate"] = "%.2f" % (
            (float(fields_total["Passed"]) / fields_total["Total"]) * 100
        )

    return fields_total, summary

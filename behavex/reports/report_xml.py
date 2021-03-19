# -*- encoding: utf-8 -*
"""
/*
* BehaveX - Agile test wrapper on top of Behave (BDD)
*/
"""
# __future__ has been added in order to maintain compatibility
from __future__ import absolute_import

import os
import re

from behavex.conf_mgr import get_env
from behavex.reports.report_utils import (
    get_save_function,
    match_for_execution,
    text,
    try_operate_descriptor,
)
from behavex.reports.template_handler import TemplateHandler

FWK_DIR = os.environ.get("BEHAVEX_PATH")
INFO_FILE = "report.json"
TEMPLATE_DIR = os.path.join(FWK_DIR, "reports", "templates")

FEATURE_XML_TEMPLATE = "xml.jinja2"
FEATURE_XML_JSON_TEMPLATE = "xml_json.jinja2"

T_HANDLER = TemplateHandler(TEMPLATE_DIR)


def _export_feature_to_xml(feature, isobject=True):
    """This function generate_gallery one file xml with information of the scenario"""

    def get_scenarios(feature_):
        """
        Access to attribute scenarios depend if is object then accessing
        as attribute else accessing to dictionary
        :param feature_:
        :return:
        """

        def flatter_scenarios(scenarios_list):
            return sum(
                (
                    [scenario] if scenario.type == "scenario" else scenario._scenarios
                    for scenario in scenarios_list
                ),
                [],
            )

        return (
            flatter_scenarios(feature_.scenarios) if isobject else feature_["scenarios"]
        )

    def get_tags(scenario_):
        """
        Access to attribute scenarios depend if is object then accessing
        as attribute else accessing to dictionary
        :param scenario_:
        :return:
        """
        return scenario_.tags if isobject else scenario_["tags"]

    def get_status(scenario_):
        """
        Access to attribute scenarios depend if is object then accessing
        as attribute else accessing to dictionary
        :param scenario_:
        :return:
        """
        return scenario_.status if isobject else scenario_["status"]

    scenarios = [
        scenario
        for scenario in get_scenarios(feature)
        if match_for_execution(get_tags(scenario))
    ]

    skipped = [scenario for scenario in scenarios if get_status(scenario) == "skipped"]
    failures = [
        scenario
        for scenario in scenarios
        if get_status(scenario) == "failed" or get_status(scenario) == "untested"
    ]

    bug_to_fix = [
        scenario
        for scenario in scenarios
        if any(i in ["TEST_TO_FIX", "BUG_TO_FIX"] for i in get_tags(scenario))
    ]

    bug_to_fix_failed = [
        scenario for scenario in bug_to_fix if get_status(scenario) == "failed"
    ]

    summary = {
        "time": sum(
            scenario.duration if isobject else scenario["duration"]
            for scenario in scenarios
        ),
        "tests": len(scenarios),
        "failures": len(failures) - len(bug_to_fix_failed),
        "skipped": len(skipped) + len(bug_to_fix_failed),
    }
    parameters_template = {
        "feature": feature,
        "summary": summary,
        "skipped": skipped,
        "failures": failures,
        "scenarios": scenarios,
        "to_be_fixed": bug_to_fix_failed,
    }

    output_text = T_HANDLER.render_template(
        FEATURE_XML_TEMPLATE if isobject else FEATURE_XML_JSON_TEMPLATE,
        parameters_template,
    )
    output_text = output_text.replace("Status.", "")
    exp = re.compile("\\\\|/")
    filename = feature.filename if isobject else feature["filename"]
    filename = text(filename)
    name = u".".join(exp.split(filename.partition("features")[2][1:-8]))
    junit_path = os.path.join(get_env("OUTPUT"), "behave")
    path_output = os.path.join(junit_path, u"TESTS-" + name + u".xml")

    try_operate_descriptor(
        path_output + ".xml", get_save_function(path_output, output_text)
    )


def export_feature_to_xml(feature, isobject=True):
    """This function generate_gallery one file xml with information of the scenario"""
    _export_feature_to_xml(feature, isobject)

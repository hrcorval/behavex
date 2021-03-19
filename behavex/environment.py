# -*- encoding: utf-8 -*-
# pylint: disable=W0703# pylint: disable=W0703
"""
BehaveX - Agile test wrapper on top of Behave (BDD)
"""
import logging
import os
import shutil

from behave.log_capture import capture
from behave.runner import Context

from behavex import conf_mgr
from behavex.conf_mgr import get_env, get_param
from behavex.reexecute import run_scenario_with_retries
from behavex.reports import report_json, report_xml
from behavex.reports.report_utils import RETRY_SCENARIOS, create_log_path
from behavex.utils import (LOGGING_CFG, create_custom_log_when_called,
                           get_logging_level)

Context.__getattribute__ = create_custom_log_when_called


def before_all(context):
    """Setup up initial tests configuration."""
    try:
        # Initialyzing log handler
        context.bhx_log_handler = None
        # Store framework settings to make them accessible from steps
        context.bhx_config_framework = conf_mgr.get_config()
        context.bhx_inside_scenario = False
    except Exception as exception:
        _log_exception_and_continue("before_all (behavex)", exception)


# noinspection PyUnusedLocal
def before_feature(context, feature):
    try:
        for scenario in feature.scenarios:
            scenario.tags += feature.tags
            if get_param("dry_run"):
                if "MANUAL" not in scenario.tags:
                    scenario.tags.append(u"BHX_MANUAL_DRY_RUN")
                    scenario.tags.append(u"MANUAL")

            if "AUTORETRY" in scenario.tags:
                run_scenario_with_retries(scenario, max_attempts=2)
    except Exception as exception:
        _log_exception_and_continue("before_feature (behavex)", exception)


def before_scenario(context, scenario):
    """Initialize logs for current scenario."""
    try:
        context.bhx_inside_scenario = True
        context.log_path = create_log_path(str(scenario.name))
        retry_scenario = False
        if (
            scenario.status in ("failed", "untested")
            and "AUTORETRY" in scenario.tags
            and get_env("autoretry_attempt") == "1"
        ):
            # if retry occurs just append logs to already existing log file
            retry_scenario = True
        mode = "w"
        if retry_scenario:
            mode = "a+"
            shutil.rmtree(context.evidence_path)
            message = "{1}{0}{1} Retrying Test Scenario... {1}{0}".format(
                "*" * 34, "\n" * 2
            )
            _log_exception_and_continue(message, "")
        log_filename = os.path.join(context.log_path, "scenario.log")
        file_handler = logging.FileHandler(
            log_filename, mode, encoding=LOGGING_CFG["file_handler"]["encoding"]
        )
        context.bhx_log_handler = _add_log_handler(file_handler)
    except Exception as exception:
        _log_exception_and_continue("before_scenario (behavex)", exception)


def before_step(context, step):
    if context.bhx_inside_scenario:
        logging.info("STEP: {}".format(step.name))


def after_step(context, step):
    if step.exception:
        step.error_message = step.error_message
        logging.exception(step.exception)
    if context.bhx_inside_scenario:
        logging.debug("Execution time %.2f sec\n", step.duration)


@capture
def after_scenario(context, scenario):
    try:
        if (
            scenario.status in ("failed", "untested")
            and "AUTORETRY" in scenario.tags
            and get_env("autoretry_attempt") == "0"
        ):
            scenario.reset()
            feature_name = scenario.feature.name
            if feature_name not in RETRY_SCENARIOS:
                RETRY_SCENARIOS[feature_name] = [scenario.name]
            else:
                RETRY_SCENARIOS[feature_name].append(scenario.name)
        _close_log_handler(context.bhx_log_handler)
    except Exception as exception:
        _log_exception_and_continue("after_scenario (behavex)", exception)


# noinspection PyUnusedLocal
def after_feature(context, feature):
    if get_env("multiprocessing") and get_param("parallel_element") == "scenario":
        return
    report_xml.export_feature_to_xml(feature)


def after_all(context):
    try:
        report_json.generate_execution_info(context, context._runner.features)
    except Exception as exception:
        _log_exception_and_continue("after_all (json_report)", exception)


def _add_log_handler(handler):
    """Adding a new log handler to logger"""
    log_level = get_logging_level()
    logging.getLogger().setLevel(log_level)
    handler.setFormatter(_get_log_formatter())
    logging.getLogger().addHandler(handler)
    return handler


def _close_log_handler(handler):
    """Closing current log handlers and removing them from logger"""
    if handler:
        if hasattr(handler, "stream") and hasattr(handler.stream, "close"):
            handler.stream.close()
        logging.getLogger().removeHandler(handler)


def _get_log_formatter():
    """Adding a new log handler to logger"""
    default_log_format = "%(asctime)s - %(levelname)s - %(message)s"
    default_date_format = "%H:%M:%S"
    logging_format = os.environ.get("logging_format", default_log_format)
    date_format = os.environ.get("logging_datefmt", default_date_format)
    try:
        formatter = logging.Formatter(logging_format, date_format)
    except Exception as exception:
        formatter = logging.Formatter(default_log_format, default_date_format)
        _log_exception_and_continue("_get_log_formatter", exception)
    return formatter


def _log_exception_and_continue(module, exception):
    """Logs any exception that occurs without raising it,
    just to avoid the testing framework to stop executing
    the following tests"""
    error_message = "Unexpected error in '%s' function:" % module
    logging.exception(error_message)
    logging.exception(exception)

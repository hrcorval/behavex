# -*- coding: utf-8 -*-
# pylint: disable=W0703# pylint: disable=W0703
"""
BehaveX - Agile test wrapper on top of Behave (BDD)
"""
import logging
import os
import shutil

from behave.contrib.scenario_autoretry import patch_scenario_with_autoretry
from behave.log_capture import capture
from behave.runner import Context

from behavex import conf_mgr
from behavex.conf_mgr import get_env, get_param
from behavex.execution_context import ExecutionContext
from behavex.outputs import report_json, report_xml
from behavex.outputs.report_utils import create_log_path
from behavex.utils import (
    LOGGING_CFG,
    create_custom_log_when_called,
    get_autoretry_attempts,
    get_logging_level,
)

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
        _log_exception_and_continue('before_all (behavex)', exception)


# noinspection PyUnusedLocal
def before_feature(context, feature):
    try:
        context.execution_attempts = {}
        for scenario in feature.scenarios:
            context.execution_attempts[scenario.name] = 0
            scenario.tags += feature.tags
            if get_param('dry_run'):
                if 'MANUAL' not in scenario.tags:
                    scenario.tags.append(u'BHX_MANUAL_DRY_RUN')
                    scenario.tags.append(u'MANUAL')
            configured_attempts = get_autoretry_attempts(scenario.tags)
            if configured_attempts > 0:
                patch_scenario_with_autoretry(scenario, configured_attempts)
    except Exception as exception:
        _log_exception_and_continue('before_feature (behavex)', exception)


def before_scenario(context, scenario):
    """Initialize logs for current scenario."""
    try:
        context.bhx_inside_scenario = True
        execution_attempt = context.execution_attempts[scenario.name]
        retrying_execution = True if execution_attempt > 0 else False
        context.log_path, context.bhx_log_handler = _add_log_handler(
            str(scenario.name), retrying_execution
        )
        if retrying_execution:
            logging.info('Retrying scenario...\n'.format())
            shutil.rmtree(context.evidence_path)
    except Exception as exception:
        _log_exception_and_continue('before_scenario (behavex)', exception)


def before_step(context, step):
    if context.bhx_inside_scenario:
        logging.info('STEP: {}'.format(step.name))


def after_step(context, step):
    if step.exception:
        step.error_message = step.error_message
        logging.exception(step.exception)
    if context.bhx_inside_scenario:
        logging.debug('Execution time %.2f sec\n', step.duration)


@capture
def after_scenario(context, scenario):
    try:
        configured_attempts = get_autoretry_attempts(scenario.tags)
        if scenario.status in ('failed', 'untested') and configured_attempts > 0:
            feature_name = scenario.feature.name
            if feature_name not in ExecutionContext().retried_scenarios:
                ExecutionContext().retried_scenarios[feature_name] = [scenario.name]
            else:
                ExecutionContext().retried_scenarios[feature_name].append(scenario.name)
            context.execution_attempts[scenario.name] += 1
        _close_log_handler(context.bhx_log_handler)
    except Exception as exception:
        _log_exception_and_continue('after_scenario (behavex)', exception)


# noinspection PyUnusedLocal
def after_feature(context, feature):
    if get_env('multiprocessing') and get_param('parallel_element') == 'scenario':
        return
    report_xml.export_feature_to_xml(feature)


def after_all(context):
    try:
        report_json.generate_execution_info(context, context._runner.features)
    except Exception as exception:
        _log_exception_and_continue('after_all (json_report)', exception)


def _add_log_handler(scenario_name, retrying_execution=False):
    """Adding a new log handler to logger"""
    log_path = create_log_path(scenario_name, retrying_execution)
    log_filename = os.path.join(log_path, 'scenario.log')
    file_handler = logging.FileHandler(
        log_filename, mode='+a', encoding=LOGGING_CFG['file_handler']['encoding']
    )
    log_level = get_logging_level()
    logging.getLogger().setLevel(log_level)
    file_handler.setFormatter(_get_log_formatter())
    logging.getLogger().addHandler(file_handler)
    return log_path, file_handler


def _close_log_handler(handler):
    """Closing current log handlers and removing them from logger"""
    if handler:
        if hasattr(handler, 'stream') and hasattr(handler.stream, 'close'):
            handler.stream.close()
        logging.getLogger().removeHandler(handler)


def _get_log_formatter():
    """Adding a new log handler to logger"""
    default_log_format = '%(asctime)s - %(levelname)s - %(message)s'
    default_date_format = '%H:%M:%S'
    logging_format = os.environ.get('logging_format', default_log_format)
    date_format = os.environ.get('logging_datefmt', default_date_format)
    try:
        formatter = logging.Formatter(logging_format, date_format)
    except Exception as exception:
        formatter = logging.Formatter(default_log_format, default_date_format)
        _log_exception_and_continue('_get_log_formatter', exception)
    return formatter


def _log_exception_and_continue(module, exception):
    """Logs any exception that occurs without raising it,
    just to avoid the testing framework to stop executing
    the following tests"""
    error_message = "Unexpected error in '%s' function:" % module
    logging.exception(error_message)
    logging.exception(exception)

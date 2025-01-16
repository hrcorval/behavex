# -*- coding: utf-8 -*-
# pylint: disable=W0703# pylint: disable=W0703
"""
BehaveX - Agile test wrapper on top of Behave (BDD)
"""
import logging
import os
import shutil
import sys

from behave.contrib.scenario_autoretry import patch_scenario_with_autoretry
from behave.log_capture import capture
from behave.model import ScenarioOutline
from behave.runner import Context, ModelRunner

from behavex import conf_mgr
from behavex.conf_mgr import get_env, get_param
from behavex.global_vars import global_vars
from behavex.outputs import report_json, report_xml
from behavex.outputs.report_utils import create_log_path, strip_ansi_codes
from behavex.utils import (LOGGING_CFG, create_custom_log_when_called,
                           get_autoretry_attempts, get_logging_level,
                           get_scenario_tags, get_scenarios_instances)

Context.__getattribute__ = create_custom_log_when_called

hooks_already_set = False

def extend_behave_hooks():
    """
    Extend Behave hooks with BehaveX hooks code.
    """
    global hooks_already_set
    behave_run_hook = ModelRunner.run_hook
    behavex_env = sys.modules[__name__]
    is_dry_run = get_param('dry_run')

    def run_hook(self, name, context, *args):

        if name == 'before_all':
            # noinspection PyUnresolvedReferences
            if not is_dry_run:
                behave_run_hook(self, name, context, *args)
            behavex_env.before_all(context)
        elif name == 'before_feature':
            # noinspection PyUnresolvedReferences
            if not is_dry_run:
                behave_run_hook(self, name, context, *args)
            behavex_env.before_feature(context, *args)
        elif name == 'before_scenario':
            # noinspection PyUnresolvedReferences
            if not is_dry_run:
                behave_run_hook(self, name, context, *args)
            behavex_env.before_scenario(context, *args)
        elif name == 'before_step':
            # noinspection PyUnresolvedReferences
            if not is_dry_run:
                behave_run_hook(self, name, context, *args)
            behavex_env.before_step(context, *args)
        elif name == 'before_tag':
            # noinspection PyUnresolvedReferences
            if not is_dry_run:
                behave_run_hook(self, name, context, *args)
            behavex_env.before_tag(context, *args)
        elif name == 'after_tag':
            # noinspection PyUnresolvedReferences
            if not is_dry_run:
                behave_run_hook(self, name, context, *args)
            behavex_env.after_tag(context, *args)
        elif name == 'after_step':
            # noinspection PyUnresolvedReferences
            behavex_env.after_step(context, *args)
            if not is_dry_run:
                behave_run_hook(self, name, context, *args)
        elif name == 'after_scenario':
            # noinspection PyUnresolvedReferences
            if not is_dry_run:
                behave_run_hook(self, name, context, *args)
            behavex_env.after_scenario(context, *args)
        elif name == 'after_feature':
            # noinspection PyUnresolvedReferences
            behavex_env.after_feature(context, *args)
            if not is_dry_run:
                behave_run_hook(self, name, context, *args)
        elif name == 'after_all':
            # noinspection PyUnresolvedReferences
            behavex_env.after_all(context, *args)
            if not is_dry_run:
                behave_run_hook(self, name, context, *args)
        else:
            # noinspection PyUnresolvedReferences
            if not is_dry_run:
                behave_run_hook(self, name, context, *args)

    if not hooks_already_set:
        hooks_already_set = True
        ModelRunner.run_hook = run_hook


def before_all(context):
    """Setup up initial tests configuration."""
    try:
        # Initialyzing log handler
        context.bhx_log_handler = None
        context.bhx_inside_scenario = False
        # Store framework settings to make them accessible from steps
        context.bhx_config_framework = conf_mgr.get_config()
    except Exception as exception:
        _log_exception_and_continue('before_all (behavex)', exception)


# noinspection PyUnusedLocal
def before_feature(context, feature):
    try:
        context.bhx_execution_attempts = {}
        scenarios_instances = get_scenarios_instances(feature.scenarios)
        for scenario in scenarios_instances:
            scenario_tags = get_scenario_tags(scenario)
            if get_param('dry_run'):
                if 'MANUAL' not in scenario_tags:
                    scenario.tags.append(u'BHX_MANUAL_DRY_RUN')
                    scenario.tags.append(u'MANUAL')
            configured_attempts = get_autoretry_attempts(scenario_tags)
            if configured_attempts > 0:
                patch_scenario_with_autoretry(scenario, configured_attempts)
    except Exception as exception:
        _log_exception_and_continue('before_feature (behavex)', exception)


def before_scenario(context, scenario):
    """Initialize logs for current scenario."""
    try:
        context.bhx_inside_scenario = True
        if scenario.name not in context.bhx_execution_attempts:
            context.bhx_execution_attempts[scenario.name] = 0
        execution_attempt = context.bhx_execution_attempts[scenario.name]
        retrying_execution = True if execution_attempt > 0 else False
        concat_feature_and_scenario_line = "{}-{}".format(str(context.feature.filename), str(scenario.line))
        context.log_path = create_log_path(concat_feature_and_scenario_line, retrying_execution)
        context.bhx_log_handler = _add_log_handler(context.log_path)
        if retrying_execution:
            logging.info('Retrying scenario execution...\n'.format())
            shutil.rmtree(context.evidence_path)
    except Exception as exception:
        _log_exception_and_continue('before_scenario (behavex)', exception)


def before_step(context, step):
    pass


def before_tag(context, tag):
    pass


def after_tag(context, tag):
    pass


def after_step(context, step):
    try:
        if step.exception:
            step.error_message = step.error_message
            logging.error(step.exception)
    except Exception as exception:
        _log_exception_and_continue('after_step (behavex)', exception)


@capture
def after_scenario(context, scenario):
    try:
        scenario_tags = get_scenario_tags(scenario)
        configured_attempts = get_autoretry_attempts(scenario_tags)
        if scenario.status in ('failed', 'untested') and configured_attempts > 0:
            feature_name = scenario.feature.name
            if feature_name not in global_vars.retried_scenarios:
                global_vars.retried_scenarios[feature_name] = [scenario.name]
            else:
                global_vars.retried_scenarios[feature_name].append(scenario.name)
            context.bhx_execution_attempts[scenario.name] += 1
        _close_log_handler(context.bhx_log_handler)
    except Exception as exception:
        _log_exception_and_continue('after_scenario (behavex)', exception)


# noinspection PyUnusedLocal
def after_feature(context, feature):
    try:
        if get_env('multiprocessing') and get_param('parallel_scheme') == 'scenario':
            return
        report_xml.export_feature_to_xml(feature)
    except Exception as exception:
        _log_exception_and_continue('after_feature (behavex)', exception)


def after_all(context):
    try:
        # noinspection PyProtectedMember
        feature_list = report_json.generate_execution_info(context._runner.features)
        report_json.generate_json_report(feature_list)
    except Exception as exception:
        _log_exception_and_continue('after_all (json_report)', exception)


def _add_log_handler(log_path):
    """Adding a new log handler to logger"""
    log_filename = os.path.join(log_path, 'scenario.log')
    file_handler = logging.FileHandler(
        log_filename, mode='+a', encoding=LOGGING_CFG['file_handler']['encoding']
    )
    log_level = get_logging_level()
    logging.getLogger().setLevel(log_level)
    file_handler.addFilter(lambda record: setattr(record, 'msg', strip_ansi_codes(str(record.msg))) or True)
    file_handler.setFormatter(_get_log_formatter())
    logging.getLogger().addHandler(file_handler)
    return file_handler


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
    logging.error(error_message)
    logging.error(exception)

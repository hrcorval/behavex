# -*- coding: utf-8 -*-
"""
/*
* BehaveX - Production-grade test orchestration for Python BDD.
*/

This module process the configuration required by the framework. Default values
 are used if no config file is provided.
"""
# pylint: disable=W0703
# pylint: disable=W0603

from __future__ import absolute_import

import os

from configobj import ConfigObj
from validate import Validator

from behavex.execution_singleton import ExecutionSingleton

CONFIG = None
CONFIG_PATH = None


def get_config():
    """Returns a dictionary containing
    the framework configuration values"""
    config_spec = """
    [output]
    path=string(default="output")

    [progress_bar]
    print_updates_in_new_lines=boolean(default=False)

    [test_run]
    tags_to_skip=string(default="")

    [params]
    tags=list(default=list())
    parallel_processes=integer(default=1)
    parallel_scheme=option('feature', 'scenario', default='scenario')
    parallel_delay=integer(default=0)
    include_paths=list(default=list())
    rerun_failures=string(default="")
    dry_run=boolean(default=False)
    show_progress_bar=boolean(default=False)
    formatter=string(default="")
    formatter_outdir=string(default="")
    formatter_attach_logs=boolean(default=True)
    order_tests=boolean(default=False)
    order_tests_strict=boolean(default=False)
    order_tag_prefix=string(default="ORDER")
    no_color=boolean(default=False)
    no_capture=boolean(default=False)
    capture_stderr=boolean(default=False)
    no_logcapture=boolean(default=False)
    no_snippets=boolean(default=False)
    define=list(default=list())
    exclude=string(default="")
    include=string(default="")
    name=string(default="")
    lang=string(default="")
    stage=string(default="")
    logging_level=option('CRITICAL', \
                         'ERROR', \
                         'WARNING', \
                         'INFO', \
                         'DEBUG', \
                         'NOTSET', \
                         default='INFO')
    logging_format=string(default="")
    logging_datefmt=string(default="")
    logging_filter=string(default="")
    stop=boolean(default=False)
    wip=boolean(default=False)
    requirements_config=string(default="")
    """
    global CONFIG
    global CONFIG_PATH
    if CONFIG is None or CONFIG_PATH != os.environ.get('CONFIG'):
        CONFIG_PATH = os.environ.get('CONFIG')
        spec = config_spec.split('\n')
        validator = Validator()
        CONFIG = ConfigObj(CONFIG_PATH, configspec=spec)
        CONFIG.validate(validator, copy=True)

    return CONFIG


class ConfigRun(metaclass=ExecutionSingleton):
    def __init__(self):
        self.config = get_config()
        self.args = None
        self.environ = {}

    def prepare_environment(self):
        output = self.get_param('output.path', 'output_folder')
        self.environ['output'] = output
        self.environ['temp'] = os.path.join(output, 'temp')

        # If a formatter is specified in command line arguments, use its output as logs path
        formatter = self.get_param('formatter', 'formatter')
        if formatter:
            formatter_output = self.get_param('formatter.outdir', 'formatter_outdir')
            self.environ['logs'] = os.path.join(output, formatter_output)
        else:
            self.environ['logs'] = os.path.join(output, 'outputs', 'logs')

    def set_args(self, args):
        self.args = args
        self.prepare_environment()

    def set_env(self, key, value):
        self.environ[key] = value

    def get_param_config(self, key_chain):
        keys = key_chain.split('.')
        if len(keys) == 1:
            keys = ['params'] + keys
        dictionary = self.config
        for key in keys:
            result = dictionary.get(key, '')
            if isinstance(result, str):
                return result
            if isinstance(result, dict):
                dictionary = result
            else:
                return result
        return ''

    def get_param(self, key_chain, arg=None):
        if not arg:
            arg = key_chain.split('.')[-1]
        cli_value = getattr(self.args, arg, None) if self.args else None
        # None/empty-string/empty-list → argparse default, fall through to config.
        # False is NOT in this set because store_false params use False to signal
        # that the user explicitly passed the flag (e.g. --no-formatter-attach-logs).
        # All store_true params must have default=None (not False) so that their
        # "not set" state is also None, not False.
        cli_is_unset = cli_value is None or cli_value == '' or cli_value == []
        if not cli_is_unset:
            return cli_value
        config_value = self.get_param_config(key_chain)
        if config_value not in (None, '', [], {}):
            return config_value
        # Both CLI and config are "empty"; return the typed config default
        # (e.g. '' or False) rather than argparse None.
        return config_value

    def get_env(self, key, optional=None):
        return self.environ.get(key.lower(), optional)


def get_param(key_chain, arg=None):
    return ConfigRun().get_param(key_chain, arg)


def get_env(key, optional=None):
    return ConfigRun().get_env(key, optional)


def set_env(key, value):
    ConfigRun().set_env(key, value)

# -*- encoding: utf-8 -*
"""
/*
* BehaveX - Agile test wrapper on top of Behave (BDD)
*/


This module process the configuration required by the framework. Default values
 are used if no config file is provided.

Variables:
    - CONFIG
    - CONFIG_PATH

Functions:
    - get_config

"""
# pylint: disable=W0703
# pylint: disable=W0603

# __future__ and six added for compatibility
from __future__ import absolute_import
import os
from configobj import ConfigObj
from validate import Validator
import six


CONFIG = None
CONFIG_PATH = None


def get_config():
    """Returns a dictionary containing
    the framework configuration values"""
    config_spec = """
    [output]
    path=string(default="output")

    [reports]
    types=string_list(default=list("html", "xml"))

    [screenshots]
    hash_detail=string(default="0")

    [bug_tag]
    regex=string(default="BUG-")

    [test_run]
    tags_to_skip=string(default="")

    [params]
    requirements_config=string(default="")
    tags=list(default=list())
    dry_run=boolean(default=False)
    no_color=boolean(default=False)
    define=string(default="")
    exclude=string(default="")
    include=string(default="")
    name=string(default="")
    no_capture=boolean(default=False)
    capture=boolean(default=True)
    capture_stderr=boolean(default=False)
    no_logcapture=boolean(default=False)
    logcapture=boolean(default=True)
    no_snippets=boolean(default=False)
    stop=boolean(default=False)
    tags_help=boolean(default=False)
    logging_level=option('CRITICAL', 'ERROR', 'WARNING', 'INFO','DEBUG', 'NOTSET', default='INFO')
    parallel_processes=integer(default=1)
    parallel_element=option('feature', 'scenario', default='scenario')
    include_paths=list(default=list())
    run_failures=boolean(default=False)
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


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


# __metaclass__ has been changed to six.with_metaclass
class ConfigRun(six.with_metaclass(Singleton)):
    def __init__(self):
        self.config = get_config()
        self.args = None
        self.environ = {}

    def prepare_environment(self):
        output = self.get_param('output.path', 'output_folder')
        self.environ['output'] = output
        self.environ['temp'] = os.path.join(output, 'temp')
        self.environ['logs'] = os.path.join(output, 'reports', 'logs')

    def set_args(self, args):
        self.args = args
        self.prepare_environment()

    def set_env(self, key, value):
        self.environ[key] = value

    def get_param_config(self, key_chain):
        """Get text of the dictionary with annotation in chain"""
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
        """Method for accessing parameters with logic between file config and
         opt module."""
        if not arg:
            arg = key_chain.split('.')[-1]
        if getattr(self.args, arg):
            return getattr(self.args, arg)
        else:
            return self.get_param_config(key_chain)

    def get_env(self, key, optional=None):
        return self.environ.get(key.lower(), optional)


def get_param(key_chain, arg=None):
    return ConfigRun().get_param(key_chain, arg)


def get_env(key, optional=None):
    return ConfigRun().get_env(key, optional)


def set_env(key, value):
    ConfigRun().set_env(key, value)

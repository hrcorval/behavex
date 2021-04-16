# -*- coding: utf-8 -*-
"""
/*
* BehaveX - Agile test wrapper on top of Behave (BDD)
*/

Test report utility methods for retrieving summarized test execution information
 from features and scenarios
"""
# pylint: disable=W0703
# pylint: disable=W0703 , E1101

# __future__ is added in order to maintain compatibility
from __future__ import absolute_import, print_function

import ast
import codecs
import os
import re
import shutil
import string
import sys
import traceback
import unicodedata
from operator import getitem

from behave.model_core import Status

from behavex.conf_mgr import get_env, get_param, set_env
from behavex.execution_context import ExecutionContext


def gather_steps_with_definition(features, steps_definition):
    """
    Gather steps with definition.

    :return dict:
    """
    all_steps = []
    for feature in features:
        for scenario in feature['scenarios']:
            all_steps += scenario['steps']
            if scenario['background']:
                all_steps += scenario['background']['steps']
    result = {}
    if steps_definition:
        for id_hash, definition in steps_definition.items():
            result[definition] = {'steps': []}
            for step in all_steps:
                if step['hash'] == int(id_hash):
                    result[definition]['steps'].append(step)
        for definition, value in result.items():
            result[definition] = get_summary_definition(value['steps'])

    return result


def get_total_steps(steps_summary):
    """
    Get return dictionary with total.

    :param steps_summary: The dictionary of step definition.
    :return:  dictionary with follow keys:
        - definitions
        - appearances
        - executions
        - avg
        - time
        - status
    """
    result = {
        'definitions': 0,
        'instances': 0,
        'executions': 0,
        'avg': 0.0,
        'time': 0.0,
        'status': [],
        'appearances': 0,
    }
    for summary in steps_summary.values():
        result['definitions'] += 1
        result['appearances'] += summary['appearances']
        result['executions'] += summary['executions']
        result['avg'] += summary['avg']
        result['time'] += summary['time']
        result['status'] += summary['status']

    return result


def get_summary_definition(steps):
    """
    Get summary for a step definitions.

    :param steps: list of behave.model.step
    :return dict: a dict with follow keys:
     avg:
     time:
     status:
     executions:
     appearances:
     steps: dict with follow keys:
        avg:
        executions:
        time:
        status:
        appearances:
    """

    result = {'steps': {}, 'status': []}
    for step in steps:
        result['status'].append(step['status'])
        execution = 1 if step['status'] in ('failed', 'passed') else 0
        if step['name'] in result['steps']:
            result['steps'][step['name']]['executions'] += execution
            result['steps'][step['name']]['time'] += step['duration']
            result['steps'][step['name']]['status'].append(step['status'])
            result['steps'][step['name']]['appearances'] += 1
        else:

            result['steps'][step['name']] = {
                'executions': execution,
                'time': step['duration'],
                'status': [step['status']],
                'appearances': 1,
            }
    total_time = 0.0
    avg_time_total = 0.0
    executions = 0
    appearances = 0
    for step_instanced in result['steps'].values():
        avg_time = step_instanced['time'] / step_instanced['appearances']
        avg_time_total += avg_time
        total_time += step_instanced['time']
        step_instanced['avg'] = avg_time
        executions += step_instanced['executions']
        appearances += step_instanced['appearances']
    result['avg'] = avg_time_total
    result['time'] = total_time
    result['executions'] = executions
    result['appearances'] = appearances

    return result


def count_by_status(values, func='getitem'):
    """
    Count the status.

    create a tuple with 3 int, the first in count the quantity of status passed exitst,
    seconds the quantity status failed exist and the last the quantity of status skipped,
     undefined and s untested

    :param values: Element that are iterable and contain the key status
    :param func:
    :return: tuple
    """
    if func == 'getitem':
        get_item = getitem
    elif func == 'getattr':
        get_item = getattr
    elif func == 'first_value':

        def get_item(x, y):
            return x

    else:
        get_item = func
    skipped = len(
        [
            1
            for value in values
            if get_item(value, 'status') in ('skipped', 'undefined', 'untested')
        ]
    )
    passed = len([1 for value in values if get_item(value, 'status') == 'passed'])
    failed = len([1 for value in values if get_item(value, 'status') == 'failed'])
    return passed, failed, skipped


def calculate_status(list_status):
    """
    Calculate the finally status.

    It Should be a list with word 'passed', 'failed', 'passed', 'untested'
    >> lst = ['passed', 'passed', 'failed']
    >> calculate_status(lst)
    'failed'
    >> lst = ['passed', 'passed', 'skipped']
    >> calculate_status(lst)
    'passed'
    >> lst = ['untested', 'passed', 'skipped']
    >> calculate_status(lst)
    'passed'
    >> lst = ['untested', 'skipped', 'skipped']
    >> calculate_status(lst)
    'skipped'

    :param list_status: list.
    :return str:
    """

    set_status = set(list_status)
    if 'untested' in set_status:
        set_status.remove('untested')
        set_status.add('skipped')
    if 'undefined' in set_status:
        set_status.remove('undefined')
        set_status.add('skipped')
    if 'failed' in set_status:
        return 'failed'
    elif {'skipped'} == set_status:
        return 'skipped'
    else:
        return 'passed'


def gather_steps(features):
    """retrieves a dictionary with steps used in latest test execution,
    together with the number of times they were executed"""
    steps = {}
    for feature in features:
        for scenario in feature['scenarios']:
            steps_back = [step for step in scenario['background']['steps']]
            for step in scenario['steps'] + steps_back:
                if not step['name'] in steps:
                    steps[step['name']] = {
                        'quantity': 0,
                        'total_duration': 0,
                        'appearances': 0,
                        'passed': 0,
                        'failed': 0,
                        'skipped': 0,
                    }
                steps[step['name']]['appearances'] += 1

                add = (
                    0
                    if step['status'].lower() in ['skipped', 'untested', 'undefined']
                    else 1
                )
                passed = 1 if step['status'] == 'passed' else 0
                failed = 1 if step['status'] == 'failed' else 0
                steps[step['name']]['passed'] += passed
                steps[step['name']]['failed'] += failed
                steps[step['name']]['quantity'] += add
                steps[step['name']]['skipped'] += not add
                steps[step['name']]['total_duration'] += step['duration']

    return steps


def get_scenarios_by_tag(all_scenarios):
    """
    return one dict with each key contain one tuple with following format:
    in position zero have list of the dict each dict have tuple with the name
    scenario in position 0, status in position 1, number row in position 2,
    id_hash in position 3, and id_feature position 4

    :param all_scenarios: list of the scenario
    :return: dict
    """
    all_tags = set(sum((scenario['tags'] for scenario in all_scenarios), []))
    scenarios_by_tag = {}

    for tag in all_tags:
        scenarios_by_tag[tag] = [
            (
                scenario['name'],
                scenario['status'],
                scenario.get('row', ''),
                scenario['id_hash'],
                scenario['id_feature'],
            )
            for scenario in all_scenarios
            if tag in scenario['tags']
        ]
    scenarios_by_tag.update(
        {
            key: (
                value,
                {status for name, status, row, id_hash, id_feature in value},
                {row for name, status, row, id_hash, id_feature in value},
            )
            for key, value in scenarios_by_tag.items()
        }
    )

    processed_tags = {
        key: (value[0], get_status({key: key for key in value[1]}), value[2])
        for key, value in scenarios_by_tag.items()
    }

    return processed_tags


def gather_errors(scenario, retrieve_step_name=False):
    """Retrieve the error message related to a particular failing scenario"""
    if retrieve_step_name:
        return scenario['error_msg'], scenario['error_lines'], scenario['error_step']
    else:
        return scenario['error_msg'], scenario['error_lines']


def pretty_print_time(seconds_float, sec_decimals=1):
    """pretty print time based on a given number of seconds"""
    seconds_float = round(seconds_float, sec_decimals)
    minutes, seconds = divmod(seconds_float, 60)
    hours, minutes = divmod(minutes, 60)

    seconds = (
        int(seconds) if float(seconds).is_integer() else round(seconds, sec_decimals)
    )

    def _pretty_format(cant, unit):
        return '{}{}'.format(cant, unit) if cant > 0 else ''

    return '{} {} {}'.format(
        _pretty_format(int(hours), 'h'),
        _pretty_format(int(minutes), 'm'),
        _pretty_format(seconds, 's'),
    )


def normalize_path(path):
    """Normalize the path for support in linux and windows"""
    exp = re.compile('\\\\|/')
    return os.path.join(*exp.split(path))


def resolving_type(step, scenario, background=True):
    """Resolving if have that put And or your step_type"""
    if step['index'] == 0:
        return step['step_type'].title()
    else:
        steps = scenario['steps']
        if 'background' in list(step.keys()) and not background:
            steps = scenario['background']['steps']
        # noinspection PyBroadException
        try:
            previous_type = steps[step['index'] - 1]['step_type']
        except BaseException:
            previous_type = step['step_type']
        if previous_type == step['step_type']:
            return 'And'
        else:
            return step['step_type'].title()


def try_operate_descriptor(dest_path, execution, return_value=False):
    """This function tries to operate with the descriptor, if the execution
    fails, then the flow of execution stops until the user enters the 'F' key
    to rerun the operation"""
    passed = False
    following = True
    retry_number = 1
    while not passed and following:
        try:
            result = execution()
            passed = True
            if return_value:
                return result
        except Exception as exception:
            menu = (
                '\nAnother program is using the files in path {}. '
                "Please, close the program and press 'c' to continue "
                " or 'a' for abort. Retry number {}\n\n.{}"
            )
            option_correct = False
            retry_number += 1
            option = (
                str(
                    input(
                        menu.format(os.path.abspath(dest_path), retry_number, exception)
                    )
                )
                .upper()
                .strip()
            )
            while not option_correct and not passed:
                if option == 'C':
                    following = True
                    option_correct = True
                elif option == 'A':
                    exit()
                else:
                    following = True
                    option_correct = False
                    msg = (
                        "\nInvalid option. Please, press 'c' to continue "
                        "or 'a' to abort\n"
                    )
                    option = str(input(msg)).upper().strip()


def get_status(dictionary):
    """Return the status"""
    return (
        dictionary.get('failed', False)
        or dictionary.get('passed', False)
        or dictionary.get('skipped', 'skipped')
    )


def get_test_execution_tags():
    """return the tags given of the console execution
    :return: tags
    """
    if not get_env('behave_tags'):
        behave_tags_path = os.path.join(
            os.path.abspath(get_env('OUTPUT')), ExecutionContext().behave_tags_file
        )
        behave_tags_file = open(behave_tags_path, 'r')
        behave_tags = behave_tags_file.readline().strip()
        behave_tags_file.close()
        os.chmod(behave_tags_path, 511)  # nosec
        set_env('behave_tags', behave_tags.replace('@MANUAL', 'False'))
        return get_env('behave_tags')
    else:
        return get_env('behave_tags')


def match_for_execution(tags):
    """ Indicates if provided tags match with execution tags """
    # Check filter
    tag_re = re.compile(r'@?[\w\d\-_.]+')
    tags_filter = get_test_execution_tags()
    # Eliminate tags put for param dry-rFun
    if get_param('dry_run'):
        if 'BHX_MANUAL_DRY_RUN' in tags:
            tags.remove('BHX_MANUAL_DRY_RUN')
            tags.remove('MANUAL')
    # Set scenario tags in filter
    for tag in tags:
        # Try with and without @
        def replace(arroba, x, y):
            return re.sub(r'^{}{}$'.format(arroba, x), 'True', y)

        tags_filter = ' '.join(
            [replace('@', tag, tag_) for tag_ in tags_filter.split()]
        )

        tags_filter = ' '.join([replace('', tag, tag_) for tag_ in tags_filter.split()])

    # Set all other tags to False
    for tag in tag_re.findall(tags_filter):
        if tag not in ('not', 'and', 'or', 'True', 'False'):
            tags_filter = tags_filter.replace(tag + ' ', 'False ')
    return tags_filter == '' or eval(tags_filter)


def copy_bootstrap_html_generator(output):
    """copy the bootstrap directory for portable html"""
    dest_path = os.path.join(output, 'outputs', 'bootstrap')
    bootstrap_path = ['outputs', 'bootstrap']
    bootstrap_path = os.path.join(ExecutionContext().execution_path, *bootstrap_path)
    if os.path.exists(dest_path):
        try_operate_descriptor(dest_path, lambda: shutil.rmtree(dest_path))
    try_operate_descriptor(
        dest_path, lambda: shutil.copytree(bootstrap_path, dest_path)
    )


def get_overall_status(output):
    """Calculating overall status"""
    if not output:
        return {'status': 'skipped'}
    overall_status = {
        feature['status']: feature['status'] for feature in output['features']
    }
    overall_status_end = get_status(overall_status)
    return overall_status_end


def get_save_function(path, content):
    """
    Returns a function that saves a file with the specified
    content and file privileges
    :param path: location of file
    :param content:  The content that will be written to the file
    :return: fun_save function
    """

    def fun_save():
        """
        Functino aux for save.
        :return:
        """
        with codecs.open(path, 'w', 'utf8') as file_:
            file_.write(content)
        os.chmod(path, 511)  # nosec

    return fun_save


def create_log_path(name, execution_retry=False):
    """
    Creating a new folder in configured log path.
    If folder exists, a suffix number is added to that folder.
    """
    name = normalize_filename(name)
    if sys.version_info < (3, 0):
        path = os.path.join(get_env('logs').decode('utf8'), str(name))
    else:
        path = os.path.join(get_env('logs'), str(name))
    initial_path = path
    scenario_outline_index = 1
    while os.path.exists(path):
        if execution_retry:
            return path
        path = initial_path + u'_' + str(scenario_outline_index)
        scenario_outline_index += 1
    os.makedirs(path)
    return path


def get_error_message(message_error):
    """"Retrieve errors in unicode format, removing invalid characters"""
    if not message_error:
        return u''
    if isinstance(message_error, Exception):
        if hasattr(message_error, 'message'):
            # noinspection PyBroadException
            try:
                message_error = traceback.format_tb(message_error.message)
            except BaseException:
                message_error = repr(message_error.message)
        if hasattr(message_error, 'exc_traceback'):
            message_error = traceback.format_tb(message_error.exc_traceback)
    elif not isinstance(message_error, str):
        message_error = repr(message_error)
    return u'\n'.join(
        [16 * u' ' + line for line in text(message_error).split('\n')]
    ).strip()


def text(value, encoding=None, errors=None):
    """Convert into a unicode string.
    :param value:  Value to convert into a unicode string (bytes, str, object).
    :param encoding: convertion encoding
    :param errors:
    :return: Unicode string
    """
    if value:
        value = value.name if isinstance(value, Status) else value.replace('\\', '/')
    if encoding is None:
        encoding = 'unicode-escape'
    if errors is None:
        errors = 'replace'

    if isinstance(value, str):
        # -- PASS-THROUGH UNICODE (efficiency):
        return value
    elif isinstance(value, bytes):
        return str(value, encoding, errors)
    elif isinstance(value, bytes):
        # -- MAYBE: filename, path, etc.
        try:
            return value.decode(sys.getfilesystemencoding())
        except UnicodeError:
            return value.decode('utf-8', 'replace')
    else:
        # -- CONVERT OBJECT TO TEXT:
        try:
            output_text = str(value)
        except UnicodeError as e:
            output_text = str(e)
        return output_text


def normalize_filename(input_name):
    """
    Removes invalid filename characters like '<>:"/\\| ?*'
    inputName = string or unicode object.
    """
    valid_name = None
    try:
        if sys.version_info[0] == 2:
            if isinstance(input_name, str):
                if isinstance(input_name, str):
                    input_name = text(input_name)
            else:
                raise TypeError
            if not input_name:
                return u''
            # xrange has been replaced for range
            characters = ''.join(map(chr, range(255)))
            reserved_characters = '<>:"/\\|?*'
            for character in reserved_characters:
                characters = characters.replace(character, '')
            valid_name = ''.join(char for char in input_name if char in characters)
            valid_name = unicodedata.normalize('NFKD', valid_name).encode(
                'ascii', 'ignore'
            )
            valid_name = string.capwords(valid_name)
            valid_name = valid_name.replace(' ', '_')
            if isinstance(valid_name, str):
                valid_name = text(valid_name)
        if sys.version_info[0] == 3:
            if isinstance(input_name, str):
                pass
            else:
                raise TypeError
            characters = ''.join(chr(i) for i in range(255))
            reserved_characters = '<>:"/\\|?*'
            for character in reserved_characters:
                characters = characters.replace(character, '')
            valid_name = ''.join(char for char in input_name if char in characters)
            valid_name = unicodedata.normalize('NFKD', valid_name).encode(
                'ascii', 'ignore'
            )
            if isinstance(valid_name, str):
                valid_name = string.capwords(valid_name)
            else:
                valid_name = bytes.title(valid_name)
            if isinstance(valid_name, str):
                valid_name = valid_name.replace(' ', '_')
            else:
                valid_name = valid_name.replace(b' ', b'_')
            if isinstance(valid_name, str):
                valid_name = bytes(valid_name, encoding='UTF-8')
        if isinstance(valid_name, bytes):
            valid_name = valid_name.decode('utf8')
        return valid_name
    except TypeError:
        err_msg = 'Input should be str or unicode, but received a: {}'.format(
            type(input_name)
        )
        print(err_msg)
        return

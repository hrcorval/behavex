import logging
import sys


def before_all(context):
    logging.info('before_all')
    context.behave_hook = context.config.userdata.get('crashing_behave_hook', '')
    crash_hook_if_specified(context, 'before_all')

def before_feature(context, feature):
    logging.info('before_feature')
    crash_hook_if_specified(context, 'before_feature')

def before_scenario(context, scenario):
    logging.info('before_scenario')
    crash_hook_if_specified(context, 'before_scenario')

def before_step(context, step):
    logging.info('before_step')
    crash_hook_if_specified(context, 'before_step')

def before_tag(context, tag):
    logging.info('before_tag')
    crash_hook_if_specified(context, 'before_tag')

def after_tag(context, tag):
    crash_hook_if_specified(context, 'after_tag')

def after_step(context, step):
    crash_hook_if_specified(context, 'after_step')

def after_scenario(context, scenario):
    crash_hook_if_specified(context, 'after_scenario')

def after_feature(context, feature):
    crash_hook_if_specified(context, 'after_feature')

def after_all(context):
    crash_hook_if_specified(context, 'after_all')

def crash_hook_if_specified(context, hook):
    if hook in context.behave_hook:
        print('Making the test crash in {} hook'.format(hook))
        0/0

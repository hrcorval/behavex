import logging
import sys


def before_all(context):
    logging.info('before_all')
    context.behave_hook = context.config.userdata.get('crashing_behave_hook', '')
    crash_hook_if_specified(context, 'before_all')

def before_feature(context, feature):
    logging.info('before_feature')
    crash_hook_if_specified(context, 'before_feature', feature.tags)

def before_scenario(context, scenario):
    logging.info('before_scenario')
    crash_hook_if_specified(context, 'before_scenario', scenario.effective_tags)

def before_step(context, step):
    logging.info('before_step')
    crash_hook_if_specified(context, 'before_step', context.scenario.effective_tags)

def before_tag(context, tag):
    logging.info('before_tag')
    crash_hook_if_specified(context, 'before_tag', [tag])

def after_tag(context, tag):
    crash_hook_if_specified(context, 'after_tag', [tag])

def after_step(context, step):
    crash_hook_if_specified(context, 'after_step', context.scenario.effective_tags)

def after_scenario(context, scenario):
    crash_hook_if_specified(context, 'after_scenario', scenario.effective_tags)

def after_feature(context, feature):
    crash_hook_if_specified(context, 'after_feature', feature.tags)

def after_all(context):
    crash_hook_if_specified(context, 'after_all')

def crash_hook_if_specified(context, hook, tags=None):
    crashing_tag = context.config.userdata.get('crashing_tag')
    if crashing_tag and tags is not None and crashing_tag not in tags:
        return
    if hook in context.behave_hook:
        print('Making the test crash in {} hook'.format(hook))
        0/0

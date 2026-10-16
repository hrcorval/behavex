# -*- coding: utf-8 -*-
""" Create environment variables related to the framework path and config,
    that are needed in framework modules.
"""
# __future__ import absolute_import  added for compatibility
from __future__ import absolute_import

import os

# Set the framework path
os.environ['BEHAVEX_PATH'] = os.path.dirname(os.path.realpath(__file__))
# Set the features path
os.environ['FEATURES_PATH'] = os.environ.get('FEATURES_PATH', 'features')

__all__ = [
    'BehaveXRunner',
    'ProgressEvent',
    'RunResult',
    'RunSummary',
    'FeatureResult',
    'ScenarioResult',
    'StepResult',
    'BackgroundResult',
]


def __getattr__(name):
    # Lazy, so the CLI and every spawned worker skip pydantic and the API
    if name not in __all__:
        raise AttributeError("module 'behavex' has no attribute {!r}".format(name))
    from behavex import api, models
    return getattr(api if name == 'BehaveXRunner' else models, name)

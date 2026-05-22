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

try:
    from behavex.api import BehaveXRunner  # noqa: E402
    from behavex.models import (  # noqa: E402
        BackgroundResult,
        FeatureResult,
        RunResult,
        RunSummary,
        ScenarioResult,
        StepResult,
    )
    __all__ = [
        'BehaveXRunner',
        'RunResult',
        'RunSummary',
        'FeatureResult',
        'ScenarioResult',
        'StepResult',
        'BackgroundResult',
    ]
except ImportError:
    # pydantic not installed — API surface unavailable, CLI still works normally
    __all__ = []


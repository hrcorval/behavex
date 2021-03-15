# -*- coding: UTF -*-
"""
/*
* BehaveX - Agile test wrapper on top of Behave (BDD)
*/

Provides support functionality to retry scenarios a number of times before
reporting it as failed. This functionality can be helpful when tests are
executed in a unreliable server/network infrastructure.
EXAMPLE:
.. sourcecode:: gherkin
    # -- FILE: features/alice.feature
    # TAG:  Feature or Scenario/ScenarioOutline with @autoretry
    # NOTE: If you tag the feature, all its scenarios are retried.
    @autoretry
    Feature: Use unreliable Server infrastructure
        Scenario: ...
.. sourcecode:: python
    # -- FILE: features/environment.py
    from behave.contrib.scenario_autoretry import run_scenario_with_retries
    def before_feature(context, feature):
        for scenario in feature.scenarios:
            if "AUTORETRY" in scenario.effective_tags:
                run_scenario_with_retries(scenario, max_attempts=2)
.. see also::
    * https://github.com/behave/behave/pull/328
    * https://github.com/hypothesis/smokey/blob/sauce-reliability/smokey/features/environment.py
"""

from __future__ import print_function
# __future__ and six are added to maintain compatibility
from __future__ import absolute_import
import functools

from behave.model import ScenarioOutline
from behavex.reports.report_utils import normalize_filename
from behavex.conf_mgr import set_env
from six.moves import range


def run_scenario_with_retries(scenario, max_attempts=3):
    """Monkey-patches :func:`~behave.model.Scenario.run()` to auto-retry a
    scenario that fails. The scenario is retried a number of times
    before its failure is accepted.
    This is helpful when the test infrastructure (server/network environment)
    is unreliable (which should be a rare case).
    :param scenario:        Scenario or ScenarioOutline to patch.
    :param max_attempts:    How many times the scenario can be run.
    """
    def retry_scenario_on_failure(scenario_run, *args, **kwargs):
        """
        Scenario run with retries.

        :param scenario_run:
        :param args:
        :param kwargs:
        :return:
        """
        set_env('autoretry_attempt', str(0))
        for attempt in range(1, max_attempts + 1):
            if not scenario_run(*args, **kwargs):
                return False    # -- NOT-FAILED = PASSED
            if attempt < max_attempts:
                set_env("autoretry", normalize_filename(scenario.name))
                set_env('autoretry_attempt', str(attempt))
        return True

    if isinstance(scenario, ScenarioOutline):
        scenario_outline = scenario
        for scenario in scenario_outline.scenarios:
            scenario_run = scenario.run
            scenario.run = functools.partial(retry_scenario_on_failure, scenario_run)
    else:
        scenario_run = scenario.run
        scenario.run = functools.partial(retry_scenario_on_failure, scenario_run)

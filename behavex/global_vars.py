# -*- coding: utf-8 -*-
import os
import time


class GlobalVars:
    def __init__(self):
        self._execution_path = os.environ.get('BEHAVEX_PATH')
        self._report_filenames = {
            'report_json': 'report.json',
            'report_overall': 'overall_status.json',
            'report_failures': 'failing_scenarios.txt',
        }
        self._behave_tags_file = os.path.join('behave', 'behave.tags')
        self._jinja_templates_path = os.path.join(
            self._execution_path, 'outputs', 'jinja'
        )
        self._jinja_templates = {
            'main': 'main.jinja2',
            'steps': 'steps.jinja2',
            'xml': 'xml.jinja2',
            'xml_json': 'xml_json.jinja2',
            'manifest': 'manifest.jinja2',
        }
        self._retried_scenarios = {}
        self._steps_definitions = {}
        self._rerun_failures = False
        self._progress_bar_instance = None
        self._execution_start_time = time.time()
        self._execution_end_time = None

    @property
    def execution_path(self):
        return self._execution_path

    @property
    def report_filenames(self):
        return self._report_filenames

    @property
    def behave_tags_file(self):
        return self._behave_tags_file

    @property
    def jinja_templates_path(self):
        return self._jinja_templates_path

    @property
    def jinja_templates(self):
        return self._jinja_templates

    @property
    def retried_scenarios(self):
        return self._retried_scenarios

    @retried_scenarios.setter
    def retried_scenarios(self, feature_name):
        self._retried_scenarios[feature_name] = []

    @property
    def steps_definitions(self):
        return self._steps_definitions

    @property
    def rerun_failures(self):
        return self._rerun_failures

    @rerun_failures.setter
    def rerun_failures(self, rerun_failures):
        self._rerun_failures = rerun_failures

    @property
    def progress_bar_instance(self):
        return self._progress_bar_instance

    @progress_bar_instance.setter
    def progress_bar_instance(self, progress_bar_instance):
        self._progress_bar_instance = progress_bar_instance

    @property
    def execution_start_time(self):
        return self._execution_start_time

    @execution_start_time.setter
    def execution_start_time(self, execution_start_time):
        self._execution_start_time = execution_start_time

    @property
    def execution_elapsed_time(self):
        return time.time() - self._execution_start_time

    @property
    def execution_end_time(self):
        if not self._execution_end_time:
            self._execution_end_time = time.time()
        return self._execution_end_time

global_vars = GlobalVars()

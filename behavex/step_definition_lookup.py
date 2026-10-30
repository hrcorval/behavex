import contextlib
import io
import multiprocessing
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from types import SimpleNamespace

from behave.configuration import Configuration
from behave.runner import ConfigError, Runner

from behavex.behave_args import set_behave_arguments
from behavex.conf_mgr import ConfigRun, get_param
from behavex.global_vars import global_vars


def single_behave_run_paths(features_path, features):
    """Return the paths one behave process runs, or None when each feature runs in its own worker."""
    if get_param('parallel_processes') > 1 and not get_param('dry_run'):
        return None
    return features_path.split(',') if global_vars.rerun_failures else list(features)


def find_undefined_step_texts(features, scenarios):
    """Return, per scenario, the steps behave cannot match, loading the steps folder run() would use."""
    single_run_paths = single_behave_run_paths(os.environ['FEATURES_PATH'], features)
    steps_folder_by_lookup_path = {}
    behave_args_and_scenarios_by_steps_folder = {}
    steps_folder_per_scenario = []
    for scenario in scenarios:
        # A single behave run takes its steps folder from the first path it gets
        if single_run_paths is not None:
            steps_lookup_path = single_run_paths[0]
        else:
            steps_lookup_path = os.path.dirname(scenario.filename)
        if steps_lookup_path not in steps_folder_by_lookup_path:
            # A parallel worker's arguments: with no_report, the single-run ones create a JUnit folder
            behave_args = set_behave_arguments(steps_lookup_path, multiprocess=True, config=ConfigRun())
            try:
                steps_folder = behave_runner_after_setup_paths(behave_args).base_dir
            except ConfigError as error:
                sys.exit('Could not find the step definitions: {}'.format(error))
            steps_folder_by_lookup_path[steps_lookup_path] = steps_folder
            behave_args_and_scenarios_by_steps_folder.setdefault(steps_folder, (behave_args, []))
        steps_folder = steps_folder_by_lookup_path[steps_lookup_path]
        behave_args_and_scenarios_by_steps_folder[steps_folder][1].append(scenario)
        steps_folder_per_scenario.append(steps_folder)
    undefined_steps_by_steps_folder = {}
    for steps_folder, (behave_args, folder_scenarios) in behave_args_and_scenarios_by_steps_folder.items():
        distinct_steps = {(step.step_type, step.name) for scenario in folder_scenarios for step in scenario.all_steps}
        # A fresh process per steps folder: a step module imported once stays cached in sys.modules,
        # so loading the same steps again in this process would not register them again
        with ProcessPoolExecutor(max_workers=1, mp_context=multiprocessing.get_context('spawn')) as executor:
            undefined_steps, error = executor.submit(
                _find_undefined_steps_in_fresh_process, behave_args, distinct_steps).result()
        if error:
            sys.exit('Could not load the step definitions in {}: {}'.format(steps_folder, error))
        undefined_steps_by_steps_folder[steps_folder] = undefined_steps
    return [['{} {}'.format(step.keyword.strip(), step.name) for step in scenario.all_steps
             if (step.step_type, step.name) in undefined_steps_by_steps_folder[steps_folder]]
            for scenario, steps_folder in zip(scenarios, steps_folder_per_scenario)]


def behave_runner_after_setup_paths(behave_args):
    """Return a behave Runner whose base_dir holds its steps folder; raises ConfigError when there is none."""
    behave_runner = Runner(Configuration(command_args=behave_args))
    behave_runner.setup_paths()
    return behave_runner


def _find_undefined_steps_in_fresh_process(behave_args, steps):
    """Return (the (step_type, name) pairs no step definition matches, None), or (None, the error)."""
    from behave.step_registry import registry
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            behave_runner = behave_runner_after_setup_paths(behave_args)
            with behave_runner.path_manager:
                behave_runner.load_hooks()
                behave_runner.load_step_definitions()
    except (Exception, SystemExit) as error:
        # A user's exception may not pickle back to the parent
        return None, '{}: {}'.format(type(error).__name__, error)
    return {(step_type, name) for step_type, name in steps
            if registry.find_match(SimpleNamespace(step_type=step_type, name=name)) is None}, None

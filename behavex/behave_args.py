import multiprocessing
import os
import re
from tempfile import gettempdir

from behave.configuration import Configuration
from behave.runner import Runner

from behavex.arguments import BEHAVE_ARGS, BEHAVEX_ARGS
from behavex.conf_mgr import get_env, get_param
from behavex.global_vars import global_vars
from behavex.utils import get_name_filters


def as_non_option(path):
    # behave reads a relative path starting with "-" (behave's own filenames included) as an option
    return os.path.abspath(path) if path.startswith('-') else path


def single_behave_run_paths(features_path, features):
    """Return the paths one behave process runs, or None when each feature runs in its own worker."""
    if get_param('parallel_processes') > 1 and not get_param('dry_run'):
        return None
    return features_path.split(',') if global_vars.rerun_failures else list(features)


def behave_runner_after_setup_paths(behave_args):
    """Return a behave Runner whose base_dir holds its steps folder; raises ConfigError when there is none."""
    behave_runner = Runner(Configuration(command_args=behave_args))
    behave_runner.setup_paths()
    return behave_runner


def set_behave_arguments(features_path, multiprocess, execution_id=None, feature=None, scenario_line=None, config=None):
    """
    Set the arguments for Behave framework based on the given parameters.

    Args:
        features_path (str): Path to the features.
        multiprocess (bool): Whether to use multiprocessing.
        execution_id (str): Execution ID.
        feature (Feature): Feature object.
        scenario_line (int): Scenario line.
        config (ConfigRun): Configuration object.

    Returns:
        list: List of arguments to be used when executing Behave.
    """
    arguments = []
    output_folder = config.get_env('OUTPUT') if config else get_env('OUTPUT')
    if multiprocess:
        updated_features_path = features_path if not feature else feature
        updated_features_path = updated_features_path if not scenario_line else "{}:{}".format(updated_features_path, scenario_line)
        arguments.append(as_non_option(updated_features_path))
        arguments.append('--no-summary')
        worker_id = multiprocessing.current_process().name.split('-')[-1]

        # Note: --outfile removed since we get execution results directly from runner

        arguments.append('-D')
        arguments.append(f'worker_id={worker_id}')
    else:
        if type(features_path) is list:
            for feature_path in features_path:
                arguments.append(as_non_option(feature_path))
        else:
            arguments.append(as_non_option(features_path))
        if get_param('dry_run'):
            arguments.append('--no-summary')
            arguments.append('--dry-run')
        else:
            arguments.append('--summary')
        arguments.append('--junit-directory')
        if get_param('no_report'):
            behave_outdir = os.path.join(gettempdir(), 'bhx_behave')
            os.makedirs(behave_outdir, exist_ok=True)
            arguments.append(behave_outdir)
        else:
            arguments.append(output_folder)
        # Note: --outfile removed since we get execution results directly from runner
        arguments.append('-D')
        arguments.append(f'worker_id=0')
    arguments.append('--no-skipped')
    arguments.append('--no-junit')
    run_wip_tests = False
    env_tags = get_env('tags')

    # Check if we're using v2 tag expressions
    tag_version = global_vars.tag_expression_version

    if env_tags and tag_version == 'v2':
        # For v2 expressions, combine user expression with default exclusions
        user_expression = env_tags.replace(';', ' and ')  # Convert semicolons to AND

        # Normalize case for v2 keywords (Behave parser expects lowercase)
        user_expression = re.sub(r'\bAND\b', 'and', user_expression, flags=re.IGNORECASE)
        user_expression = re.sub(r'\bOR\b', 'or', user_expression, flags=re.IGNORECASE)
        user_expression = re.sub(r'\bNOT\b', 'not', user_expression, flags=re.IGNORECASE)

        # Check if WIP tests should be run
        if 'WIP' in env_tags.upper() or '@WIP' in env_tags.upper():
            run_wip_tests = True

        # Build combined v2 expression with default exclusions
        exclusions = []
        if not run_wip_tests:
            exclusions.append('not @WIP')
        exclusions.append('not @MANUAL')

        if exclusions:
            combined_expression = f"({user_expression}) and {' and '.join(exclusions)}"
        else:
            combined_expression = user_expression

        # Add the combined expression as a single tag argument
        arguments.append('--tags')
        arguments.append(combined_expression)

    elif env_tags:
        # For v1 expressions, use the original logic
        tags = env_tags.split(';')
        for tag in tags:
            arguments.append('--tags')
            arguments.append(tag)
            if tag.upper() in ['WIP', '@WIP']:
                run_wip_tests = True

        # Add default exclusions in v1 format
        if not run_wip_tests:
            arguments.append('--tags')
            arguments.append('~@WIP')
        arguments.append('--tags')
        arguments.append('~@MANUAL')
    else:
        # No user tags, just add default exclusions in v1 format
        arguments.append('--tags')
        arguments.append('~@WIP')
        arguments.append('--tags')
        arguments.append('~@MANUAL')

    # Handle output based on execution mode
    if multiprocess:
        # In multiprocess: suppress output entirely — mixing output from concurrent processes
        # in the console would produce unreadable interleaved text
        arguments.append('--format')
        arguments.append('null')
    # In single process: no --outfile and no --format override, so behave writes
    # to stdout directly using the default pretty formatter (or any user-specified formatter)

    args_sys = config.args if config else None
    set_args_captures(arguments, args_sys)
    if args_sys and args_sys.no_snippets:
        arguments.append('--no-snippets')
    for arg in BEHAVE_ARGS:
        value_arg = getattr(args_sys, arg) if hasattr(args_sys, arg) else False
        if arg == 'include':
            if multiprocess or not value_arg:
                continue
            else:
                features_path = os.path.abspath(os.environ['FEATURES_PATH'])
                value_arg = value_arg.replace(features_path, 'features').replace(
                    '\\', '\\\\'
                )
        if arg == 'define':
            if not value_arg:
                value_arg = get_param('define')
            if isinstance(value_arg, str) and value_arg:
                value_arg = [value_arg]
            if value_arg:
                for key_value in value_arg:
                    arguments.append('--define={}'.format(key_value))
        if arg == 'name':
            for name in get_name_filters():
                arguments.append('--name={}'.format(name))
            continue
        if arg == 'exclude':
            if get_param('exclude'):
                arguments.append('--exclude={}'.format(get_param('exclude')))
            continue
        if value_arg and arg not in BEHAVEX_ARGS and arg != 'define':
            arguments.append('--{}'.format(arg.replace('_', '-')))
            if value_arg and not isinstance(value_arg, bool):
                arguments.append(value_arg)
                os.environ[arg] = str(value_arg)
    return arguments


def set_args_captures(args, args_sys):
    """
    Set the capture arguments for Behave.

    Args:
        args (list): List of arguments.
        args_sys (Namespace): Parsed command-line arguments.
    """
    for default_arg in ['capture', 'capture_stderr', 'logcapture']:
        if not getattr(args_sys, 'no_{}'.format(default_arg)):
            args.append('--no-{}'.format(default_arg.replace('_', '-')))

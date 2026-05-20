import logging
import os
import shutil
import subprocess
import tempfile

from behave import given, then, when

root_project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
secondary_features_path = os.path.join(root_project_path, 'tests', 'features', 'secondary_features')

# Env vars that parent behavex injects into its own process.  The child
# subprocess must NOT inherit them — they would override the child's own config
# discovery and output paths, causing spurious failures.
_PARENT_BEHAVEX_ENV_VARS = frozenset({
    'CONFIG', 'OUTPUT', 'TAGS', 'PARALLEL_SCHEME',
    'PARALLEL_PROCESSES', 'FEATURES_PATH', 'TEMP', 'LOGS', 'LOGGING_LEVEL',
})


def _clean_child_env():
    """Return a copy of os.environ without parent-behavex-injected variables."""
    return {k: v for k, v in os.environ.items() if k not in _PARENT_BEHAVEX_ENV_VARS}


def _make_config_dir(context):
    if not hasattr(context, 'config_dir'):
        # Parent behavex overrides TEMP to its own output/temp dir.  We MUST
        # pass an explicit dir= so the config test dirs land in a short system
        # path, not nested inside output/temp.  Long nested paths break the
        # child's multiprocessing SyncManager socket with AF_UNIX path too long.
        if os.path.isdir('/tmp'):
            base_tmp = '/tmp'  # POSIX (Linux / macOS)
        else:
            # Windows: create the config dir on the same drive as the feature files.
            # Behave <=1.2.6 calls os.path.relpath(feature_path, cwd) without
            # catching ValueError, which fails when cwd and feature path are on
            # different drives (e.g. D:\ repo vs C:\Temp on GitHub Actions runners).
            drive, _ = os.path.splitdrive(secondary_features_path)
            base_tmp = drive + os.sep + 'bhx_cfg_tmp'
            os.makedirs(base_tmp, exist_ok=True)
        config_dir = tempfile.mkdtemp(prefix='bhx_cfg_test_', dir=base_tmp)
        context.add_cleanup(shutil.rmtree, config_dir, ignore_errors=True)
        context.config_dir = config_dir
    return context.config_dir


def _write_config_file(directory, filename, content):
    path = os.path.join(directory, filename)
    with open(path, 'w') as f:
        f.write(content)
    return path


# ─────────────────────────────────────────────────────────────────────────────
# Given steps
# ─────────────────────────────────────────────────────────────────────────────

@given('a "{filename}" config file with param "{param}" set to "{value}"')
def given_config_file_with_param(context, filename, param, value):
    config_dir = _make_config_dir(context)
    content = f'[params]\n{param} = {value}\n'
    _write_config_file(config_dir, filename, content)


@given('a "{filename}" config file with section "{section}" param "{param}" set to "{value}"')
def given_config_file_with_section_param(context, filename, section, param, value):
    config_dir = _make_config_dir(context)
    content = f'{section}\n{param} = {value}\n'
    _write_config_file(config_dir, filename, content)


@given('an explicit config file with param "{param}" set to "{value}"')
def given_explicit_config_file(context, param, value):
    config_dir = _make_config_dir(context)
    content = f'[params]\n{param} = {value}\n'
    explicit_path = _write_config_file(config_dir, 'explicit_config.cfg', content)
    context.extra_cli_args = getattr(context, 'extra_cli_args', []) + ['--config', explicit_path]


@given('a "{filename}" config file with params')
def given_config_file_with_params_table(context, filename):
    config_dir = _make_config_dir(context)
    content = '[params]\n' + ''.join(f'{row["param"]} = {row["value"]}\n' for row in context.table)
    _write_config_file(config_dir, filename, content)


@given('the CLI args "{cli_args}"')
def given_extra_cli_args(context, cli_args):
    context.extra_cli_args = getattr(context, 'extra_cli_args', []) + cli_args.split()


# ─────────────────────────────────────────────────────────────────────────────
# When steps — single pattern avoids Behave ambiguity with greedy {params}
# ─────────────────────────────────────────────────────────────────────────────

@given('no explicit output folder is provided')
def given_no_output_folder(context):
    context.skip_output_arg = True


@when('I run behavex from the config file directory for feature "{feature_name}"')
def when_run_from_config_dir(context, feature_name):
    feature_path = os.path.join(secondary_features_path, feature_name)
    extra = getattr(context, 'extra_cli_args', [])
    skip_output = getattr(context, 'skip_output_arg', False)
    if skip_output:
        cmd = ['behavex', feature_path] + extra
        context.output_path = None
    else:
        output_path = os.path.join(context.config_dir, 'output')
        context.output_path = output_path
        cmd = ['behavex', feature_path, '-o', output_path] + extra
    child_env = _clean_child_env()
    context.result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=context.config_dir, env=child_env
    )
    if context.result.returncode != 0:
        logging.error(
            f"Child behavex process failed (rc={context.result.returncode})\n"
            f"CMD: {' '.join(cmd)}\n"
            f"CWD: {context.config_dir}\n"
            f"STDOUT:\n{context.result.stdout}\n"
            f"STDERR:\n{context.result.stderr}"
        )
    context.extra_cli_args = []
    context.skip_output_arg = False


# ─────────────────────────────────────────────────────────────────────────────
# Then steps
# ─────────────────────────────────────────────────────────────────────────────

@then('I should not see the following in the behavex console output')
def then_output_not_contains(context):
    for row in context.table:
        assert row['output_line'] not in context.result.stdout, (
            f"Expected NOT to find '{row['output_line']}' in output but it was present.\n"
            f"Full output:\n{context.result.stdout}"
        )

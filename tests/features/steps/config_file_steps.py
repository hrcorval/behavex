import os
import shutil
import subprocess
import tempfile

from behave import given, then, when

root_project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
secondary_features_path = os.path.join(root_project_path, 'tests', 'features', 'secondary_features')


def _make_config_dir(context):
    if not hasattr(context, 'config_dir'):
        config_dir = tempfile.mkdtemp(prefix='bhx_cfg_test_')
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
    # Store the --config flag so the @when step picks it up automatically.
    context.extra_cli_args = getattr(context, 'extra_cli_args', []) + ['--config', explicit_path]


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
    context.result = subprocess.run(cmd, capture_output=True, text=True, cwd=context.config_dir)
    if context.result.returncode != 0:
        import logging
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

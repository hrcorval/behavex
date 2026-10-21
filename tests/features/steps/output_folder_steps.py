import os

from behave import then, when
from execution_steps import execute_command
from sys_path_resolution_steps import _clean_child_env, _make_project_dir


@when('I run the behavex command in a new project with the output folder "{output_folder}"')
def when_run_in_new_project_with_output_folder(context, output_folder):
    project_dir = _make_project_dir(context)
    steps_path = os.path.join(project_dir, 'features', 'steps')
    os.makedirs(steps_path)
    with open(os.path.join(project_dir, 'features', 'passing.feature'), 'w') as feature_file:
        feature_file.write('Feature: Passing\n\n  Scenario: Passing\n    Given a passing step\n')
    with open(os.path.join(steps_path, 'steps.py'), 'w') as steps_file:
        steps_file.write("from behave import given\n\n\n@given('a passing step')\ndef step_passing(context):\n    pass\n")
    execute_command(context, ['behavex', 'features', '-o', output_folder], env=_clean_child_env(), cwd=project_dir)


@then('I should see the project features folder was kept')
def then_project_features_folder_kept(context):
    for kept_path in (os.path.join('features', 'passing.feature'), os.path.join('features', 'steps', 'steps.py')):
        assert os.path.exists(os.path.join(context.project_dir, kept_path)), f"{kept_path} was deleted"

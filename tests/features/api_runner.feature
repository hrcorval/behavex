Feature: BehaveXRunner Python API
  Verify that BehaveX can be invoked programmatically via BehaveXRunner
  without using the CLI.

  @API_RUNNER_001
  Scenario: BehaveXRunner returns passed=True for a passing test suite
    When I run BehaveXRunner with passing tests
    Then the RunResult exit_code should be "0"
    And the RunResult passed should be "True"

  @API_RUNNER_002
  Scenario: BehaveXRunner returns passed=False for a failing test suite
    When I run BehaveXRunner with failing tests
    Then the RunResult exit_code should be "1"
    And the RunResult passed should be "False"

  @API_RUNNER_003
  Scenario: BehaveXRunner applies tag filtering to limit executed scenarios
    When I run BehaveXRunner with passing tests filtered by tag "@PASSING_TAG_1"
    Then the RunResult exit_code should be "0"
    And I should see "1 scenario passed" in the BehaveXRunner output

  @API_RUNNER_004
  Scenario: BehaveXRunner preserves the output_folder in RunResult
    When I run BehaveXRunner with passing tests and a configured output folder
    Then the RunResult output_folder matches the configured output folder
    And the RunResult exit_code should be "0"

  @API_RUNNER_005
  Scenario: BehaveXRunner runs tests in parallel when parallel_processes is set
    When I run BehaveXRunner with passing tests using "2" parallel processes and "scenario" parallel scheme
    Then the RunResult exit_code should be "0"
    And I should see "Running parallel scenarios" in the BehaveXRunner output

  @API_RUNNER_006
  Scenario: BehaveXRunner with no_report=True does not create an output folder
    When I run BehaveXRunner with passing tests, no_report enabled, and a configured output folder
    Then the RunResult exit_code should be "0"
    And the configured output folder should not exist on the filesystem

  @API_RUNNER_007
  Scenario: BehaveX CLI works normally without pydantic installed
    When I run the behavex CLI without pydantic available
    Then the CLI exits successfully
    And pydantic was not required

  @API_RUNNER_008
  Scenario: BehaveXRunner raises a clear error when pydantic is not installed
    When I import BehaveXRunner without pydantic available
    Then an ImportError is raised mentioning "pip install 'behavex[api]'"

  @API_RUNNER_MODEL_001
  Scenario: RunResult.features is populated after a run with output folder
    When I run BehaveXRunner with passing tests and a configured output folder
    Then the RunResult has at least "1" feature
    And the RunResult first feature name is "Passing Tests"
    And the RunResult first feature status is "passed"

  @API_RUNNER_MODEL_002
  Scenario: RunResult.summary reflects all passing scenarios
    When I run BehaveXRunner with passing tests and a configured output folder
    Then the RunResult summary total is greater than "0"
    And the RunResult summary has no failed scenarios
    And the RunResult summary has no skipped scenarios

  @API_RUNNER_MODEL_003
  Scenario: RunResult.summary counts a failing scenario correctly
    When I run BehaveXRunner with failing tests and a configured output folder
    Then the RunResult summary total is "1"
    And the RunResult summary failed is "1"
    And the RunResult summary passed is "0"

  @API_RUNNER_MODEL_004
  Scenario: RunResult.failed_scenarios contains failing scenario details
    When I run BehaveXRunner with failing tests and a configured output folder
    Then the RunResult has "1" failed scenario
    And the RunResult first failed scenario name is "This test should fail"
    And the RunResult first failed scenario has error details

  @API_RUNNER_MODEL_005
  Scenario: RunResult.features is empty when no_report is enabled
    When I run BehaveXRunner with passing tests, no_report enabled, and a configured output folder
    Then the RunResult has "0" features

  @API_RUNNER_MODEL_006
  Scenario: ScenarioResult.tags is populated from the report
    When I run BehaveXRunner with passing tests and a configured output folder
    Then at least one scenario in the RunResult has tags

  @API_RUNNER_009
  Scenario: BehaveXRunner with multiple tags applies AND logic
    When I run BehaveXRunner with passing tests filtered by tags "@PASSING_TAG_3" and "@PASSING_TAG_3_1"
    Then the RunResult exit_code should be "0"
    And I should see "1 scenario passed" in the BehaveXRunner output

  @API_RUNNER_010
  Scenario: BehaveXRunner with dry_run=True does not execute steps
    When I run BehaveXRunner with dry_run enabled
    Then the RunResult exit_code should be "0"
    And I should see "Dry run completed" in the BehaveXRunner output

  @API_RUNNER_RUN_ID_001
  Scenario: RunResult exposes a unique run_id for each execution
    When I run BehaveXRunner with passing tests
    Then the RunResult run_id is a valid UUID

  @API_RUNNER_RUN_ID_002
  Scenario: Each BehaveXRunner.run() call produces a different run_id
    When I run BehaveXRunner with passing tests twice
    Then the two run_ids are different
    And both runs completed successfully

  @API_RUNNER_011
  Scenario: BehaveXRunner with name filter limits executed scenarios by scenario name
    When I run BehaveXRunner with passing tests filtered by name "This test should pass and does not contain a tag"
    Then the RunResult exit_code should be "0"
    And I should see "1 scenario passed" in the BehaveXRunner output

  @API_RUNNER_012
  Scenario: BehaveXRunner with stop=True passes the stop flag to the runner
    When I run BehaveXRunner with failing tests and stop enabled
    Then the RunResult exit_code should be "1"

  @API_RUNNER_013
  Scenario: BehaveXRunner with define passes user-defined variables to scenarios
    When I run BehaveXRunner with userdata tests and define "test_udkey=test_udvalue"
    Then the RunResult exit_code should be "0"

  @API_RUNNER_014
  Scenario: BehaveXRunner with logging_level set does not break execution
    When I run BehaveXRunner with passing tests and logging_level "WARNING"
    Then the RunResult exit_code should be "0"

  @API_RUNNER_015
  Scenario: on_progress callback is invoked for each scenario in non-parallel mode
    When I run BehaveXRunner with passing tests and an on_progress callback
    Then the on_progress callback was called at least "3" times
    And each on_progress event has a non-empty scenario_name and feature_name
    And each on_progress event has a status of "passed"
    And the completed counter in on_progress events is strictly increasing

  @API_RUNNER_016
  Scenario: on_progress callback is invoked for each scenario in parallel mode
    When I run BehaveXRunner with passing tests using "2" parallel processes, "scenario" scheme, and an on_progress callback
    Then the on_progress callback was called at least "3" times
    And each on_progress event has a non-empty scenario_name and feature_name

  @API_RUNNER_017
  Scenario: exceptions raised inside on_progress callback do not affect the exit code
    When I run BehaveXRunner with passing tests and an on_progress callback that always raises
    Then the RunResult exit_code should be "0"

  @API_RUNNER_018
  Scenario: on_progress callback reports failed status for failing tests in non-parallel mode
    When I run BehaveXRunner with failing tests and an on_progress callback
    Then the on_progress callback was called at least "1" time
    And at least one on_progress event has a status of "failed"

  @API_RUNNER_019
  Scenario: on_progress callback is invoked for each scenario using feature parallel scheme
    When I run BehaveXRunner with passing tests using "2" parallel processes, "feature" scheme, and an on_progress callback
    Then the on_progress callback was called at least "3" times
    And each on_progress event has a non-empty scenario_name and feature_name

  @API_RUNNER_020
  Scenario: on_progress callback reports failed status for failing tests in parallel mode
    When I run BehaveXRunner with failing tests using "2" parallel processes, "scenario" scheme, and an on_progress callback
    Then the on_progress callback was called at least "1" time
    And at least one on_progress event has a status of "failed"

  @API_RUNNER_021
  Scenario: on_progress callback reports failed status for failing tests using feature parallel scheme
    When I run BehaveXRunner with failing tests using "2" parallel processes, "feature" scheme, and an on_progress callback
    Then the on_progress callback was called at least "1" time
    And at least one on_progress event has a status of "failed"

  @API_RUNNER_022
  Scenario: stop() called outside an active run does not raise
    When I call stop() on a BehaveXRunner that is not running
    Then no exception was raised

  @API_RUNNER_023
  Scenario: stop() called from a background thread during non-parallel run completes without error
    When I run BehaveXRunner with passing tests and call stop() from a background thread
    Then the RunResult exit_code should be "0"
    And no exception was raised

  @API_RUNNER_024
  Scenario: stop() called from a background thread during parallel run does not raise or deadlock
    When I run BehaveXRunner with passing tests in parallel and call stop() from a background thread
    Then no exception was raised

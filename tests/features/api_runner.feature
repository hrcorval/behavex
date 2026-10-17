Feature: BehaveXRunner Python API
  Verify that BehaveX can be invoked programmatically via BehaveXRunner
  without using the CLI.

  @API_RUNNER_001
  Scenario: BehaveXRunner returns passed=True for a passing test suite
    When I run BehaveXRunner with passing tests
    Then the RunResult exit_code should be "0"
    And the RunResult passed should be "True"
    And the RunResult stopped should be "False"

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
  Scenario: RunResult.output_folder is the resolved configured output folder
    When I run BehaveXRunner with passing tests and a configured output folder
    Then the RunResult output_folder is the absolute path of the configured output folder
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
  Scenario: RunResult.features is populated when no_report is enabled
    When I run BehaveXRunner with passing tests, no_report enabled, and a configured output folder
    Then the RunResult has at least "1" feature
    And the RunResult summary total is greater than "0"

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
  Scenario: BehaveXRunner with stop_on_failure=True passes the stop flag to the runner
    When I run BehaveXRunner with failing tests and stop_on_failure enabled
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
    Then the on_progress callback was called once per scenario in the RunResult summary
    And each on_progress event has a non-empty scenario_name and feature_name
    And each on_progress event has a status of "passed"
    And the completed_count in on_progress events is strictly increasing up to the summary total

  @API_RUNNER_016
  Scenario: on_progress callback is invoked for each scenario in parallel mode
    When I run BehaveXRunner with passing tests using "2" parallel processes, "scenario" scheme, and an on_progress callback
    Then the on_progress callback was called once per scenario in the RunResult summary
    And each on_progress event has a non-empty scenario_name and feature_name
    And the completed_count in on_progress events is strictly increasing up to the summary total

  @API_RUNNER_017
  Scenario: exceptions raised inside on_progress callback do not affect the exit code
    When I run BehaveXRunner with passing tests and an on_progress callback that always raises
    Then the RunResult exit_code should be "0"

  @API_RUNNER_025
  Scenario: an on_progress callback that raises once keeps receiving the remaining events
    When I run BehaveXRunner with passing tests and an on_progress callback that raises on its first call
    Then the RunResult exit_code should be "0"
    And the on_progress callback was called once per scenario in the RunResult summary

  @API_RUNNER_018
  Scenario: on_progress callback reports failed status for failing tests in non-parallel mode
    When I run BehaveXRunner with failing tests and an on_progress callback
    Then the on_progress callback was called once per scenario in the RunResult summary
    And at least one on_progress event has a status of "failed"

  @API_RUNNER_019
  Scenario: on_progress callback is invoked for each scenario using feature parallel scheme
    When I run BehaveXRunner with passing tests using "2" parallel processes, "feature" scheme, and an on_progress callback
    Then the on_progress callback was called once per scenario in the RunResult summary
    And each on_progress event has a non-empty scenario_name and feature_name
    And the completed_count in on_progress events is strictly increasing up to the summary total

  @API_RUNNER_020
  Scenario: on_progress callback reports failed status for failing tests in parallel mode
    When I run BehaveXRunner with failing tests using "2" parallel processes, "scenario" scheme, and an on_progress callback
    Then the on_progress callback was called once per scenario in the RunResult summary
    And at least one on_progress event has a status of "failed"

  @API_RUNNER_021
  Scenario: on_progress callback reports failed status for failing tests using feature parallel scheme
    When I run BehaveXRunner with failing tests using "2" parallel processes, "feature" scheme, and an on_progress callback
    Then the on_progress callback was called once per scenario in the RunResult summary
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

  @API_RUNNER_026
  Scenario: stop() called from on_progress cancels the scenarios a parallel run has not started
    When I run BehaveXRunner on "twelve_scenarios.feature" with "2" parallel processes, "scenario" scheme, and call stop() on progress event "1"
    Then the RunResult exit_code should be "0"
    And the RunResult stopped should be "True"
    And the RunResult passed should be "False"
    And the on_progress callback was called once per scenario in the RunResult summary
    And the RunResult summary total is less than "12"

  @API_RUNNER_043
  Scenario: stop() called from the last progress event does not mark a complete run as stopped
    When I run BehaveXRunner on "twelve_scenarios.feature" with "2" parallel processes, "scenario" scheme, and call stop() on progress event "12"
    Then the RunResult exit_code should be "0"
    And the RunResult stopped should be "False"
    And the RunResult passed should be "True"
    And the RunResult summary total is "12"

  @API_RUNNER_044
  Scenario Outline: stop() called during the serial phase of a parallel run skips the remaining serial units
    When I run BehaveXRunner on "serial_mix" with "2" parallel processes, "<scheme>" scheme, and call stop() on progress event "1"
    Then the RunResult stopped should be "True"
    And the RunResult passed should be "False"
    And the on_progress callback was called once per scenario in the RunResult summary
    And the RunResult summary total is less than "3"
    Examples:
      | scheme   |
      | scenario |
      | feature  |

  @API_RUNNER_047
  Scenario Outline: stop() called before a parallel run submits any work skips every scenario
    When I run BehaveXRunner on "stop_before_workers" with "2" parallel processes, "<scheme>" scheme, and call stop() while before_all_workers runs
    Then the RunResult stopped should be "True"
    And the RunResult passed should be "False"
    And the RunResult summary total is less than "4"
    Examples:
      | scheme   |
      | scenario |
      | feature  |

  @API_RUNNER_045
  Scenario Outline: on_progress fires for the @SERIAL scenarios of a parallel run
    When I run BehaveXRunner on @SERIAL and parallel scenarios using "2" parallel processes, "<scheme>" scheme, and an on_progress callback
    Then the RunResult summary total is "5"
    And the on_progress callback was called once per scenario in the RunResult summary
    And the completed_count in on_progress events is strictly increasing up to the summary total
    Examples:
      | scheme   |
      | scenario |
      | feature  |

  @API_RUNNER_027
  Scenario: repeated runs in one process do not accumulate tag filters
    When I run BehaveXRunner on passing tests in one process with tags "@PASSING_TAG_1", none, "@PASSING_TAG_2", none
    Then the in-process run totals are "1, 5, 1, 5"

  @API_RUNNER_030
  Scenario: repeated runs in one process each run their own paths
    When I run BehaveXRunner in one process on passing tests, then failing tests, then passing tests with "1" parallel processes
    Then the in-process run totals are "5, 1, 5"

  @API_RUNNER_031
  Scenario: repeated parallel runs in one process each run their own paths
    When I run BehaveXRunner in one process on passing tests, then failing tests, then passing tests with "2" parallel processes
    Then the in-process run totals are "5, 1, 5"

  @API_RUNNER_028
  Scenario: RunResult.summary counts a @MANUAL scenario as manual
    When I run BehaveXRunner with a feature holding one automated and one @MANUAL scenario
    Then the RunResult summary total is "2"
    And the RunResult summary passed is "1"
    And the RunResult summary manual is "1"
    And the RunResult summary counts add up to the total

  @API_RUNNER_029
  Scenario: the behavex CLI does not import the API models or pydantic
    When I run the behavex CLI on passing tests and list the loaded modules
    Then the CLI run loaded neither "behavex.models" nor "pydantic"

  @API_RUNNER_032
  Scenario: on_progress fires once per @AUTORETRY scenario, after its final attempt
    When I run BehaveXRunner on @AUTORETRY scenarios that pass on a retry or fail every attempt with an on_progress callback
    Then the RunResult exit_code should be "1"
    And the on_progress callback was called once per scenario in the RunResult summary
    And at least one on_progress event has a status of "passed"
    And at least one on_progress event has a status of "failed"
    And the completed_count in on_progress events is strictly increasing up to the summary total

  @API_RUNNER_046
  Scenario: on_progress fires once per @AUTORETRY scenario that ends in error, after its final attempt
    When I run BehaveXRunner on @AUTORETRY scenarios whose step raises an error or whose teardown fails on every attempt with an on_progress callback
    Then the RunResult summary total is "2"
    And the on_progress callback was called once per scenario in the RunResult summary
    And each on_progress event status matches the scenario's final status in the RunResult
    And at least one on_progress event has behave's error status

  @API_RUNNER_033
  Scenario: RunResult loads a scenario whose background step is undefined
    When I run BehaveXRunner with a feature whose background step is undefined
    Then the RunResult has "1" failed scenario
    And the RunResult first failed scenario has behave's error status and the error message "step undefined"

  @API_RUNNER_034
  Scenario: RunResult loads a scenario whose parallel worker crashed
    When I run BehaveXRunner with a crashing test using "2" parallel processes and "scenario" parallel scheme
    Then the RunResult has "1" failed scenario
    And the RunResult first failed scenario has status "failed" and the error message "Execution crashed or was interrupted when executing the scenario. No outputs could be generated."

  @API_RUNNER_035
  Scenario: an interrupt before the results are merged still returns a RunResult
    When I run BehaveXRunner with passing tests while merging the results raises KeyboardInterrupt
    Then the RunResult exit_code should be "1"

  @API_RUNNER_036
  Scenario: a queued future cancelled by stop() while the runner waits on it is not counted as a crash
    When the runner waits on a queued future that stop() cancels meanwhile
    Then no execution code was recorded for the cancelled future

  @API_RUNNER_037
  Scenario: repeated runs in one process each use their own config file
    When I run BehaveXRunner in one process with a config file setting output folder "a", then one setting "b"
    Then each in-process run reported and wrote its report to its own config's output folder

  @API_RUNNER_038
  Scenario: RunResult.output_folder is the resolved default output folder
    When I run BehaveXRunner with passing tests
    Then the RunResult output_folder is the absolute path of "output"

  @API_RUNNER_039
  Scenario: a run does not reuse the paths of a previous run in the same process
    When I run BehaveXRunner in one process on passing tests, then with include_paths on failing tests only
    Then the in-process run totals are "5, 1"

  @API_RUNNER_040
  Scenario: a parallel run after a rerun_failures run in the same process runs its own scenarios
    When I run BehaveXRunner in one process with rerun_failures on the failing test, then on passing tests with "2" parallel processes
    Then the in-process run totals are "1, 5"

  @API_RUNNER_041
  Scenario: on_progress reports the final status of a scenario whose after_scenario hook fails
    When I run BehaveXRunner on passing scenarios, one with a failing after_scenario hook, with an on_progress callback
    Then the on_progress callback was called once per scenario in the RunResult summary
    And each on_progress event status matches the scenario's final status in the RunResult
    And at least one on_progress event has behave's error status

  @API_RUNNER_042
  Scenario: a later in-process run does not call the previous run's worker hooks
    When I run BehaveXRunner in one process on worker hook tests, then on passing tests
    Then the second run did not call any worker hook

  @API_RUNNER_048
  Scenario: a dry run does not suppress the user hooks of a later run in the same process
    When I run BehaveXRunner in one process as a dry run, then as a real run, on passing scenarios, one with a failing after_scenario hook
    Then the RunResult has "1" failed scenario

  @API_RUNNER_049
  Scenario: stop() does not drop a scenario whose result callback finishes after the last future resolves
    When I run BehaveXRunner on "twelve_scenarios.feature" with "2" parallel processes, slow result callbacks, and call stop() on progress event "1"
    Then every scenario whose result was handled is in the RunResult and fired its event before run() returned

  @API_RUNNER_050
  Scenario Outline: an invalid <argument> raises ValueError instead of exiting
    When I run BehaveXRunner on passing tests with <argument> set to "<value>"
    Then run() raised a ValueError mentioning "invalid choice: '<value>'"
    Examples:
      | argument        | value   |
      | parallel_scheme | bogus   |
      | logging_level   | verbose |

  @API_RUNNER_051
  Scenario: a tag starting with "-" is passed to the run instead of being parsed as an option
    When I run BehaveXRunner with passing tests filtered by tag "-@PASSING_TAG_1"
    Then the RunResult stopped should be "False"

  @API_RUNNER_052
  Scenario: a path that does not exist raises ValueError instead of exiting
    When I run BehaveXRunner on a feature path that does not exist
    Then run() raised a ValueError mentioning "BehaveX stopped before running the tests"

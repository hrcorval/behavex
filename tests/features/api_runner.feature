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
    Given Python can cancel queued futures
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

  @API_RUNNER_055
  Scenario: on_progress skips an @AUTORETRY scenario that the tag filter excludes
    When I run BehaveXRunner with tags "@INCLUDED" on @AUTORETRY scenarios, one excluded by the tag filter, with an on_progress callback
    Then the RunResult summary total is "2"
    And the on_progress callback was called once per scenario in the RunResult summary
    And no on_progress event is for the scenario "Autoretry scenario excluded by the tag filter"

  @API_RUNNER_070
  Scenario: on_progress skips an @AUTORETRY Scenario Outline example that the name filter excludes
    When I run BehaveXRunner with name "row selected" on an @AUTORETRY Scenario Outline with an on_progress callback
    Then the RunResult summary total is "1"
    And the on_progress callback was called once per scenario in the RunResult summary

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

  @API_RUNNER_069
  Scenario: on_progress reports the final status of a scenario whose cleanup or after_tag hook fails
    When I run BehaveXRunner on passing scenarios, one with a failing cleanup and one with a failing after_tag hook, with an on_progress callback
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
    Given Python can cancel queued futures
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
  Scenario Outline: <input> raises ValueError instead of exiting or passing with no scenarios
    When I call run() with <input>
    Then run() raised a ValueError mentioning "BehaveX stopped before running the tests: Specified path was not found"
    Examples:
      | input                           |
      | a path that does not exist      |
      | no paths and no features folder |

  @API_RUNNER_053
  Scenario Outline: a relative <argument> entry starting with "-" runs its scenarios instead of being parsed as an option
    When I run BehaveXRunner on passing tests through a relative <argument> entry starting with "-" using "<processes>" parallel processes
    Then the RunResult exit_code should be "0"
    And the RunResult summary total is "5"
    Examples:
      | argument      | processes |
      | paths         | 1         |
      | paths         | 2         |
      | include_paths | 1         |
      | include_paths | 2         |

  @API_RUNNER_054
  Scenario Outline: on_progress fires for every scenario in the RunResult, including those stop_on_failure left unexecuted
    When I run BehaveXRunner with stop_on_failure on a failure followed by passing scenarios using "<processes>" parallel processes and an on_progress callback
    Then the RunResult summary untested is "<untested>"
    And the on_progress callback was called once per scenario in the RunResult summary
    And the completed_count in on_progress events is strictly increasing up to the summary total
    Examples:
      | processes | untested |
      | 1         | 2        |
      | 2         | 0        |

  @API_RUNNER_056
  Scenario: RunResult.model_dump() and its serialization schema include passed, summary and failed_scenarios
    When I run BehaveXRunner with failing tests and serialize the RunResult with model_dump
    Then the dumped RunResult holds passed False, a summary total of 1 and 1 failed scenario

  @API_RUNNER_057
  Scenario: a run started while another run is active raises RuntimeError
    When I run BehaveXRunner with passing tests and call run() from its on_progress callback
    Then the second run raised a RuntimeError mentioning "Another BehaveXRunner.run() or discover() is active"
    And the RunResult exit_code should be "0"
    And the RunResult summary total is "5"

  @API_RUNNER_058
  Scenario: a glob that matches no file raises a ValueError naming the pattern
    When I call run() with a glob that matches no file
    Then run() raised a ValueError mentioning "BehaveX stopped before running the tests: No files found matching pattern"

  @API_RUNNER_059
  Scenario Outline: the behavex CLI prints why <input> stops the run and exits with code 1
    When I run the behavex CLI with <input>
    Then the CLI printed "Specified path was not found", then "Exit code: 1", and exited with code 1
    Examples:
      | input                           |
      | a path that does not exist      |
      | no paths and no features folder |

  @API_RUNNER_060
  Scenario: a run returns its results when sys.stdout cannot be reconfigured
    When I run BehaveXRunner with passing tests while sys.stdout is an io.StringIO
    Then the RunResult exit_code should be "0"
    And the RunResult summary total is "5"

  @API_RUNNER_061
  Scenario: repeated runs in one process do not grow PATH
    When I run BehaveXRunner twice in one process on passing tests and record PATH
    Then PATH is the same after both runs

  @API_RUNNER_062
  Scenario: on_progress events of a parallel scenario run carry the number of scenarios as total
    When I run BehaveXRunner with passing tests using "2" parallel processes, "scenario" scheme, and an on_progress callback
    Then the on_progress callback was called once per scenario in the RunResult summary
    And each on_progress event has the summary total as its total

  @API_RUNNER_063
  Scenario Outline: discover() lists the scenarios a single-process run reports, filtered by <filter>
    When I call discover() and then run() single-process on the discovery features filtered by <filter>
    Then discover() listed the scenarios the run reported, with their features and tags
    Examples:
      | filter                      |
      | nothing                     |
      | an included tag             |
      | an excluded tag             |
      | name                        |
      | an include_paths file line  |
      | a Scenario Outline example  |
      | the config tags_to_skip     |
      | a rerun_failures file       |
      | exclude                     |
      | include                     |

  @API_RUNNER_064
  Scenario Outline: <call> writes nothing to stdout and leaves <folder> untouched
    When I call <call> on <features> with <folder> as the output folder
    Then discover() listed "<count>" scenarios and printed nothing to stdout
    And "<undefined>" of the listed scenarios have undefined steps
    And the output folder is as it was before discover()
    Examples:
      | call                       | features                     | folder                              | count | undefined |
      | discover()                 | the discovery features       | an existing folder holding a marker | 7     | 0         |
      | discover()                 | the discovery features       | a folder that does not exist        | 7     | 0         |
      | discover()                 | the undefined steps features | a folder that does not exist        | 5     | 0         |
      | discover(check_steps=True) | the undefined steps features | an existing folder holding a marker | 5     | 3         |

  @API_RUNNER_065
  Scenario Outline: discover() raises a ValueError naming why <input> stops it, and a later run still runs
    When I call discover() with <input>, then run() on passing tests in the same process
    Then discover() raised a ValueError mentioning "<reason>"
    And the RunResult exit_code should be "0"
    And the RunResult summary total is "5"
    Examples:
      | input                         | reason                                                                                    |
      | a path that does not exist    | BehaveX stopped before discovering the tests: Specified path was not found                |
      | a glob that matches no file   | BehaveX stopped before discovering the tests: No files found matching pattern             |
      | a missing rerun_failures file | BehaveX stopped before discovering the tests: the rerun_failures file is missing or empty |
      | no paths and no features folder | BehaveX stopped before discovering the tests: Specified path was not found: features    |

  @API_RUNNER_066
  Scenario: discover() during an active run raises RuntimeError
    When I run BehaveXRunner with passing tests and call discover() from its on_progress callback
    Then discover() raised a RuntimeError mentioning "Another BehaveXRunner.run() or discover() is active"

  @API_RUNNER_067
  Scenario: a run started while discover() is exploring the features raises RuntimeError
    When I call discover() on the discovery features and start a run while it explores them
    Then the run started during discover() raised a RuntimeError mentioning "Another BehaveXRunner.run() or discover() is active"

  @API_RUNNER_068
  Scenario: of two threads calling run() at once, exactly one raises RuntimeError
    When two threads call run() on passing tests at once, the second while the first validates its arguments
    Then exactly one of the two runs raised a RuntimeError mentioning "Another BehaveXRunner.run() or discover() is active"

  @API_RUNNER_071
  Scenario Outline: load_results() rebuilds the RunResult that run() returned <case>
    When I run BehaveXRunner <case> with a configured output folder, then call load_results() on that folder
    Then load_results() returned the same RunResult as run()
    And the loaded RunResult has exit_code "<exit_code>", stopped "<stopped>" and "<total>" scenarios
    Examples:
      | case                                                | exit_code | stopped | total |
      | on the secondary features in a single process       | 1         | False   | 54    |
      | on the secondary features in parallel by feature    | 1         | False   | 54    |
      | on the secondary features in parallel by scenario   | 1         | False   | 54    |
      | on the secondary features as a dry run              | 0         | False   | 54    |
      | on the secondary features with the Allure formatter | 1         | False   | 54    |
      | on tests whose before_all_workers hook fails        | 1         | False   | 0     |
      | stopped while before_all_workers runs               | 0         | True    | 0     |

  @API_RUNNER_072
  Scenario Outline: load_results() raises a ValueError naming why <folder> holds no results
    When I call load_results() on <folder>
    Then load_results() raised a ValueError mentioning "<reason>"
    Examples:
      | folder                                     | reason                                                   |
      | the output folder of a no_report run       | has no overall_status.json (a no_report run writes none) |
      | a folder that does not exist               | has no overall_status.json (a no_report run writes none) |
      | a folder written by BehaveX 4.6            | was written by a BehaveX older than 4.7.0                |
      | a passed run's folder without report.json  | has no report.json for a run that exited 0               |
      | a folder whose report.json has no features | has no features                                          |

  @API_RUNNER_073
  Scenario: load_results() reads a run started from the CLI
    When I run behavex from the CLI on the secondary features, then call load_results() on its output folder
    Then the loaded RunResult has the CLI's exit code, a run_id and "54" scenarios

  @API_RUNNER_074
  Scenario Outline: discover(check_steps=True) lists the steps a run <mode> finds undefined, on <features>
    When I call discover(check_steps=True), then run BehaveXRunner <mode>, on <features>
    Then discover() listed the undefined steps the run reported, "<count>" of them
    Examples:
      | mode                    | features                                              | count |
      | in a single process     | the undefined steps features                          | 3     |
      | as a dry run            | the undefined steps features                          | 3     |
      | in parallel by feature  | the undefined steps features                          | 3     |
      | in parallel by scenario | the undefined steps features                          | 3     |
      | in a single process     | a top feature and a feature with its own steps folder | 2     |
      | in parallel by feature  | a top feature and a feature with its own steps folder | 1     |

  @API_RUNNER_076
  Scenario: discover(check_steps=True) ignores the step definitions an earlier run in the same process loaded
    When I run BehaveXRunner on the undefined steps features, then call discover(check_steps=True) on the top feature, in the same process
    Then discover() listed "1" undefined steps for the scenario "Uses a step only the undefined steps features define"

  @API_RUNNER_075
  Scenario Outline: discover(check_steps=True) raises a ValueError when <problem>
    When I call discover(check_steps=True) on features whose <problem>
    Then discover() raised a ValueError mentioning "<reason>"
    Examples:
      | problem                     | reason                                                  |
      | step module fails to import | No module named 'a_module_that_does_not_exist'          |
      | folder has no steps folder  | Could not find the step definitions: No steps directory |

  @API_RUNNER_077
  Scenario Outline: a run <mode> does not see the step definitions of an earlier run in the same process
    When I run BehaveXRunner <mode> on the undefined steps features, then on the top feature, in the same process
    Then the scenario "Uses a step only the undefined steps features define" ended with behave's error status in the second run
    Examples:
      | mode                   |
      | in a single process    |
      | in parallel by feature |

  @API_RUNNER_078
  Scenario: a single-process run writes behave's output through the host's sys.stdout
    When I run BehaveXRunner in a single process on passing tests with sys.stdout redirected
    Then the redirected sys.stdout received behave's summary and the process stdout did not

  @API_RUNNER_079
  Scenario: a single-process run delivers each on_progress event as its scenario finishes
    When I run BehaveXRunner in a single process on passing tests, noting the output that had arrived at each on_progress event
    Then the first on_progress event arrived before behave printed its summary

  @API_RUNNER_080
  Scenario Outline: a parallel run <scheme> runs @SERIAL work without the step definitions of an earlier @SERIAL run in the same process
    When I run BehaveXRunner in parallel by <scheme> on the first @SERIAL suite, then on the second, in the same process
    Then the scenario "Uses a step only the first serial suite defines" ended with behave's error status in the second run
    Examples:
      | scheme   |
      | feature  |
      | scenario |

  @API_RUNNER_081
  Scenario Outline: stop() racing the @SERIAL work of a parallel run by <scheme> returns the results gathered so far, when <race>
    When I run BehaveXRunner in parallel by <scheme> on the second @SERIAL suite, and <race>
    Then the run raised no exception and the RunResult stopped is "True"
    Examples:
      | scheme   | race                                                    |
      | feature  | stop() comes right after the stop check                 |
      | feature  | the submitted @SERIAL work is cancelled before it starts |
      | scenario | stop() comes right after the stop check                 |
      | scenario | the submitted @SERIAL work is cancelled before it starts |

  @API_RUNNER_082
  Scenario: a single-process run lets a step write to sys.stdout's file descriptor
    When I run BehaveXRunner in a single process on a step that runs a subprocess writing to sys.stdout
    Then the RunResult exit_code should be "0"

  @API_RUNNER_083
  Scenario Outline: a Ctrl+C sent to <target> during a single-process run returns the scenarios that ran before it
    When I run BehaveXRunner in a single process on slow scenarios and send Ctrl+C once to <target> once the first one finishes
    Then the run raised no exception and the first scenario passed while the others did not run
    Examples:
      | target                                      |
      | the whole process group, as a terminal does |
      | the host process alone, as Jupyter does     |

  @API_RUNNER_084
  Scenario Outline: a worker that dies <mode> ends the run with exit_code 1 instead of raising
    When I run BehaveXRunner <mode> on a @SERIAL scenario that kills its worker
    Then the run raised no exception, the RunResult exit_code is "1" and it was not stopped
    Examples:
      | mode                    |
      | in a single process     |
      | in parallel by feature  |
      | in parallel by scenario |

  @API_RUNNER_085
  Scenario Outline: a Ctrl+C sent <presses> to the host process alone stops only the run's own processes
    When I run BehaveXRunner in a single process on slow scenarios and send Ctrl+C <presses> to the host process alone, as Jupyter does once the first one finishes
    Then the run raised no exception and a multiprocessing child the host started itself is still running
    Examples:
      | presses |
      | once    |
      | twice   |

  @API_RUNNER_086
  Scenario: a name filter starting with "-" is passed to behave instead of being parsed as an option
    When I run BehaveXRunner with passing tests filtered by name "-x|another"
    Then the RunResult exit_code should be "0"
    And the RunResult summary total is "1"

  @API_RUNNER_087
  Scenario: a Ctrl+C after stop() still terminates the workers of a parallel run
    When I run BehaveXRunner in parallel on slow scenarios, call stop() and send Ctrl+C to the host process once the first one finishes
    Then the run raised no exception and none of its processes is still running

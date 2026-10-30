Feature: BehaveXRunner Python API: on_progress events

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

  @API_RUNNER_062
  Scenario: on_progress events of a parallel scenario run carry the number of scenarios as total
    When I run BehaveXRunner with passing tests using "2" parallel processes, "scenario" scheme, and an on_progress callback
    Then the on_progress callback was called once per scenario in the RunResult summary
    And each on_progress event has the summary total as its total

  @API_RUNNER_079
  Scenario: a single-process run delivers each on_progress event as its scenario finishes
    When I run BehaveXRunner in a single process on passing tests, noting the output that had arrived at each on_progress event
    Then the first on_progress event arrived before behave printed its summary

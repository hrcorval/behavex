Feature: BehaveXRunner Python API: stop()
  Verify that BehaveXRunner.stop() ends a run early and returns the results gathered so far.

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

  @API_RUNNER_036
  Scenario: a queued future cancelled by stop() while the runner waits on it is not counted as a crash
    When the runner waits on a queued future that stop() cancels meanwhile
    Then no execution code was recorded for the cancelled future

  @API_RUNNER_049
  Scenario: stop() does not drop a scenario whose result callback finishes after the last future resolves
    Given Python can cancel queued futures
    When I run BehaveXRunner on "twelve_scenarios.feature" with "2" parallel processes, slow result callbacks, and call stop() on progress event "1"
    Then every scenario whose result was handled is in the RunResult and fired its event before run() returned

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

  @API_RUNNER_089
  Scenario: stop() on a BehaveXRunner that is not running leaves another instance's run going
    When I run BehaveXRunner on "twelve_scenarios.feature" with "2" parallel processes, "scenario" scheme, and call stop() on another, idle BehaveXRunner on progress event "1"
    Then the RunResult exit_code should be "0"
    And the RunResult stopped should be "False"
    And the RunResult summary total is "12"

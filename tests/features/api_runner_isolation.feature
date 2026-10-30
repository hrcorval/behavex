Feature: BehaveXRunner Python API: runs isolated from each other and from the host
  Verify that repeated BehaveXRunner runs in one process do not leak state into each other
  or into the host application.

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

  @API_RUNNER_037
  Scenario: repeated runs in one process each use their own config file
    When I run BehaveXRunner in one process with a config file setting output folder "a", then one setting "b"
    Then each in-process run reported and wrote its report to its own config's output folder

  @API_RUNNER_039
  Scenario: a run does not reuse the paths of a previous run in the same process
    When I run BehaveXRunner in one process on passing tests, then with include_paths on failing tests only
    Then the in-process run totals are "5, 1"

  @API_RUNNER_040
  Scenario: a parallel run after a rerun_failures run in the same process runs its own scenarios
    When I run BehaveXRunner in one process with rerun_failures on the failing test, then on passing tests with "2" parallel processes
    Then the in-process run totals are "1, 5"

  @API_RUNNER_042
  Scenario: a later in-process run does not call the previous run's worker hooks
    When I run BehaveXRunner in one process on worker hook tests, then on passing tests
    Then the second run did not call any worker hook

  @API_RUNNER_048
  Scenario: a dry run does not suppress the user hooks of a later run in the same process
    When I run BehaveXRunner in one process as a dry run, then as a real run, on passing scenarios, one with a failing after_scenario hook
    Then the RunResult has "1" failed scenario

  @API_RUNNER_060
  Scenario: a run returns its results when sys.stdout cannot be reconfigured
    When I run BehaveXRunner with passing tests while sys.stdout is an io.StringIO
    Then the RunResult exit_code should be "0"
    And the RunResult summary total is "5"

  @API_RUNNER_061
  Scenario: repeated runs in one process do not grow PATH
    When I run BehaveXRunner twice in one process on passing tests and record PATH
    Then PATH is the same after both runs

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

  @API_RUNNER_080
  Scenario Outline: a parallel run <scheme> runs @SERIAL work without the step definitions of an earlier @SERIAL run in the same process
    When I run BehaveXRunner in parallel by <scheme> on the first @SERIAL suite, then on the second, in the same process
    Then the scenario "Uses a step only the first serial suite defines" ended with behave's error status in the second run
    Examples:
      | scheme   |
      | feature  |
      | scenario |

  @API_RUNNER_082
  Scenario: a single-process run lets a step write to sys.stdout's file descriptor
    When I run BehaveXRunner in a single process on a step that runs a subprocess writing to sys.stdout
    Then the RunResult exit_code should be "0"

  @API_RUNNER_088
  Scenario Outline: a run <mode> leaves the host application's logging configuration as it was
    When I run BehaveXRunner <mode> after the host application configured its own logging
    Then the run raised no exception and the host application's logging still works as it configured it
    Examples:
      | mode                    |
      | in a single process     |
      | in parallel by scenario |

  @API_RUNNER_090 @POSIX_ONLY
  Scenario Outline: a run <mode> from a host that forks processes does not see the host's step definitions
    When I run BehaveXRunner <mode> on slow scenarios from a host that forks processes and registered the same step itself
    Then the run raised no exception and its RunResult exit_code is "0"
    Examples:
      | mode                    |
      | in a single process     |
      | in parallel by scenario |

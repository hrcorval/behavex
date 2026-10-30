Feature: BehaveXRunner Python API: argument validation and overlapping calls
  Verify that BehaveXRunner refuses invalid arguments with an exception instead of exiting,
  and refuses a call while another one is active.

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

  @API_RUNNER_068
  Scenario: of two threads calling run() at once, exactly one raises RuntimeError
    When two threads call run() on passing tests at once, the second while the first validates its arguments
    Then exactly one of the two runs raised a RuntimeError mentioning "Another BehaveXRunner.run() or discover() is active"

  @API_RUNNER_086
  Scenario: a name filter starting with "-" is passed to behave instead of being parsed as an option
    When I run BehaveXRunner with passing tests filtered by name "-x|another"
    Then the RunResult exit_code should be "0"
    And the RunResult summary total is "1"

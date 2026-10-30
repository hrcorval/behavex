Feature: BehaveXRunner Python API: Ctrl+C and dying workers
  Verify that a Ctrl+C or a dying worker during a BehaveXRunner run still returns a RunResult.

  @API_RUNNER_035
  Scenario: an interrupt before the results are merged still returns a RunResult
    When I run BehaveXRunner with passing tests while merging the results raises KeyboardInterrupt
    Then the RunResult exit_code should be "1"

  @API_RUNNER_083 @POSIX_ONLY
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

  @API_RUNNER_085 @POSIX_ONLY
  Scenario Outline: a Ctrl+C sent <presses> to the host process alone stops only the run's own processes
    When I run BehaveXRunner in a single process on slow scenarios and send Ctrl+C <presses> to the host process alone, as Jupyter does once the first one finishes
    Then the run raised no exception and a multiprocessing child the host started itself is still running
    Examples:
      | presses |
      | once    |
      | twice   |

  @API_RUNNER_087 @POSIX_ONLY
  Scenario: a Ctrl+C after stop() still terminates the workers of a parallel run
    When I run BehaveXRunner in parallel on slow scenarios, call stop() and send Ctrl+C to the host process once the first one finishes
    Then the run raised no exception and none of its processes is still running

  @API_RUNNER_091 @POSIX_ONLY
  Scenario: a Ctrl+C that reaches a worker while it sends output to the host stops behave once the send completes
    When a worker gets a Ctrl+C while it puts a message on the host queue
    Then the put completed before the KeyboardInterrupt was raised

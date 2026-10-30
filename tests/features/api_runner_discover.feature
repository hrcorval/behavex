Feature: BehaveXRunner Python API: discover() and load_results()
  Verify that BehaveXRunner.discover() lists the scenarios a run would execute, and that
  load_results() rebuilds a RunResult from an output folder.

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
      | the config exclude          |
      | the config include          |

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

Feature: before_all_workers and after_all_workers hooks

  @WORKER_HOOKS_VALIDATION
  Scenario Outline: Shared context values flow from before_all_workers into all workers
    Given I have installed behavex
    When I run the behavex command on the "worker_hooks_features" worker hooks fixture with arguments "-t @WORKER_HOOKS --parallel-processes <parallel_processes>"
    Then I should see the following behavex console outputs and exit code "0"
      | output_line                 |
      | passed, 0 failed, 0 skipped |
      | Exit code: 0                |
    And I should not see error messages in the output
    And I should see the worker hook "before_all_workers" was called "1" times
    And I should see the worker hook "after_all_workers" was called "1" times

    Examples:
      | parallel_processes |
      | 1                  |
      | 2                  |

  @WORKER_HOOKS_VALIDATION
  Scenario: Non-serializable values in before_all_workers raise a clear error before execution starts
    Given I have installed behavex
    When I run the behavex command targeting the invalid worker hooks feature
    Then I should see the following behavex console outputs and exit code "1"
      | output_line                                                         |
      | Cannot set 'bad_value' in before_all_workers / after_all_workers    |
      | is not JSON-serializable and cannot be shared with worker processes |
      | Supported types: str, int, float, bool, list, dict, None            |
      | Exit code: 1                                                        |

  @WORKER_HOOKS_VALIDATION
  Scenario Outline: Worker hooks run exactly once when targeting <target> <arguments>
    Given I have installed behavex
    When I run the behavex command on the "<target>" worker hooks fixture with arguments "<arguments>"
    Then I should see the following behavex console outputs and exit code "0"
      | output_line      |
      | passed, 0 failed |
    And I should see the worker hook "before_all_workers" was called "1" times
    And I should see the worker hook "after_all_workers" was called "1" times

    Examples:
      | target                                                     | arguments                                         |
      | worker_hooks_features                                      | --parallel-processes 1                            |
      | worker_hooks_features                                      | --parallel-processes 3 --parallel-scheme scenario |
      | worker_hooks_features                                      | --parallel-processes 3 --parallel-scheme feature  |
      | worker_hooks_features/nested/worker_hooks_nested.feature   | --parallel-processes 1                            |
      | worker_hooks_features/nested/worker_hooks_nested.feature   | --parallel-processes 3 --parallel-scheme scenario |
      | worker_hooks_features/nested/worker_hooks_nested.feature   | --parallel-processes 3 --parallel-scheme feature  |
      | worker_hooks_features/nested/worker_hooks_nested.feature:4 | --parallel-processes 1                            |
      | worker_hooks_features/nested/worker_hooks_nested.feature:4 | --parallel-processes 3 --parallel-scheme scenario |
      | worker_hooks_features/nested/worker_hooks_nested.feature   | -t @WORKER_HOOKS --parallel-processes 3           |
      | worker_hooks_features                                      | --name Nested --parallel-processes 1              |
      | worker_hooks_features                                      | --name Nested --parallel-processes 3              |
      | worker_hooks_features/nested/worker_hooks_nested.feature   | --name Nested --parallel-processes 3              |

  @WORKER_HOOKS_VALIDATION
  Scenario Outline: Worker hooks are not called on a dry run targeting <target> <arguments>
    Given I have installed behavex
    When I run the behavex command on the "<target>" worker hooks fixture with arguments "--dry-run <arguments>"
    Then I should see the following behavex console outputs and exit code "0"
      | output_line  |
      | Exit code: 0 |
    And I should see the worker hook "before_all_workers" was called "0" times
    And I should see the worker hook "after_all_workers" was called "0" times

    Examples:
      | target                                                   | arguments              |
      | worker_hooks_features                                    | --parallel-processes 1 |
      | worker_hooks_features                                    | --parallel-processes 3 |
      | worker_hooks_features/nested/worker_hooks_nested.feature | --parallel-processes 3 |

  @WORKER_HOOKS_VALIDATION
  Scenario Outline: A failing <hook_name> is reported as a hook error and fails the run with <parallel_processes> parallel processes
    Given I have installed behavex
    When I run the behavex command on the "worker_hooks_features" worker hooks fixture with "FAILING_WORKER_HOOK" set to "<hook_name>" and arguments "--parallel-processes <parallel_processes>"
    Then I should see the following behavex console outputs and exit code "1"
      | output_line                                                            |
      | HOOK-ERROR in <hook_name>: RuntimeError: <hook_name> failed on purpose |
      | Exit code: 1                                                           |
    And I should see the worker hook "before_all_workers" was called "1" times
    And I should see the worker hook "after_all_workers" was called "1" times
    And I should see the overall status report shows "failed"

    Examples:
      | hook_name          | parallel_processes |
      | before_all_workers | 1                  |
      | before_all_workers | 3                  |
      | after_all_workers  | 1                  |
      | after_all_workers  | 3                  |

  @WORKER_HOOKS_VALIDATION
  Scenario Outline: Worker hooks run from the staged environment with <parallel_processes> parallel processes
    Given I have installed behavex
    When I run the behavex command on the "worker_hooks_stage_features" worker hooks fixture with "BEHAVE_STAGE" set to "product" and arguments "--parallel-processes <parallel_processes>"
    Then I should see the following behavex console outputs and exit code "0"
      | output_line      |
      | passed, 0 failed |
    And I should see the worker hook "before_all_workers" was called "1" times
    And I should see the worker hook "after_all_workers" was called "1" times

    Examples:
      | parallel_processes |
      | 1                  |
      | 3                  |

  @WORKER_HOOKS_VALIDATION
  Scenario Outline: Worker hooks next to a package import from the base directory run once with <parallel_processes> parallel processes from another directory
    Given I have installed behavex
    When I run the behavex command on the "worker_hooks_base_dir_features/features/sub" worker hooks fixture with arguments "--parallel-processes <parallel_processes>"
    Then I should see the following behavex console outputs and exit code "0"
      | output_line                            |
      | 1 scenario passed, 0 failed, 0 skipped |
      | Exit code: 0                           |
    And I should not see error messages in the output
    And I should see the worker hook "before_all_workers" was called "1" times
    And I should see the worker hook "after_all_workers" was called "1" times

    Examples:
      | parallel_processes |
      | 1                  |
      | 3                  |

  @WORKER_HOOKS_VALIDATION
  Scenario: An environment.py without worker hooks that imports a package from its base directory runs from another directory
    Given I have installed behavex
    When I run the behavex command on the "no_worker_hooks_base_dir_features/features/sub" worker hooks fixture with arguments "--parallel-processes 1"
    Then I should see the following behavex console outputs and exit code "0"
      | output_line                            |
      | 1 scenario passed, 0 failed, 0 skipped |
      | Exit code: 0                           |
    And I should not see error messages in the output
    And environment.py was imported only once, by the BehaveX main process

  @WORKER_HOOKS_VALIDATION
  Scenario: An environment.py without worker hooks is imported only by the worker processes of a parallel run
    Given I have installed behavex
    When I run the behavex command on the "no_worker_hooks_base_dir_features/features/sub" worker hooks fixture with arguments "--parallel-processes 3"
    Then I should see the following behavex console outputs and exit code "0"
      | output_line                            |
      | 1 scenario passed, 0 failed, 0 skipped |
      | Exit code: 0                           |
    And environment.py was imported by worker processes but not by the BehaveX main process

  @WORKER_HOOKS_VALIDATION
  Scenario: An environment.py encoded in Latin-1 without worker hooks runs
    Given I have installed behavex
    When I run the behavex command on a copy of the "no_worker_hooks_base_dir_features" worker hooks fixture whose environment.py is encoded in Latin-1
    Then I should see the following behavex console outputs and exit code "0"
      | output_line                            |
      | 1 scenario passed, 0 failed, 0 skipped |
      | Exit code: 0                           |

  @WORKER_HOOKS_VALIDATION
  Scenario: An environment.py with worker hooks that fails to import is reported as a hook error
    Given I have installed behavex
    When I run the behavex command on the "worker_hooks_base_dir_features/features/sub" worker hooks fixture with "FAILING_ENVIRONMENT_IMPORT" set to "1" and arguments "--parallel-processes 3"
    Then I should see the following behavex console outputs and exit code "1"
      | output_line                                                                      |
      | HOOK-ERROR in before_all_workers: RuntimeError: environment.py failed on purpose |
      | Exit code: 1                                                                     |

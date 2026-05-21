Feature: before_all_workers and after_all_workers hooks

  @WORKER_HOOKS_VALIDATION
  Scenario Outline: Shared context values flow from before_all_workers into all workers
    Given I have installed behavex
    When I run the behavex command targeting the worker hooks feature with "<parallel_processes>" parallel processes
    Then I should see the following behavex console outputs and exit code "0"
      | output_line                        |
      | passed, 0 failed, 0 skipped        |
      | Exit code: 0                       |
    And I should not see error messages in the output

    Examples:
      | parallel_processes |
      | 1                  |
      | 2                  |

  @WORKER_HOOKS_VALIDATION
  Scenario: Non-serializable values in before_all_workers raise a clear error before execution starts
    Given I have installed behavex
    When I run the behavex command targeting the invalid worker hooks feature
    Then I should see the following behavex console outputs and exit code "1"
      | output_line                                                                 |
      | Cannot set 'bad_value' in before_all_workers / after_all_workers            |
      | is not JSON-serializable and cannot be shared with worker processes          |
      | Supported types: str, int, float, bool, list, dict, None                    |
      | Exit code: 1                                                                |

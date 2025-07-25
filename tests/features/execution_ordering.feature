Feature: Test Execution Ordering

  @ORDER_TESTS
  Scenario Outline: Validate execution ordering by <parallel_scheme> with <parallel_processes> parallel processes
    Given I have installed behavex
    When I run the behavex command with execution ordering enabled using "<parallel_processes>" parallel processes and parallel scheme set as "<parallel_scheme>"
    Then I should see the following behavex console outputs and exit code "0"
    | output_line                                 |
    | PARALLEL_PROCESSES  \| <parallel_processes> |
    | PARALLEL_SCHEME     \| <parallel_scheme>    |
    | Exit code: 0                                |
    And I should not see error messages in the output
    And I should see the scenarios executed in the correct order for "<parallel_scheme>" scheme
    Examples:
      | parallel_scheme | parallel_processes |
      | scenario        | 2                  |
      | feature         | 2                  |

  @ORDER_TESTS @CUSTOM_PREFIX
  Scenario Outline: Validate execution ordering with custom order tag prefix using <parallel_scheme> and <parallel_processes> parallel processes
    Given I have installed behavex
    When I run the behavex command with execution ordering enabled using custom prefix "PRIORITY" with "<parallel_processes>" parallel processes and parallel scheme set as "<parallel_scheme>"
    Then I should see the following behavex console outputs and exit code "0"
    | output_line                                 |
    | PARALLEL_PROCESSES  \| <parallel_processes> |
    | PARALLEL_SCHEME     \| <parallel_scheme>    |
    | Exit code: 0                                |
    And I should not see error messages in the output
    And I should see the scenarios executed in the correct order for "<parallel_scheme>" scheme with custom prefix
    Examples:
      | parallel_scheme | parallel_processes |
      | scenario        | 2                  |
      | feature         | 2                  |

  @ORDER_TESTS @MIXED_TAGS
  Scenario Outline: Validate execution ordering with mixed order and unordered scenarios using <parallel_scheme> and <parallel_processes> parallel processes
    Given I have installed behavex
    When I run the behavex command with execution ordering enabled for mixed scenarios using "<parallel_processes>" parallel processes and parallel scheme set as "<parallel_scheme>"
    Then I should see the following behavex console outputs and exit code "0"
    | output_line                                 |
    | PARALLEL_PROCESSES  \| <parallel_processes> |
    | PARALLEL_SCHEME     \| <parallel_scheme>    |
    | Exit code: 0                                |
    And I should not see error messages in the output
    And I should see that ordered scenarios execute before unordered scenarios for "<parallel_scheme>" scheme
    Examples:
      | parallel_scheme | parallel_processes |
      | scenario        | 3                  |
      | feature         | 2                  |

  @ORDER_TESTS @SINGLE_PROCESS
  Scenario: Validate that ordering is ignored with single process execution
    Given I have installed behavex
    When I run the behavex command with execution ordering enabled using "1" parallel processes and parallel scheme set as "scenario"
    Then I should see the following behavex console outputs and exit code "0"
    | output_line                                 |
    | PARALLEL_PROCESSES  \| 1                   |
    | PARALLEL_SCHEME     \| scenario            |
    | Exit code: 0                                |
    And I should not see error messages in the output
    And the execution order should not be enforced with single process execution

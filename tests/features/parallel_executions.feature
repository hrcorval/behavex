Feature: Parallel executions

  @PARALLEL
  Scenario Outline: Parallel executions by <parallel_schema> and <parallel_processes> parallel processes
    Given I have installed behavex
    When I run the behavex command with "<parallel_processes>" parallel processes and parallel scheme set as "<parallel_schema>"
    Then I should see the behavex output with "PARALLEL_PROCESSES  | <parallel_processes>"
    And I should see the behavex output with "PARALLEL_SCHEME     | <parallel_schema>"
    And I should see the behavex output with "Exit code: 1"
    And I should not see error messages in the output
    Examples:
      | parallel_schema | parallel_processes |
      | scenario        | 3                  |
      | feature         | 2                  |

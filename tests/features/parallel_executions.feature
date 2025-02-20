Feature: Parallel executions

  @PARALLEL
  Scenario Outline: Parallel executions by <parallel_scheme> and <parallel_processes> parallel processes
    Given I have installed behavex
    When I run the behavex command with "<parallel_processes>" parallel processes and parallel scheme set as "<parallel_scheme>"
    Then I should see the following behavex console outputs and exit code "1"
    | output_line                                 |
    | PARALLEL_PROCESSES  \| <parallel_processes> |
    | PARALLEL_SCHEME     \| <parallel_scheme>    |
    | Exit code: 1                                |
    And I should not see error messages in the output
    And I should see the same number of scenarios in the reports and the console output
    Examples:
      | parallel_scheme | parallel_processes |
      | scenario        | 3                  |
      | feature         | 2                  |


  @PARALLEL
  Scenario Outline: Parallel executions by <parallel_scheme> and <parallel_processes> parallel processes with tags <tags>
    Given I have installed behavex
    When I run the behavex command with the following scheme, processes and tags
    | parallel_scheme   | parallel_processes   | tags     |
    | <parallel_scheme> | <parallel_processes> | <tags>   |
    Then I should see the following behavex console outputs and exit code "0"
    | output_line                                 |
    | PARALLEL_PROCESSES  \| <parallel_processes> |
    | PARALLEL_SCHEME     \| <parallel_scheme>    |
    | Exit code: 0                                |
    | 1 scenario passed, 0 failed                 |
    And I should not see error messages in the output
    And I should see the same number of scenarios in the reports and the console output
    And I should see the generated HTML report does not contain internal BehaveX variables and tags
    Examples:
      | parallel_scheme | parallel_processes | tags                                   |
      | scenario        | 3                  | -t=@PASSING_TAG_3 -t=@PASSING_TAG_3_1  |
      | scenario        | 2                  | -t=@PASSING_TAG_3 -t=~@PASSING_TAG_3_1 |
      | feature         | 3                  | -t=@PASSING_TAG_3 -t=@PASSING_TAG_3_1  |
      | feature         | 2                  | -t=@PASSING_TAG_3 -t=~@PASSING_TAG_3_1 |

Feature: Renaming Scenarios

  @RENAME
  Scenario: Renaming scenarios and features
    Given I have installed behavex
    When I run the behavex command that renames scenarios and features
    Then I should see the following behavex console outputs and exit code "0"
    | output_line                              |
    | scenarios passed, 0 failed, 0 skipped    |
    | Exit code: 0                             |
    And I should not see error messages in the output
    And I should see the same number of scenarios in the reports and the console output

  @RENAME
  Scenario Outline: Renaming scenarios and features in parallel by <parallel_scheme> scheme
    Given I have installed behavex
    When I setup the behavex command with "<parallel_processes>" parallel processes and parallel scheme set as "<parallel_scheme>"
    And I run the behavex command that renames scenarios and features
    Then I should see the following behavex console outputs and exit code "0"
    | output_line                              |
    | scenarios passed, 0 failed, 0 skipped    |
    | Exit code: 0                             |
    And I should not see error messages in the output
    And I should see the same number of scenarios in the reports and the console output
    Examples:
      | parallel_scheme | parallel_processes |
      | scenario        | 3                  |
      | feature         | 2                  |

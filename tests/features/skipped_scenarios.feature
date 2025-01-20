Feature: Skipped Scenarios

  @SKIPPED
  Scenario: Skipped tests should be reported
    Given I have installed behavex
    When I run the behavex command with a skipped test
    Then I should see the following behavex console outputs and exit code "0"
    | output_line                              |
    | 0 scenarios passed, 0 failed, 1 skipped  |
    | Exit code: 0                             |
    And I should not see error messages in the output
    And I should see the same number of scenarios in the reports and the console output
    And I should see the generated HTML report does not contain internal BehaveX variables and tags

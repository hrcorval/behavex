Feature: Failing Scenarios

  @FAILING
  Scenario: Failing tests should be reported
    Given I have installed behavex
    When I run the behavex command with a failing test
    Then I should see the following behavex console outputs and exit code "1"
    | output_line                             |
    | 0 scenarios passed, 1 failed, 0 skipped |
    | Exit code: 1                            |
    And I should not see exception messages in the output
    And I should see the same number of scenarios in the reports and the console output
    And I should see the generated HTML report does not contain internal BehaveX variables and tags

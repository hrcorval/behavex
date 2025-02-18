Feature: No tests executed

  @NO_TESTS_RUN
  Scenario: Execution without test scenarios run should not trigger errors
    Given I have installed behavex
    When I run the behavex command with no tests
    Then I should see the following behavex console outputs and exit code "0"
    | output_line                              |
    | Exit code: 0                             |
    And I should not see error messages in the output
    And I should see the same number of scenarios in the reports and the console output
    And I should see the generated HTML report does not contain internal BehaveX variables and tags

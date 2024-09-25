Feature: Passing Scenarios

  @PASSING
  Scenario: Passing tests should be reported
    Given I have installed behavex
    When I run the behavex command with a passing test
    Then I should see the behavex output with "1 scenario passed, 0 failed, 0 skipped" and exit code "0"
    And I should not see error messages in the output

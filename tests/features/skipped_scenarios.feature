Feature: Skipped Scenarios

  @SKIPPED
  Scenario: Skipped tests should be reported
    Given I have installed behavex
    When I run the behavex command with a skipped test
    Then I should see the behavex output with "0 scenarios passed, 0 failed, 1 skipped" and exit code "0"
    And I should not see error messages in the output

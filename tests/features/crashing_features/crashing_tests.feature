Feature: Crashing Tests

  @CRASHING
  Scenario: Crashing tests should be reported
    Given a condition to exit the scenario
    Then I should see the behavex output with "0 scenarios passed, 1 failed, 0 skipped"

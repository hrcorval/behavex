Feature: Crashing Tests

  @CRASHING @SERIAL
  Scenario: Crashing tests should be reported
    Given a condition to exit the scenario
    Then I perform the condition

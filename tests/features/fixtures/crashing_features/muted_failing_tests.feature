Feature: Muted Failing Tests

  @CRASHING @SERIAL @MUTE
  Scenario: Muted failing scenario
    Given a failing condition
    Then I perform the condition

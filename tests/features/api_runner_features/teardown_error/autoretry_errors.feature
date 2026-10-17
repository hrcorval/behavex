Feature: Autoretry Errors

  @AUTORETRY
  Scenario: Scenario whose step raises an error on every attempt
    Given a step that raises a non-assertion exception

  @AUTORETRY @FAILING_TEARDOWN
  Scenario: Scenario whose teardown fails on every attempt
    Given a passing step

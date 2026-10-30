Feature: Teardown Error

  Scenario: Passing scenario with a clean teardown
    Given a passing step

  @FAILING_TEARDOWN
  Scenario: Passing scenario whose teardown fails
    Given a passing step

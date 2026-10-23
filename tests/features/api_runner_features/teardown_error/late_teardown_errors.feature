Feature: Late Teardown Errors

  Scenario: Passing scenario with a clean teardown
    Given a passing step

  @FAILING_CLEANUP
  Scenario: Passing scenario whose cleanup fails
    Given a passing step

  @FAILING_AFTER_TAG
  Scenario: Passing scenario whose after_tag hook fails
    Given a passing step

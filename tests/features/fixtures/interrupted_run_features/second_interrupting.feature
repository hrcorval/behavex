Feature: Second feature that interrupts the run

  @FAILING_HOOK
  Scenario: Second scenario whose before_scenario hook fails
    Given a passing step

  Scenario: Second scenario that interrupts the run
    Given a step that interrupts the run

Feature: First feature that interrupts the run

  @FAILING_HOOK
  Scenario: First scenario whose before_scenario hook fails
    Given a passing step

  Scenario: First scenario that interrupts the run
    Given a step that interrupts the run

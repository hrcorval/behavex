Feature: Autoretry Raising Scenarios

  @AUTORETRY
  Scenario: Scenario whose step raises on its first attempt
    Given a step that raises on its first attempt

  @AUTORETRY
  Scenario: Scenario with autoretry that passes on its first attempt
    Given a passing step

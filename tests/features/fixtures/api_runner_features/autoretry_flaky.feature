Feature: Autoretry Flaky

  @AUTORETRY
  Scenario: Scenario that passes on its second attempt
    Given a step that fails on its first attempt

  @AUTORETRY
  Scenario: Scenario that fails on every attempt
    Given a step that always fails

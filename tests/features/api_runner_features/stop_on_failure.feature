Feature: Stop On Failure

  Scenario: Failing scenario that stops the run
    Given a step that always fails

  Scenario: Passing scenario after the failure 01
    Given a passing step

  Scenario: Passing scenario after the failure 02
    Given a passing step

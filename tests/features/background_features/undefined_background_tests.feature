Feature: Undefined Background Step

  Background:
    Given a background step nobody defined

  Scenario: Scenario behind an undefined background step
    Then I perform the condition

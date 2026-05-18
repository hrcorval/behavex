Feature: XML Validation Tests

  Background: Common setup
    Given a passing condition

  Scenario: Passing scenario for XML validation
    Then I perform the condition

  Scenario: Failing scenario for XML validation
    Given a failing condition
    Then I perform the condition

  Scenario: Skipped scenario for XML validation
    Given a condition to skip the scenario
    Then I perform the condition

  Scenario Outline: Parameterized scenario for XML validation with <param>
    Then I perform the condition
  Examples: "param set"
    | param |
    | alpha |
    | beta  |

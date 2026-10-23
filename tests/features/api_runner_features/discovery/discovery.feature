Feature: Discovery

  Scenario: Plain scenario
    Given a passing step

  @SMOKE
  Scenario: Smoke scenario
    Given a passing step

  @SKIP
  Scenario: Scenario skipped by the config
    Given a passing step

  @MANUAL
  Scenario: Manual scenario
    Given a passing step

  Scenario Outline: Outline scenario <value>
    Given a passing step
    Examples:
      | value |
      | one   |
      | two   |

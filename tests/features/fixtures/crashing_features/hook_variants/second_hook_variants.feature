@CRASH_HOOK
Feature: Second Hook Variants

  Scenario: Passing scenario in a tagged feature
    Given a passing condition
    Then I perform the condition

  Scenario: Failing scenario in a tagged feature
    Given a failing condition
    Then I perform the condition

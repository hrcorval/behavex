Feature: First Hook Variants

  @CRASH_HOOK
  Scenario: Tagged scenario in an untagged feature
    Given a passing condition
    Then I perform the condition

  Scenario: Untagged passing scenario
    Given a passing condition
    Then I perform the condition

  Scenario Outline: Untagged outline row <row>
    Given a passing condition
    Then I perform the condition
    Examples:
      | row |
      | 1   |
      | 2   |

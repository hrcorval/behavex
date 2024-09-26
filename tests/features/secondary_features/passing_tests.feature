Feature: Passing Tests

  Scenario: This test should pass and does not contain a tag
    Given a passing condition
    Then I perform the condition

  @PASSING_TAG_1
  Scenario: This test should pass and contains a tag
    Given a passing condition
    Then I perform the condition

  @PASSING_TAG_2
  Scenario: This test should pass and contains another tag
    Given a passing condition
    Then I perform the condition

  @PASSING_TAG_3
  Scenario Outline: This test should pass and contains tag <tag> got from with examples
    Given a passing condition
    Then I perform the condition
  @PASSING_TAG_3_1
  Examples: "PASSING_TAG_3_1"
    | tag             |
    | PASSING_TAG_3_1 |

  @PASSING_TAG_3_2
  Examples: "PASSING_TAG_3_2"
    | tag             |
    | PASSING_TAG_3_2 |

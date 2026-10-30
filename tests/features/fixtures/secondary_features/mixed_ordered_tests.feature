Feature: Mixed Ordered and Unordered Test Scenarios

  @MIXED_TEST
  Scenario: Unordered test scenario that should run last
    Given a passing condition that records execution order "UNORDERED_1"
    Then I perform the condition

  @ORDER_002 @MIXED_TEST
  Scenario: Second ordered test scenario
    Given a passing condition that records execution order "ORDER_002"
    Then I perform the condition

  @MIXED_TEST
  Scenario: Another unordered test scenario that should run last
    Given a passing condition that records execution order "UNORDERED_2"
    Then I perform the condition

  @ORDER_001 @MIXED_TEST
  Scenario: First ordered test scenario
    Given a passing condition that records execution order "ORDER_001"
    Then I perform the condition

  @ORDER_003 @MIXED_TEST
  Scenario: Third ordered test scenario
    Given a passing condition that records execution order "ORDER_003"
    Then I perform the condition

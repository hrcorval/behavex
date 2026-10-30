Feature: Ordered Test Scenarios

  @ORDER_003 @ORDERED_TEST
  Scenario: Third ordered test scenario
    Given a passing condition that records execution order "ORDER_003"
    Then I perform the condition

  @ORDER_001 @ORDERED_TEST
  Scenario: First ordered test scenario
    Given a passing condition that records execution order "ORDER_001"
    Then I perform the condition

  @ORDER_002 @ORDERED_TEST
  Scenario: Second ordered test scenario
    Given a passing condition that records execution order "ORDER_002"
    Then I perform the condition

  @ORDER_010 @ORDERED_TEST
  Scenario: Fourth ordered test scenario
    Given a passing condition that records execution order "ORDER_010"
    Then I perform the condition

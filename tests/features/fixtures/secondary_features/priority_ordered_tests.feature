Feature: Priority Ordered Test Scenarios

  @PRIORITY_003 @PRIORITY_TEST
  Scenario: Third priority test scenario
    Given a passing condition that records execution order "PRIORITY_003"
    Then I perform the condition

  @PRIORITY_001 @PRIORITY_TEST
  Scenario: First priority test scenario
    Given a passing condition that records execution order "PRIORITY_001"
    Then I perform the condition

  @PRIORITY_002 @PRIORITY_TEST
  Scenario: Second priority test scenario
    Given a passing condition that records execution order "PRIORITY_002"
    Then I perform the condition

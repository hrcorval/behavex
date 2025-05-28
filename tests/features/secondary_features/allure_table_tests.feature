Feature: Allure Table Test Scenarios
  This feature contains scenarios with table data for testing table processing

  Scenario: Test scenario with table data
    Given a test condition with table data
    When I process the following table:
      | name  | age | city        |
      | Alice | 30  | New York    |
      | Bob   | 25  | Los Angeles |
    Then I should see the table processed correctly

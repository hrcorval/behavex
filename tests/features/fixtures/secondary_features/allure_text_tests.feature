Feature: Allure Text Test Scenarios
  This feature contains scenarios with multiline text for testing text processing

  Scenario: Test scenario with multiline text
    Given a test condition with multiline text
    When I process the following text:
      """
      This is a multiline text block
      that contains multiple lines
      for testing text attachment processing
      in the Allure formatter
      """
    Then I should see the text processed correctly

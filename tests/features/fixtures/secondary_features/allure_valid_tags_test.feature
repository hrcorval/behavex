@VALID_ALLURE_TAGS_SUBJECT
Feature: Test Feature with Valid Allure Tags
  This feature contains scenarios with valid allure tags to ensure
  our validation doesn't break normal tag processing

  @allure.label.severity:critical @allure.link.docs:https://docs.example.com @allure.issue:BUG-123 @epic=RC-555
  Scenario: Scenario with valid allure tags
    Given a simple test condition
    When I perform a simple action
    Then I should see a simple result

  @allure.tms:JIRA-456 @allure.testcase:TC-789 @allure.link.custom:https://custom.example.com @story=VPD-444
  Scenario: Scenario with more valid allure tags
    Given a simple test condition
    When I perform a simple action
    Then I should see a simple result

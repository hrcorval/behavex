@epic=RC-001 @story=VPD-123 @severity=critical @author:john.doe
Feature: Allure Tagged Test Scenarios
  This feature contains scenarios with various Allure-specific tags for testing tag processing

  @allure.tms:JIRA-456 @allure.issue:BUG-789 @allure.testcase:TC-123 @allure.link.custom:https://example.com/link @package=integration.auth
  Scenario: Test scenario with comprehensive Allure tags
    Given a test condition with allure tags
    When I execute an action with epic and story tags
    Then I should see the result processed correctly

  @epic=RC-002 @story=VPD-456 @severity=normal
  Scenario: Test scenario with different epic and story
    Given another test condition with different tags
    When I execute another action
    Then I should see different tag processing

  @severity=blocker @author:jane.smith @package=integration.api
  Scenario: Test scenario with blocker severity
    Given a critical test condition
    When I execute a critical action
    Then I should see critical processing

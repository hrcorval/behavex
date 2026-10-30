@MALFORMED_ALLURE_TAGS_SUBJECT
Feature: Test Feature with Malformed Allure Tags
  This feature contains scenarios with malformed allure tags to test that
  the Allure formatter handles them gracefully without crashing

  @allure.label.severity @allure.label.:critical @allure.label.author: @epic=RC-999
  Scenario: Scenario with malformed allure.label tags
    Given a simple test condition
    When I perform a simple action
    Then I should see a simple result

  @allure.link.custom @allure.link.:https://example.com @allure.link.docs: @story=VPD-888
  Scenario: Scenario with malformed allure.link tags
    Given a simple test condition
    When I perform a simple action
    Then I should see a simple result

  @allure.issue: @allure.tms: @allure.testcase: @severity=blocker
  Scenario: Scenario with malformed simple allure tags
    Given a simple test condition
    When I perform a simple action
    Then I should see a simple result

  @allure.label. @allure.link. @author:valid.user
  Scenario: Scenario with edge case malformed tags
    Given a simple test condition
    When I perform a simple action
    Then I should see a simple result

  @allure.label.severity:normal @allure.label.invalid @allure.link.repo:https://github.com/example @allure.link.broken: @story=VPD-777
  Scenario: Scenario with mixed valid and invalid tags
    Given a simple test condition
    When I perform a simple action
    Then I should see a simple result

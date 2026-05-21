Feature: Worker Hooks Shared Context Tests

  @WORKER_HOOKS
  Scenario: Shared context values are accessible in steps
    Given the shared context values are available
    Then the string value "shared_url" should equal "https://staging.behavex.io"
    And the integer value "shared_retries" should equal "3"
    And the boolean value "shared_enabled" should be true
    And the list value "shared_tags" should contain "smoke"

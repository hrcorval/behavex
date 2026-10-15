Feature: Worker Hooks Nested Feature Tests

  @WORKER_HOOKS
  Scenario: Nested feature receives the shared context values
    Given the shared context values are available
    Then the string value "shared_url" should equal "https://staging.behavex.io"

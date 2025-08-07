Feature: Autoretry Test Scenarios
  This feature contains test scenarios that use autoretry functionality
  for validation of the autoretry mechanism

  @AUTORETRY @AUTORETRY_RECOVERABLE
  Scenario: Scenario that fails first but passes on retry (default 2 attempts)
    Given a condition that fails on first attempt but recovers on retry
    When I execute an action that is flaky
    Then I should see the result processed correctly after retry

  @AUTORETRY_3 @AUTORETRY_RECOVERABLE
  Scenario: Scenario that fails twice but passes on third attempt (3 attempts)
    Given a condition that fails on first two attempts but recovers on third
    When I execute an action that is very flaky
    Then I should see the result processed correctly after multiple retries

  @AUTORETRY_5 @AUTORETRY_RECOVERABLE
  Scenario: Scenario that fails multiple times but eventually passes (5 attempts)
    Given a condition that fails on first four attempts but recovers on fifth
    When I execute an action that is extremely flaky
    Then I should see the result processed correctly after many retries

  @AUTORETRY @AUTORETRY_PERMANENT_FAILURE
  Scenario: Scenario that always fails even with retries (default 2 attempts)
    Given a condition that always fails
    When I execute an action that never succeeds
    Then I should see the action consistently fail

  @AUTORETRY_3 @AUTORETRY_PERMANENT_FAILURE
  Scenario: Scenario that permanently fails with 3 retry attempts
    Given a condition that always fails regardless of attempts
    When I execute an action that is permanently broken
    Then I should see the action fail after all retry attempts

  @AUTORETRY_RECOVERABLE
  Scenario: Regular scenario that fails first but passes on second run (no autoretry)
    Given a condition that fails on first attempt but recovers on second
    When I execute an action without autoretry
    Then I should see the action fail immediately without retry

  @AUTORETRY @AUTORETRY_IMMEDIATE_SUCCESS
  Scenario: Scenario with autoretry that passes immediately (no retry needed)
    Given a condition that always passes
    When I execute an action that succeeds immediately
    Then I should see the result processed correctly without retry

  @AUTORETRY_3 @AUTORETRY_IMMEDIATE_SUCCESS
  Scenario: Another scenario with autoretry that passes immediately (no retry needed)
    Given a condition that consistently passes
    When I execute an action that works on first try
    Then I should see the result processed correctly without any retries

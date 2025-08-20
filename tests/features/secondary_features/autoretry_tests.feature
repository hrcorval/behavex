Feature: Autoretry Test Scenarios
  This feature contains test scenarios that use autoretry functionality
  for validation of the autoretry mechanism

  @AUTORETRY @AUTORETRY_RECOVERABLE
  Scenario: Scenario that fails first but passes on retry (default 2 attempts)
    Given a condition that fails on first attempt but recovers on retry
    When I execute an action that fails initially
    Then I should see the result processed correctly after retry

  @AUTORETRY_3 @AUTORETRY_RECOVERABLE
  Scenario: Scenario that fails twice but passes on third attempt (3 attempts)
    Given a condition that fails on first two attempts but recovers on third
    When I execute an action that fails twice
    Then I should see the result processed correctly after retry

  @AUTORETRY_5 @AUTORETRY_RECOVERABLE
  Scenario: Scenario that fails multiple times but eventually passes (5 attempts)
    Given a condition that fails on first four attempts but recovers on fifth
    When I execute an action that fails multiple times
    Then I should see the result processed correctly after retry

  @AUTORETRY @AUTORETRY_PERMANENT_FAILURE
  Scenario: Scenario that always fails even with retries (default 2 attempts)
    Given a condition that always fails
    When I execute a permanently broken action
    Then I should see the result processed correctly after all retries

  @AUTORETRY_3 @AUTORETRY_PERMANENT_FAILURE
  Scenario: Scenario that permanently fails with 3 retry attempts
    Given a condition that always fails
    When I execute a permanently broken action with 3 attempts
    Then I should see the result processed correctly after all retries

  @AUTORETRY_5 @AUTORETRY_PERMANENT_FAILURE
  Scenario: Scenario that permanently fails with 5 retry attempts
    Given a condition that always fails
    When I execute a permanently broken action with 5 attempts
    Then I should see the result processed correctly after all retries

  @NO_AUTORETRY_FAILURE
  Scenario: Regular scenario that fails first but passes on second run (no autoretry)
    Given a condition that fails on first attempt but recovers on retry
    When I execute an action that fails without autoretry
    Then I should see the result processed correctly without retry

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

Feature: Autoretry Mechanism Validation

  @AUTORETRY_TESTS
  Scenario Outline: Validate autoretry mechanism with different retry counts and parallel execution
    Given I have installed behavex
    When I run the behavex command with autoretry tests using "<parallel_processes>" parallel processes and parallel scheme set as "<parallel_scheme>"
    Then I should see the following behavex console outputs and exit code "0"
    | output_line                                 |
    | PARALLEL_PROCESSES  \| <parallel_processes> |
    | PARALLEL_SCHEME     \| <parallel_scheme>    |
    | Exit code: 0                                |
    And I should not see error messages in the output
    And I should see autoretry messages for scenarios that recovered after retry
    And I should see the correct number of retry attempts for each autoretry scenario
    And I should see the HTML report contains retried scenarios information
    Examples:
      | parallel_scheme | parallel_processes |
      | scenario        | 1                  |
      | scenario        | 3                  |
      | feature         | 2                  |

  @AUTORETRY_TESTS @FAILING_SCENARIOS
  Scenario Outline: Validate autoretry mechanism with permanently failing scenarios
    Given I have installed behavex
    When I run the behavex command with permanently failing autoretry tests using "<parallel_processes>" parallel processes and parallel scheme set as "<parallel_scheme>"
    Then I should see the following behavex console outputs and exit code "1"
    | output_line                                 |
    | PARALLEL_PROCESSES  \| <parallel_processes> |
    | PARALLEL_SCHEME     \| <parallel_scheme>    |
    | Exit code: 1                                |
    And I should see autoretry failure messages for scenarios that never recover
    And I should see the correct number of retry attempts for each permanently failing scenario
    And I should see that permanently failing scenarios are marked as failed after all retry attempts
    Examples:
      | parallel_scheme | parallel_processes |
      | scenario        | 1                  |
      | scenario        | 2                  |

  @AUTORETRY_TESTS @DEFAULT_RETRY
  Scenario: Validate default autoretry behavior with @AUTORETRY tag (2 attempts)
    Given I have installed behavex
    When I run the behavex command with default autoretry test scenarios
    Then I should see the following behavex console outputs and exit code "0"
    | output_line   |
    | Exit code: 0  |
    And I should see that scenarios with @AUTORETRY tag are retried maximum 2 times
    And I should see autoretry messages in the console output
    And I should see the HTML report contains retried scenarios information

  @AUTORETRY_TESTS @CUSTOM_RETRY
  Scenario: Validate custom autoretry counts with @AUTORETRY_N tags
    Given I have installed behavex
    When I run the behavex command with custom autoretry count test scenarios
    Then I should see the following behavex console outputs and exit code "0"
    | output_line   |
    | Exit code: 0  |
    And I should see that scenarios with @AUTORETRY_3 tag are retried maximum 3 times
    And I should see that scenarios with @AUTORETRY_5 tag are retried maximum 5 times
    And I should see autoretry messages in the console output for each attempt
    And I should see the HTML report contains correct retry counts for each scenario

  @AUTORETRY_TESTS @MIXED_SCENARIOS
  Scenario: Validate mixed scenarios with and without autoretry
    Given I have installed behavex
    When I run the behavex command with mixed autoretry and regular test scenarios
    Then I should see the following behavex console outputs and exit code "1"
    | output_line   |
    | Exit code: 1  |
    And I should see that only scenarios with autoretry tags are retried
    And I should see that regular scenarios without autoretry tags fail immediately
    And I should see autoretry messages only for scenarios with autoretry tags
    And I should see the HTML report correctly distinguishes between retried and non-retried scenarios

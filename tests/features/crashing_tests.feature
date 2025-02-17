Feature: Crashing Tests

  @CRASHING
  Scenario: Crashing tests should be reported
    Given I have installed behavex
    When I run the behavex command with a crashing test
    Then I should see the following behavex console outputs and exit code "1"
    | output_line                              |
    | Exit code: 1                             |
    And I should not see exception messages in the output


  @CRASHING
  Scenario: Crashing tests with parallel processes and parallel scheme set as "scenario" should be reported
    Given I have installed behavex
    When I setup the behavex command with "2" parallel processes and parallel scheme set as "scenario"
    And I run the behavex command with a crashing test
    Then I should see the following behavex console outputs and exit code "1"
    | output_line                              |
    | Exit code: 1                             |
    And I should not see exception messages in the output


  @CRASHING
  Scenario: Crashing tests with parallel processes and parallel scheme set as "feature" should be reported
    Given I have installed behavex
    When I setup the behavex command with "2" parallel processes and parallel scheme set as "feature"
    And I run the behavex command with a crashing test
    Then I should see the following behavex console outputs and exit code "1"
    | output_line                              |
    | Exit code: 1                             |
    And I should not see exception messages in the output


  @CRASHING
  Scenario: Crashing tests should be reported
    Given I have installed behavex
    When I run the behavex command with a test that uses a crashing environment
    Then I should see the following behavex console outputs and exit code "1"
    | output_line                              |
    | Exit code: 1                             |
    And I should not see exception messages in the output

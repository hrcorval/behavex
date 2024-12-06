Feature: Passing Scenarios

  @PASSING
  Scenario: Passing tests should be reported
    Given I have installed behavex
    When I run the behavex command with a passing test
    Then I should see the following behavex console outputs and exit code "0"
    | output_line                              |
    | scenarios passed, 0 failed, 0 skipped    |
    | Exit code: 0                             |
    And I should not see error messages in the output
    And I should see the same number of scenarios in the reports and the console output
    And I should see the generated HTML report does not contain internal BehaveX variables and tags


  @PASSING
  Scenario: Passing tests with AND tags
    Given I have installed behavex
    When I run the behavex command with the following tags
    | tags                                  |
    | -t=@PASSING_TAG_3 -t=@PASSING_TAG_3_1 |
    Then I should see the following behavex console outputs and exit code "0"
    | output_line                       |
    | 1 scenario passed, 0 failed       |
    | Exit code: 0                      |
    And I should not see error messages in the output
    And I should see the same number of scenarios in the reports
    And I should see the generated HTML report does not contain internal BehaveX variables and tags

  @PASSING @WIP
  Scenario: Passing tests with NOT tags
    Given I have installed behavex
    When I run the behavex command with the following tags
    | tags                                   |
    | -t=@PASSING_TAG_3 -t=~@PASSING_TAG_3_1 |
    Then I should see the following behavex console outputs and exit code "0"
    | output_line                       |
    | 1 scenario passed, 0 failed       |
    | Exit code: 0                      |
    And I should not see error messages in the output
    And I should see the same number of scenarios in the reports and the console output
    And I should see the generated HTML report does not contain internal BehaveX variables and tags

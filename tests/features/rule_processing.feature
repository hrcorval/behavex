Feature: Rule Processing

  @RULE_PROCESSING
  Scenario: Scenarios under Rule sections should be executed by behavex
    Given I have installed behavex
    When I run the behavex command with a rule test
    Then I should see the following behavex console outputs and exit code "0"
      | output_line                          |
      | 3 scenarios passed, 0 failed         |
      | Exit code: 0                         |
    And I should not see error messages in the output

  @RULE_PROCESSING
  Scenario: Scenarios under Rule sections should appear in the HTML report
    Given I have installed behavex
    When I run the behavex command with a rule test
    Then I should see the HTML report was generated and contains "3" scenarios
    And I should see the same number of scenarios in the reports and the console output

  @RULE_PROCESSING
  Scenario: Scenario names under Rule sections should be visible in the HTML report
    Given I have installed behavex
    When I run the behavex command with a rule test
    Then I should see the generated HTML report contains the "Passing scenario in first rule" string
    And I should see the generated HTML report contains the "Passing scenario in second rule" string

  @RULE_PROCESSING
  Scenario: Scenarios under Rule sections should execute correctly in parallel
    Given I have installed behavex
    When I run the behavex command with a rule test using "2" parallel processes and "scenario" parallel scheme
    Then I should see the following behavex console outputs and exit code "0"
      | output_line                          |
      | 3 scenarios passed, 0 failed         |
      | Exit code: 0                         |
    And I should see the HTML report was generated and contains "3" scenarios

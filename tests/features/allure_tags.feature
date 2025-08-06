@ALLURE_TAGS
Feature: Allure Tag Validation End-to-End Tests
  These tests verify that the Allure formatter properly handles malformed tags
  by running complete BehavX executions and examining the generated Allure reports

  @ALLURE_FORMATTER
  Scenario: Validate Allure formatter gracefully handles malformed label tags
    Given I have installed behavex
    When I run the behavex command with allure formatter on malformed tags test file
    Then I should see the following behavex console outputs and exit code "0"
    | output_line   |
    | Exit code: 0  |
    And I should not see error messages in the output
    And I should see that allure-results directory was created
    And I should see that allure result files were generated despite malformed tags
    And I should see that malformed allure.label tags are not present in the generated reports
    And I should see that valid tags are still processed correctly in the reports

  @ALLURE_FORMATTER
  Scenario: Validate Allure formatter handles mixed valid and invalid tags
    Given I have installed behavex
    When I run the behavex command with allure formatter on mixed tags scenarios
    Then I should see the following behavex console outputs and exit code "0"
    | output_line   |
    | Exit code: 0  |
    And I should not see error messages in the output
    And I should see that allure-results directory was created
    And I should see that only valid tags appear in the generated allure reports
    And I should see that invalid tags are silently omitted from reports

  @ALLURE_FORMATTER
  Scenario: Validate Allure formatter processes valid tags correctly (baseline)
    Given I have installed behavex
    When I run the behavex command with allure formatter on valid tags test file
    Then I should see the following behavex console outputs and exit code "0"
    | output_line   |
    | Exit code: 0  |
    And I should not see error messages in the output
    And I should see that allure-results directory was created
    And I should see that all valid allure tags are present in the generated reports
    And I should see that no malformed tag warnings appear in valid tag scenarios

  @ALLURE_FORMATTER
  Scenario: Validate Allure formatter robustness with edge case tags
    Given I have installed behavex
    When I run the behavex command with allure formatter on edge case malformed tags
    Then I should see the following behavex console outputs and exit code "0"
    | output_line   |
    | Exit code: 0  |
    And I should not see error messages in the output
    And I should see that allure-results directory was created
    And I should see that edge case malformed tags do not crash the formatter
    And I should see that only well-formed tags appear in the final reports

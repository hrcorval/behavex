Feature: Image Attachment Testing

  @IMAGE_ATTACHMENT @HTML_REPORT
  Scenario: Validate image attachments appear in HTML report with gallery icon
    Given I have installed behavex
    And image attachment functionality is required
    When I run the behavex command with image attachments
    Then image attachment dependencies should be available
    And I should see the following behavex console outputs and exit code "0"
    | output_line   |
    | Exit code: 0  |
    And I should not see error messages in the output
    And I should see the HTML report was generated and contains scenarios
    And I should see the generated HTML report contains the "glyphicon-picture" string

  @IMAGE_ATTACHMENT @ALLURE_FORMATTER
  Scenario: Validate image attachments appear in Allure formatter output
    Given I have installed behavex
    And image attachment functionality is required
    When I run the behavex command with allure formatter and image attachments
    Then image attachment dependencies should be available
    And I should see the following behavex console outputs and exit code "0"
    | output_line   |
    | Exit code: 0  |
    And I should not see error messages in the output
    And I should see that allure-results directory was created
    And I should see that images are stored in the allure formatter output directory

  @IMAGE_ATTACHMENT @HTML_REPORT @FAILED_SCENARIO
  Scenario: Validate image attachments appear for failed scenarios with ONLY_ON_FAILURE condition
    Given I have installed behavex
    And image attachment functionality is required
    And image attachments are configured for ONLY_ON_FAILURE condition
    When I run the behavex command with failed scenario and image attachments
    Then image attachment dependencies should be available
    And I should see the HTML report was generated and contains scenarios
    And I should see the generated HTML report contains the "glyphicon-picture" string
    And I should see that images are attached for failed scenarios in the HTML report

  @IMAGE_ATTACHMENT @HTML_REPORT @ERROR_SCENARIO
  Scenario: Validate image attachments behavior for error scenarios with ONLY_ON_FAILURE condition
    Given I have installed behavex
    And image attachment functionality is required
    And image attachments are configured for ONLY_ON_FAILURE condition
    When I run the behavex command with error scenario and image attachments
    Then image attachment dependencies should be available
    And I should see the HTML report was generated and contains scenarios
    And I should verify current behavior for error scenarios with ONLY_ON_FAILURE condition

Feature: Image Attachment Testing

  @IMAGE_ATTACHMENT @HTML_REPORT @INTEGRATION
  Scenario: Validate image attachments appear in HTML report with gallery icon
    Given I have installed behavex
    When I run the behavex command with image attachments
    Then I should see the following behavex console outputs and exit code "0"
    | output_line   |
    | Exit code: 0  |
    And I should not see error messages in the output
    And I should see the HTML report was generated and contains scenarios
    And I should see the generated HTML report contains the "glyphicon-picture" string

  @IMAGE_ATTACHMENT @ALLURE_FORMATTER @INTEGRATION
  Scenario: Validate image attachments appear in Allure formatter output
    Given I have installed behavex
    When I run the behavex command with allure formatter and image attachments
    Then I should see the following behavex console outputs and exit code "0"
    | output_line   |
    | Exit code: 0  |
    And I should not see error messages in the output
    And I should see that allure-results directory was created
    And I should see that images are stored in the allure formatter output directory

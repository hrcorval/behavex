Feature: Simple Image Attachment Tests

  @IMAGE_ATTACHMENT @HTML_REPORT
  Scenario: Test HTML report with multiple image attachments
    Given I take a screenshot using test image 1
    And I take a screenshot using test image 2
    When I validate image attachments
    Then I should see attached images in the output

  @IMAGE_ATTACHMENT @ALLURE_FORMATTER
  Scenario: Test Allure formatter with multiple image attachments
    Given I take a screenshot using test image 1
    And I take a screenshot using test image 2
    When I validate image attachments
    Then I should see attached images in the output

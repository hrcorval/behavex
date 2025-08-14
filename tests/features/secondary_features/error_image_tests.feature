Feature: Error Scenario Image Attachment Tests

  @IMAGE_ATTACHMENT @ERROR_SCENARIO @NON_PRODUCTION
  Scenario: Test scenario that ends in error status with image attachment
    Given image attachments are set to ONLY_ON_FAILURE condition
    And I take a screenshot using test image 1
    And I take a screenshot using test image 2
    When I validate image attachments
    Then I call an undefined step that will cause error status

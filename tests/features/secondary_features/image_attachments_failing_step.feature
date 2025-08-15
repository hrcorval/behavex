Feature: Image Attachments Failing Step

  @IMAGE_ATTACHMENT @FAILED_SCENARIO @NON_PRODUCTION
  Scenario: Test scenario with failing step and image attachment
    Given image attachments are set to ONLY_ON_FAILURE condition
    And I take a screenshot using test image 1
    And I take a screenshot using test image 2
    When I validate image attachments
    Then a failing condition is performed

Feature: Evidence and Image Attachment Tests

  @EVIDENCE_ATTACHMENT
  Scenario: Test that attaches a file to evidence path
    Given I attach a file to the scenario evidence path
    Then the evidence file should exist in the evidence folder

  @IMAGE_EVIDENCE_ATTACHMENT
  Scenario: Test that attaches an image using behavex-images
    Given image attachments are set to ALWAYS condition
    And I take a screenshot using test image 1
    And I attach a file to the scenario evidence path
    Then the evidence file should exist in the evidence folder

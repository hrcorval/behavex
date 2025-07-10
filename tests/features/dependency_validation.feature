Feature: Dependency Validation

  @DEPENDENCY_VALIDATION @IMAGE_DEPS @CRITICAL
  Scenario: Validate image attachment dependencies when required
    Given I have installed behavex
    And image attachment functionality is required
    And I take a screenshot using test image 1
    Then image attachment dependencies should be available
    # This test will FAIL if behavex-images is not available when required

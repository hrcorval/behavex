Feature: Test behavex installation

  @INSTALL
  Scenario: Verify behavex is installed
    Given I have installed behavex
    When I run the behavex command
    Then I should see the behavex output

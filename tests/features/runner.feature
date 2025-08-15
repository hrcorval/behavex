Feature: Test Behavex Installation

  @INSTALL
  Scenario: Verify behavex is installed
    Given I have installed behavex
    When I run the behavex command
    Then I should see the behavex output
    And I should not see exception messages in the output

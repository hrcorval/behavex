Feature: Dry run

  @DRY_RUN
  Scenario: Passing tests should be reported
    Given I have installed behavex
    When I run the behavex command by performing a dry run
    Then I should see the following behavex console outputs and exit code "0"
    | output_line         |
    | Dry run completed   |
    | Exit code: 0        |
    And I should not see error messages in the output

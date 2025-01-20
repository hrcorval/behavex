Feature: Rerun Scenarios

  @RERUN_SCENARIOS
  Scenario Outline: Performing rerun of failing scenarios using the -rf option
    Given I have installed behavex
    When I setup the behavex command with "<parallel_processes>" parallel processes and parallel scheme set as "<parallel_scheme>"
    When I run the behavex command with a file of failing tests
    Then I should see the following behavex console outputs and exit code "1"
    | output_line                    |
    | 2 scenarios passed, 1 failed   |
    | Exit code: 1                   |
    And I should not see exception messages in the output
    And I should see the same number of scenarios in the reports not considering the skipped scenarios
    And I should see the generated HTML report does not contain internal BehaveX variables and tags
    Examples:
      | parallel_scheme | parallel_processes |
      | scenario        | 1                  |
      | scenario        | 3                  |
      | feature         | 2                  |

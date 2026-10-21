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

      # TODO: Uncomment this when enable performing rerun of failing scenarios using parallel scheme set as feature
      # | feature         | 2                  |

  @RERUN_SCENARIOS
  Scenario Outline: A rerun with a <failures_file_state> failures file stops without running any test
    Given I have installed behavex
    When I run the behavex command on passing tests rerunning the failures of a "<failures_file_state>" file
    Then I should see the following behavex console outputs and exit code "1"
      | output_line   |
      | <output_line> |
    And I should not see "scenarios passed" in the console output
    Examples:
      | failures_file_state | output_line                                            |
      | missing             | The specified failing scenarios filename was not found |
      | empty               | There are no failing test scenarios to run             |
      | blank               | There are no failing test scenarios to run             |

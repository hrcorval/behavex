Feature: Progress Bar

Background:
  Given I have installed behavex
  And The progress bar is enabled

  @PROGRESS_BAR @PARALLEL
  Scenario Outline: Progress bar should be shown when running tests in parallel
    When I run the behavex command with "<parallel_processes>" parallel processes and parallel scheme set as "<parallel_scheme>"
    Then I should see the following behavex console outputs and exit code "1"
    | output_line                                   |
    | PARALLEL_PROCESSES  \| <parallel_processes>   |
    | PARALLEL_SCHEME     \| <parallel_scheme>      |
    | Exit code: 1                                  |
    | Executed <parallel_scheme>s: 100%\|           |
    And I should not see error messages in the output
    Examples:
      | parallel_scheme | parallel_processes |
      | scenario        | 3                  |
      | feature         | 2                  |

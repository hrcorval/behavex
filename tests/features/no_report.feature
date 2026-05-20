Feature: No Report argument

  @NO_REPORT
  Scenario Outline: Running with --no-report should not create any output files
    Given I have installed behavex
    When I run the behavex command with --no-report flag using "<parallel_processes>" parallel processes
    Then I should see the following behavex console outputs and exit code "0"
      | output_line                           |
      | scenarios passed, 0 failed, 0 skipped |
      | Exit code: 0                          |
    And the output folder should not exist
    And I should not see error messages in the output

    Examples:
      | parallel_processes |
      | 1                  |
      | 2                  |

  @NO_REPORT
  Scenario Outline: Running with --no-report should not fail when tests write evidence
    Given I have installed behavex
    When I run the behavex command with --no-report flag and evidence attachments using "<parallel_processes>" parallel processes
    Then I should see the following behavex console outputs and exit code "0"
      | output_line                     |
      | 1 scenario passed, 0 failed     |
      | Exit code: 0                    |
    And the output folder should not exist
    And I should not see error messages in the output

    Examples:
      | parallel_processes |
      | 1                  |
      | 2                  |

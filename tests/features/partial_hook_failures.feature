Feature: Partial hook failures under parallel-scheme feature

  @PARALLEL
  Scenario: A scenario's hook failure must not fail its siblings in the same feature
    Given I have installed behavex
    When I run the behavex command on "tests/features/partial_hook_failures/partial_hook_failure.feature" with "2" parallel processes and parallel scheme set as "feature"
    Then I should see the following behavex console outputs and exit code "1"
      | output_line                                     |
      | Second scenario fails its before_scenario hook  |
      | 2 scenarios passed, 1 failed, 0 skipped          |
      | Exit code: 1                                     |
    And I should see all scenario statuses in the JSON report are valid strings
    And I should see "1" failing scenarios in the JUnit XML report
    And I should see the JUnit XML failure message contains "HOOK-ERROR in before_scenario"
    And I should see the overall status report shows "failed"
    And I should see the error message of every failed scenario in the JSON report contains "HOOK-ERROR in before_scenario"

  Scenario: A scenario's hook failure must be reported with a valid allure status
    Given I have installed behavex
    When I run the behavex command with allure formatter on "partial_hook_failures/partial_hook_failure.feature"
    Then I should see that allure result files only contain valid allure statuses

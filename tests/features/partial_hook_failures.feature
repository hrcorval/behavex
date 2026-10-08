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

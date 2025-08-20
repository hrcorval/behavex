@TEST_EXECUTION_SUMMARY_VALIDATION
Feature: Execution Summary Validation
    As a BehaveX user
    I want execution summaries to be consistent between single and parallel execution
    So that I can rely on accurate test reporting regardless of execution mode

    Scenario: Validate passing tests summary format
        When I run the behavex command with "1" parallel processes and parallel scheme set as "scenario"
        Then I should see the following behavex console outputs
            | output_line                          |
            | features passed                      |
            | scenarios passed                     |
            | steps passed                         |
        When I run the behavex command with "2" parallel processes and parallel scheme set as "scenario"
        Then I should see the following behavex console outputs
            | output_line                          |
            | features passed                      |
            | scenarios passed                     |
            | steps passed                         |

    Scenario: Validate failed tests summary format
        When I run the behavex command on "tests/features/secondary_features/failing_tests.feature" with "1" parallel processes and parallel scheme set as "scenario"
        Then I should see the following behavex console outputs
            | output_line                          |
            | 0 features passed, 1 failed         |
            | 0 scenarios passed, 1 failed        |
            | 1 step passed, 1 failed             |
        When I run the behavex command on "tests/features/secondary_features/failing_tests.feature" with "2" parallel processes and parallel scheme set as "scenario"
        Then I should see the following behavex console outputs
            | output_line                          |
            | 0 features passed, 1 failed         |
            | 0 scenarios passed, 1 failed        |
            | 1 steps passed, 1 failed            |

    Scenario: Validate skipped tests summary format
        When I run the behavex command on "tests/features/secondary_features/skipped_tests.feature" with "1" parallel processes and parallel scheme set as "scenario"
        Then I should see the following behavex console outputs
            | output_line                          |
            | 0 features passed, 0 failed, 1 skipped |
            | 0 scenarios passed, 0 failed, 1 skipped |
            | 1 step passed, 0 failed, 1 skipped   |
        When I run the behavex command on "tests/features/secondary_features/skipped_tests.feature" with "2" parallel processes and parallel scheme set as "scenario"
        Then I should see the following behavex console outputs
            | output_line                          |
            | 0 features passed, 0 failed, 1 skipped |
            | 0 scenarios passed, 0 failed, 1 skipped |
            | 1 steps passed, 0 failed, 1 skipped  |

    Scenario: Validate mixed status tests summary format
        When I run the behavex command on "tests/features/secondary_features/passing_tests.feature tests/features/secondary_features/failing_tests.feature tests/features/secondary_features/skipped_tests.feature" with "1" parallel processes and parallel scheme set as "scenario"
        Then I should see the following behavex console outputs
            | output_line                          |
            | 1 feature passed, 1 failed, 1 skipped |
            | 5 scenarios passed, 1 failed, 1 skipped |
            | 12 steps passed, 1 failed, 1 skipped |
        When I run the behavex command on "tests/features/secondary_features/passing_tests.feature tests/features/secondary_features/failing_tests.feature tests/features/secondary_features/skipped_tests.feature" with "2" parallel processes and parallel scheme set as "scenario"
        Then I should see the following behavex console outputs
            | output_line                          |
            | 1 feature passed, 1 failed, 1 skipped |
            | 5 scenarios passed, 1 failed, 1 skipped |
            | 12 steps passed, 1 failed, 1 skipped |

    Scenario: Validate execution summary consistency between single and parallel execution
        When I run the behavex command on "tests/features/secondary_features/passing_tests.feature tests/features/secondary_features/failing_tests.feature" with "1" parallel processes and parallel scheme set as "scenario"
        Then the execution summaries should be identical between single and parallel execution
        When I run the behavex command on "tests/features/secondary_features/passing_tests.feature tests/features/secondary_features/failing_tests.feature" with "2" parallel processes and parallel scheme set as "scenario"
        Then the execution summaries should be identical between single and parallel execution

    Scenario: Validate report consistency with console output
        When I run the behavex command on "tests/features/secondary_features/passing_tests.feature tests/features/secondary_features/failing_tests.feature" with "1" parallel processes and parallel scheme set as "scenario"
        Then I should see the same number of scenarios in the reports and the console output
        When I run the behavex command on "tests/features/secondary_features/passing_tests.feature tests/features/secondary_features/failing_tests.feature" with "2" parallel processes and parallel scheme set as "scenario"
        Then I should see the same number of scenarios in the reports and the console output

    Scenario: Validate error categories are hidden when counts are zero
        When I run the behavex command on "tests/features/secondary_features/passing_tests.feature" with "1" parallel processes and parallel scheme set as "scenario"
        Then the summary should not show error categories when there are no errors

    Scenario: Validate comprehensive mixed status summary including multiple statuses
        When I run the behavex command on "tests/features/secondary_features/passing_tests.feature tests/features/secondary_features/failing_tests.feature tests/features/secondary_features/skipped_tests.feature" with "1" parallel processes and parallel scheme set as "scenario"
        Then I should see the following behavex console outputs
            | output_line                          |
            | 1 feature passed, 1 failed, 1 skipped |
            | 5 scenarios passed, 1 failed, 1 skipped |
            | 12 steps passed, 1 failed, 1 skipped |
        When I run the behavex command on "tests/features/secondary_features/passing_tests.feature tests/features/secondary_features/failing_tests.feature tests/features/secondary_features/skipped_tests.feature" with "2" parallel processes and parallel scheme set as "scenario"
        Then I should see the following behavex console outputs
            | output_line                          |
            | 1 feature passed, 1 failed, 1 skipped |
            | 5 scenarios passed, 1 failed, 1 skipped |
            | 12 steps passed, 1 failed, 1 skipped |

Feature: Crashing Tests

  @CRASHING
  Scenario: Crashing tests should be reported
    Given I have installed behavex
    When I run the behavex command with a crashing test
    Then I should see the following behavex console outputs and exit code "1"
    | output_line                              |
    | Exit code: 1                             |
    And I should not see exception messages in the output


  @CRASHING
  Scenario: Crashing tests with parallel processes and parallel scheme set as "scenario" should be reported
    Given I have installed behavex
    When I setup the behavex command with "2" parallel processes and parallel scheme set as "scenario"
    And I run the behavex command with a crashing test
    Then I should see the following behavex console outputs and exit code "1"
    | output_line                              |
    | Exit code: 1                             |
    And I should not see exception messages in the output


  @CRASHING
  Scenario: Crashing tests with parallel processes and parallel scheme set as "feature" should be reported
    Given I have installed behavex
    When I setup the behavex command with "2" parallel processes and parallel scheme set as "feature"
    And I run the behavex command with a crashing test
    Then I should see the following behavex console outputs and exit code "1"
    | output_line                              |
    | Exit code: 1                             |
    And I should not see exception messages in the output


  @CRASHING
  Scenario: Exit code should be 1 when step loading fails due to an ImportError
    Given I have installed behavex
    When I run the behavex command targeting the "import_error_features/import_error_tests.feature" feature
    Then I should see the following behavex console outputs and exit code "1"
      | output_line  |
      | Exit code: 1 |


  @CRASHING
  Scenario: XML report should be generated successfully when a step has no matching definition
    Given I have installed behavex
    When I run the behavex command targeting the "xml_report_features/undefined_step_tests.feature" feature
    Then I should not see exception messages in the output
    And I should see the JUnit XML report was generated


  @CRASHING @CRASHING_BEHAVE_HOOK
  Scenario Outline: Crashing tests in "<behave_hook>" hook should be reported
    Given I have installed behavex
    When I run the behavex command with a test that crashes in "<behave_hook>" hook with "<parallel_processes>" parallel processes and "<parallel_scheme>" parallel scheme
    Then I should see the following behavex console outputs and exit code "1"
    | output_line                              |
    | Exit code: 1                             |
    And I should not see exception messages in the output
    Examples:
      | behave_hook     | parallel_processes | parallel_scheme |
      | before_all      | 1                  | scenario        |
      | before_feature  | 1                  | scenario        |
      | before_scenario | 1                  | scenario        |
      | before_step     | 1                  | scenario        |
      | before_tag      | 1                  | scenario        |
      | after_all       | 1                  | scenario        |
      | after_feature   | 1                  | scenario        |
      | after_scenario  | 1                  | scenario        |
      | after_step      | 1                  | scenario        |
      | after_tag       | 1                  | scenario        |
      | before_all      | 2                  | scenario        |
      | before_feature  | 2                  | scenario        |
      | before_scenario | 2                  | scenario        |
      | before_step     | 2                  | scenario        |
      | before_tag      | 2                  | scenario        |
      | after_all       | 2                  | scenario        |
      | after_feature   | 2                  | scenario        |
      | after_scenario  | 2                  | scenario        |
      | after_step      | 2                  | scenario        |
      | after_tag       | 2                  | scenario        |


  @CRASHING @CRASHING_BEHAVE_HOOK
  Scenario Outline: A crash in "<behave_hook>" hook on "<target>" reports the same statuses in parallel as with a single process
    Given I have installed behavex
    When I run the behavex command on "<target>" with arguments "--parallel-processes 1 --parallel-scheme scenario -D crashing_behave_hook=<behave_hook> -D crashing_tag=<crashing_tag>"
    Then I should see the following behavex console outputs and exit code "1"
    | output_line  |
    | Exit code: 1 |
    And I should see the overall status report shows "failed"
    And I keep the feature and scenario statuses from the JSON report
    When I run the behavex command on "<target>" with arguments "--parallel-processes 2 --parallel-scheme scenario -D crashing_behave_hook=<behave_hook> -D crashing_tag=<crashing_tag>"
    Then I should see the following behavex console outputs and exit code "1"
    | output_line  |
    | Exit code: 1 |
    And I should see the overall status report shows "failed"
    And I should see the same feature and scenario statuses in the JSON report as the kept ones
    When I run the behavex command on "<target>" with arguments "--parallel-processes 2 --parallel-scheme feature -D crashing_behave_hook=<behave_hook> -D crashing_tag=<crashing_tag>"
    Then I should see the following behavex console outputs and exit code "1"
    | output_line  |
    | Exit code: 1 |
    And I should see the overall status report shows "failed"
    And I should see the same feature and scenario statuses in the JSON report as the kept ones
    Examples:
      | target                                               | behave_hook     | crashing_tag |
      | crashing_features/crashing_environment_tests.feature | before_all      |              |
      | crashing_features/crashing_environment_tests.feature | before_feature  |              |
      | crashing_features/crashing_environment_tests.feature | after_feature   |              |
      | crashing_features/crashing_environment_tests.feature | after_all       |              |
      | crashing_features/hook_variants                      | before_all      | CRASH_HOOK   |
      | crashing_features/hook_variants                      | before_feature  | CRASH_HOOK   |
      | crashing_features/hook_variants                      | before_scenario | CRASH_HOOK   |
      | crashing_features/hook_variants                      | before_step     | CRASH_HOOK   |
      | crashing_features/hook_variants                      | before_tag      | CRASH_HOOK   |
      | crashing_features/hook_variants                      | after_all       | CRASH_HOOK   |
      | crashing_features/hook_variants                      | after_feature   | CRASH_HOOK   |
      | crashing_features/hook_variants                      | after_scenario  | CRASH_HOOK   |
      | crashing_features/hook_variants                      | after_step      | CRASH_HOOK   |
      | crashing_features/hook_variants                      | after_tag       | CRASH_HOOK   |


  @CRASHING @CRASHING_BEHAVE_HOOK
  Scenario: An interrupted run after a hook failure must leave the feature it never reached untested
    Given I have installed behavex
    When I run the behavex command on "interrupted_run_features" with arguments "--parallel-processes 1"
    Then I should see the following behavex console outputs and exit code "1"
    | output_line  |
    | Exit code: 1 |
    And I should see "1" features with status "untested" in the JSON report


  @CRASHING @CRASHING_BEHAVE_HOOK
  Scenario Outline: A crash in "<behave_hook>" hook should only report valid statuses
    Given I have installed behavex
    When I run the behavex command with a test that crashes in "<behave_hook>" hook
    Then I should see the following behavex console outputs and exit code "1"
    | output_line  |
    | Exit code: 1 |
    And I should see all scenario statuses in the JSON report are valid strings
    And I should see all step statuses in the JSON report are valid strings
    Examples:
      | behave_hook     |
      | before_scenario |
      | before_step     |
      | after_step      |
      | after_scenario  |

  @CRASHING @CRASHING_BEHAVE_HOOK
  Scenario Outline: A crash in "<behave_hook>" hook must not be reported as passed or skipped
    Given I have installed behavex
    When I run the behavex command with a test that crashes in "<behave_hook>" hook with "<parallel_processes>" parallel processes and "<parallel_scheme>" parallel scheme
    Then I should see the following behavex console outputs and exit code "1"
    | output_line                              |
    | Exit code: 1                             |
    And I should see the overall status report shows "failed"
    And I should see the feature status in the JSON report is one of "failed, error"
    Examples:
      | behave_hook     | parallel_processes | parallel_scheme |
      | before_all      | 1                  | scenario        |
      | before_feature  | 1                  | scenario        |
      | before_all      | 2                  | scenario        |
      | before_feature  | 2                  | scenario        |
      | before_all      | 2                  | feature         |
      | before_feature  | 2                  | feature         |


  @CRASHING @CRASHING_BEHAVE_HOOK
  Scenario Outline: A crash in "after_all" hook must not leave the overall status passed with "<parallel_processes>" parallel processes and "<parallel_scheme>" parallel scheme
    Given I have installed behavex
    When I run the behavex command with a test that crashes in "after_all" hook with "<parallel_processes>" parallel processes and "<parallel_scheme>" parallel scheme
    Then I should see the following behavex console outputs and exit code "1"
    | output_line  |
    | Exit code: 1 |
    And I should see the overall status report shows "failed"
    Examples:
      | parallel_processes | parallel_scheme |
      | 1                  | scenario        |
      | 2                  | scenario        |
      | 2                  | feature         |

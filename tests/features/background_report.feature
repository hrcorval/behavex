@BACKGROUND_REPORT
Feature: Background Step Report Validation
  Validate that BehaveX correctly includes Background steps in its reports,
  ensuring background steps are visible in the HTML report and fully
  preserved in the JSON report structure for each scenario.

  Scenario: HTML report includes content from background steps
    When I run the behavex command targeting the "background_features/background_tests.feature" feature
    Then I should see the generated HTML report contains the "a passing condition" string

  Scenario: JSON report includes background steps structure for each scenario
    When I run the behavex command targeting the "background_features/background_tests.feature" feature
    Then I should see background steps in the JSON report for each scenario

  Scenario: Console step count includes background steps executed for each scenario
    When I run the behavex command targeting the "background_features/background_tests.feature" feature
    Then I should see the following behavex console outputs
      | output_line    |
      | 6 steps passed |

  Scenario: HTML and JUnit XML reports agree on the total scenario count
    When I run the behavex command targeting the "background_features/background_tests.feature" feature
    Then I should see the same number of scenarios in the reports

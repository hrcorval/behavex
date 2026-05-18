@SCENARIO_OUTLINE_REPORT
Feature: Scenario Outline Report Validation
  Validate that BehaveX correctly expands Scenario Outline examples into
  individual scenarios across all report formats with proper parameter
  substitution and independent status tracking per instance.

  Scenario: Scenario Outline example values appear as separate entries in the HTML report
    When I run the behavex command targeting the "xml_report_features/xml_validation_tests.feature" feature
    Then I should see the generated HTML report contains the "alpha" string
    And I should see the generated HTML report contains the "beta" string

  Scenario: JSON report includes parameter values for each Scenario Outline instance
    When I run the behavex command targeting the "xml_report_features/xml_validation_tests.feature" feature
    Then I should see scenario outline parameters in the JSON report

  Scenario: JUnit XML contains one testcase entry per Scenario Outline example
    When I run the behavex command targeting the "xml_report_features/xml_validation_tests.feature" feature
    Then I should see the scenario name "alpha" in the JUnit XML report
    And I should see the scenario name "beta" in the JUnit XML report

  Scenario: HTML and JUnit XML reports agree on the total scenario count including all outline instances
    When I run the behavex command targeting the "xml_report_features/xml_validation_tests.feature" feature
    Then I should see the same number of scenarios in the reports

@REPORT_OUTPUT_STRUCTURE
Feature: Report Output Structure Validation
  Validate that BehaveX generates all expected output files in the correct
  location after every test run. All three report types must be present:
  HTML, JSON, and JUnit XML.

  Scenario: All report files are generated after a mixed-status test run
    When I run the behavex command targeting the "xml_report_features/xml_validation_tests.feature" feature
    Then I should see the HTML report was generated
    And I should see the JSON report was generated
    And I should see the JUnit XML report was generated

  Scenario: All report files are generated after a passing-only test run
    When I run the behavex command targeting the "background_features/background_tests.feature" feature
    Then I should see the HTML report was generated
    And I should see the JSON report was generated
    And I should see the JUnit XML report was generated

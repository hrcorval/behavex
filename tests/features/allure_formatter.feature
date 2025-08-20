Feature: Allure Formatter Complete Test Suite

  # Integration Tests - Testing the formatter when integrated with BehaveX execution

  @ALLURE_FORMATTER
  Scenario: Validate Allure formatter generates basic files with passing tests
    Given I have installed behavex
    When I run the behavex command with allure formatter and passing tests
    Then I should see the following behavex console outputs and exit code "0"
    | output_line   |
    | Exit code: 0  |
    And I should not see error messages in the output
    And I should see that allure-results directory was created
    And I should see that allure result files were generated for passing scenarios
    And I should see that categories.json file was created
    And I should see that container files were created

  @ALLURE_FORMATTER
  Scenario: Validate Allure formatter generates files with failing tests
    Given I have installed behavex
    When I run the behavex command with allure formatter and failing tests
    Then I should see the following behavex console outputs and exit code "1"
    | output_line   |
    | Exit code: 1  |
    And I should not see exception messages in the output
    And I should see that allure-results directory was created
    And I should see that allure result files were generated for failing scenarios
    And I should see that categories.json contains Product Defects category
    And I should see that environment-categories.json file was created

  @ALLURE_FORMATTER
  Scenario: Validate Allure formatter with custom output directory
    Given I have installed behavex
    When I run the behavex command with allure formatter using custom output directory "custom-allure-results"
    Then I should see the following behavex console outputs and exit code "0"
    | output_line   |
    | Exit code: 0  |
    And I should not see error messages in the output
    And I should see that custom allure-results directory "custom-allure-results" was created
    And I should see that allure result files were generated in custom directory "custom-allure-results"

  @ALLURE_FORMATTER
  Scenario: Validate Allure formatter with mixed test results
    Given I have installed behavex
    When I run the behavex command with allure formatter and mixed test results
    Then I should see the following behavex console outputs and exit code "1"
    | output_line   |
    | Exit code: 1  |
    And I should not see exception messages in the output
    And I should see that allure-results directory was created
    And I should see that allure result files were generated for mixed scenarios
    And I should see that categories.json contains both Product Defects and Test Defects categories

  @ALLURE_FORMATTER
  Scenario: Validate Allure formatter processes scenario tags correctly
    Given I have installed behavex
    When I run the behavex command with allure formatter and tagged scenarios
    Then I should see the following behavex console outputs and exit code "0"
    | output_line   |
    | Exit code: 0  |
    And I should not see error messages in the output
    And I should see that allure result files contain correct tags and labels
    And I should see that epic and story labels are correctly processed
    And I should see that severity labels are correctly processed

  @ALLURE_FORMATTER
  Scenario: Validate Allure formatter handles basic scenario data
    Given I have installed behavex
    When I run the behavex command with allure formatter and scenario with table data
    Then I should see the following behavex console outputs and exit code "0"
    | output_line   |
    | Exit code: 0  |
    And I should not see error messages in the output
    And I should see that allure-results directory was created
    And I should see that allure result files were generated for passing scenarios

  @ALLURE_FORMATTER
  Scenario: Validate Allure formatter handles basic text scenarios
    Given I have installed behavex
    When I run the behavex command with allure formatter and scenario with multiline text
    Then I should see the following behavex console outputs and exit code "0"
    | output_line   |
    | Exit code: 0  |
    And I should not see error messages in the output
    And I should see that allure-results directory was created
    And I should see that allure result files were generated for passing scenarios

  @ALLURE_FORMATTER
  Scenario: Validate Allure formatter with no-formatter-attach-logs flag
    Given I have installed behavex
    When I run the behavex command with allure formatter and no log attachments
    Then I should see the following behavex console outputs and exit code "0"
    | output_line   |
    | Exit code: 0  |
    And I should not see error messages in the output
    And I should see that allure-results directory was created
    And I should see that allure result files were generated for passing scenarios
    And I should see that allure result files do not contain scenario log attachments

  @ALLURE_FORMATTER @STANDALONE
  Scenario: Validate Allure formatter standalone script functionality
    Given I have installed behavex
    And I have a valid BehaveX report.json file
    When I run the allure formatter script directly with the report file
    Then I should see that the script executes successfully
    And I should see that allure result files were generated by the script
    And I should see that all expected allure files are present

  @ALLURE_FORMATTER @ERROR_HANDLING
  Scenario: Validate Allure formatter handles invalid JSON input
    Given I have installed behavex
    And I have an invalid JSON report file
    When I run the allure formatter script with the invalid JSON file
    Then I should see an error message about invalid JSON format
    And the script should exit with non-zero code

  @ALLURE_FORMATTER @ERROR_HANDLING
  Scenario: Validate Allure formatter handles missing report file
    Given I have installed behavex
    When I run the allure formatter script with a non-existent report file
    Then I should see an error message about missing report file
    And the script should exit with non-zero code

  @ALLURE_FORMATTER @DEFECT_CATEGORIZATION
  Scenario: Validate Allure formatter categorizes failed assertions as Product Defects
    Given I have installed behavex
    When I run the behavex command with allure formatter and assertion failure tests
    Then I should see the following behavex console outputs and exit code "1"
    | output_line   |
    | Exit code: 1  |
    And I should see that allure-results directory was created
    And I should see that categories.json contains Product Defects category
    And I should see that failed assertion scenarios are categorized as Product Defects

  @ALLURE_FORMATTER @DEFECT_CATEGORIZATION
  Scenario: Validate Allure formatter categorizes undefined steps as Test Defects
    Given I have installed behavex
    When I run the behavex command with allure formatter and undefined step tests
    Then I should see the following behavex console outputs and exit code "1"
    | output_line   |
    | Exit code: 1  |
    And I should see that allure-results directory was created
    And I should see that categories.json contains Test Defects category
    And I should see that undefined step scenarios are categorized as Test Defects

  @ALLURE_FORMATTER @DEFECT_CATEGORIZATION
  Scenario: Validate Allure formatter categorizes error scenarios as Product Defects
    Given I have installed behavex
    When I run the behavex command with allure formatter and error exception tests
    Then I should see the following behavex console outputs and exit code "1"
    | output_line   |
    | Exit code: 1  |
    And I should see that allure-results directory was created
    And I should see that categories.json contains Product Defects category
    And I should see that error scenarios are categorized as Product Defects

  @ALLURE_FORMATTER @DEFECT_CATEGORIZATION
  Scenario: Validate Allure formatter comprehensive defect categorization
    Given I have installed behavex
    When I run the behavex command with allure formatter and comprehensive failure tests
    Then I should see the following behavex console outputs and exit code "1"
    | output_line   |
    | Exit code: 1  |
    And I should see that allure-results directory was created
    And I should see that categories.json contains both Product Defects and Test Defects categories
    And I should see that failed scenarios are properly categorized by failure type
    And I should see that undefined scenarios are categorized as Test Defects
    And I should see that error scenarios are categorized as Product Defects

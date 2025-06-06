Feature: Allure Formatter Complete Test Suite

  # Integration Tests - Testing the formatter when integrated with BehaveX execution

  @ALLURE_FORMATTER @INTEGRATION
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

  @ALLURE_FORMATTER @INTEGRATION
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

  @ALLURE_FORMATTER @INTEGRATION
  Scenario: Validate Allure formatter with custom output directory
    Given I have installed behavex
    When I run the behavex command with allure formatter using custom output directory "custom-allure-results"
    Then I should see the following behavex console outputs and exit code "0"
    | output_line   |
    | Exit code: 0  |
    And I should not see error messages in the output
    And I should see that custom allure-results directory "custom-allure-results" was created
    And I should see that allure result files were generated in custom directory "custom-allure-results"

  @ALLURE_FORMATTER @INTEGRATION
  Scenario: Validate Allure formatter with mixed test results
    Given I have installed behavex
    When I run the behavex command with allure formatter and mixed test results
    Then I should see the following behavex console outputs and exit code "1"
    | output_line   |
    | Exit code: 1  |
    And I should not see exception messages in the output
    And I should see that allure-results directory was created
    And I should see that allure result files were generated for mixed scenarios
    And I should see that categories.json contains both Product Defects and Broken Tests categories

  @ALLURE_FORMATTER @INTEGRATION
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

  @ALLURE_FORMATTER @INTEGRATION
  Scenario: Validate Allure formatter handles basic scenario data
    Given I have installed behavex
    When I run the behavex command with allure formatter and scenario with table data
    Then I should see the following behavex console outputs and exit code "0"
    | output_line   |
    | Exit code: 0  |
    And I should not see error messages in the output
    And I should see that allure-results directory was created
    And I should see that allure result files were generated for passing scenarios

  @ALLURE_FORMATTER @INTEGRATION
  Scenario: Validate Allure formatter handles basic text scenarios
    Given I have installed behavex
    When I run the behavex command with allure formatter and scenario with multiline text
    Then I should see the following behavex console outputs and exit code "0"
    | output_line   |
    | Exit code: 0  |
    And I should not see error messages in the output
    And I should see that allure-results directory was created
    And I should see that allure result files were generated for passing scenarios

  @ALLURE_FORMATTER @INTEGRATION
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

  @ALLURE_FORMATTER @INTEGRATION @STANDALONE
  Scenario: Validate Allure formatter standalone script functionality
    Given I have installed behavex
    And I have a valid BehaveX report.json file
    When I run the allure formatter script directly with the report file
    Then I should see that the script executes successfully
    And I should see that allure result files were generated by the script
    And I should see that all expected allure files are present

  @ALLURE_FORMATTER @INTEGRATION @ERROR_HANDLING
  Scenario: Validate Allure formatter handles invalid JSON input
    Given I have installed behavex
    And I have an invalid JSON report file
    When I run the allure formatter script with the invalid JSON file
    Then I should see an error message about invalid JSON format
    And the script should exit with non-zero code

  @ALLURE_FORMATTER @INTEGRATION @ERROR_HANDLING
  Scenario: Validate Allure formatter handles missing report file
    Given I have installed behavex
    When I run the allure formatter script with a non-existent report file
    Then I should see an error message about missing report file
    And the script should exit with non-zero code

  # Unit Tests - Testing individual methods of the AllureBehaveXFormatter class

  @ALLURE_FORMATTER @UNIT_TESTS
  Scenario: Validate MIME type detection functionality
    Given I have an AllureBehaveXFormatter instance
    When I test the MIME type detection for various file extensions
    Then I should see correct MIME types returned for all supported formats

  @ALLURE_FORMATTER @UNIT_TESTS
  Scenario: Validate error message sanitization functionality
    Given I have an AllureBehaveXFormatter instance
    When I test error message sanitization with various inputs
    Then I should see properly sanitized error messages

  @ALLURE_FORMATTER @UNIT_TESTS
  Scenario: Validate package name extraction from file paths
    Given I have an AllureBehaveXFormatter instance
    When I test package name extraction from various file paths
    Then I should see correct package names extracted

  @ALLURE_FORMATTER @UNIT_TESTS
  Scenario: Validate table formatting to CSV functionality
    Given I have an AllureBehaveXFormatter instance
    When I test table formatting with sample table data
    Then I should see properly formatted CSV output

  @ALLURE_FORMATTER @UNIT_TESTS
  Scenario: Validate step line extraction from image filenames
    Given I have an AllureBehaveXFormatter instance
    When I test step line extraction from various image filenames
    Then I should see correct step line numbers extracted

Feature: Output Folder

  Scenario Outline: BehaveX refuses an output folder that holds the project or its features, "<output_folder>"
    Given I have installed behavex
    When I run the behavex command in a new project with the output folder "<output_folder>"
    Then I should see the following behavex console outputs and exit code "1"
    | output_line                                                           |
    | and BehaveX deletes it before each run; use a dedicated output folder |
    And I should see the project feature files were kept
    Examples:
      | output_folder |
      | .             |
      | features      |

  Scenario: BehaveX accepts a dedicated output folder inside the project
    Given I have installed behavex
    When I run the behavex command in a new project with the output folder "reports"
    Then I should see the following behavex console outputs and exit code "0"
    | output_line  |
    | Exit code: 0 |
    And I should see the project feature files were kept

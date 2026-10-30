Feature: Rename Tests

  Scenario: This scenario changes the name of the scenario by adding a suffix
    Given I rename the scenario from context to have the suffix " - RENAMED"

  Scenario Outline: This scenario changes the name of the scenario outline by adding a suffix
    Given I rename the scenario from context to have the suffix "<suffix>"
    Examples: EXAMPLES_TITLE
      | suffix          |
      | - RENAMED_1       |
      | - RENAMED_2     |
    Examples: "EXAMPLES_TITLE2"
      | suffix          |
      | - RENAMED_3       |
      | - RENAMED_4     |

  Scenario: This scenario changes the name of the feature by adding a suffix
    Given I rename the feature from context to have the suffix " - RENAMED"

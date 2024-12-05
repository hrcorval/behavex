Feature: Behavex arguments

  @BEHAVEX_ARGUMENTS
  Scenario Outline: Validate BehaveX arguments with <argument_separator> separator
    Given I have installed behavex
    When I run the behavex command using "<argument_separator>" separator for "passing_tests.feature" feature with the following scheme, processes and tags
    | parallel_scheme   | parallel_processes   | tags     |
    | <parallel_scheme> | <parallel_processes> | <tags>   |
    Then I should see the following behavex console outputs and exit code "0"
    | output_line                                   |
    | PARALLEL_PROCESSES  \| <parallel_processes>   |
    | PARALLEL_SCHEME     \| <parallel_scheme>      |
    | Exit code: 0                                  |
    And I should not see error messages in the output
    And I should see the same number of scenarios in the reports
    And I should see the generated HTML report does not contain internal BehaveX variables and tags
    Examples:
      | argument_separator | parallel_processes | parallel_scheme | tags                                                |
      | blank              | 1                  | scenario        | -t @PASSING_TAG_1,@PASSING_TAG_2,@PASSING_TAG_3     |
      | equal              | 1                  | scenario        | -t=@PASSING_TAG_1,@PASSING_TAG_2,@PASSING_TAG_3     |
      | blank              | 1                  | scenario        | -t @PASSING_TAG_1,PASSING_TAG_3 -t ~@PASSING_TAG_2  |
      | equal              | 1                  | scenario        | -t @PASSING_TAG_1,PASSING_TAG_3 -t ~@PASSING_TAG_2  |
      | blank              | 2                  | scenario        | -t @PASSING_TAG_1,@PASSING_TAG_2,@PASSING_TAG_3     |
      | equal              | 2                  | scenario        | -t=@PASSING_TAG_1,@PASSING_TAG_2,@PASSING_TAG_3     |
      | blank              | 2                  | scenario        | -t @PASSING_TAG_1,PASSING_TAG_3 -t ~@PASSING_TAG_2  |
      | equal              | 2                  | scenario        | -t @PASSING_TAG_1,PASSING_TAG_3 -t ~@PASSING_TAG_2  |
      | blank              | 1                  | feature         | -t @PASSING_TAG_1,@PASSING_TAG_2,@PASSING_TAG_3     |
      | equal              | 1                  | feature         | -t=@PASSING_TAG_1,@PASSING_TAG_2,@PASSING_TAG_3     |
      | blank              | 1                  | feature         | -t @PASSING_TAG_1,PASSING_TAG_3 -t ~@PASSING_TAG_2  |
      | equal              | 1                  | feature         | -t @PASSING_TAG_1,PASSING_TAG_3 -t ~@PASSING_TAG_2  |
      | blank              | 2                  | feature         | -t @PASSING_TAG_1,@PASSING_TAG_2,@PASSING_TAG_3     |
      | equal              | 2                  | feature         | -t=@PASSING_TAG_1,@PASSING_TAG_2,@PASSING_TAG_3     |
      | blank              | 2                  | feature         | -t @PASSING_TAG_1,PASSING_TAG_3 -t ~@PASSING_TAG_2  |
      | equal              | 2                  | feature         | -t @PASSING_TAG_1,PASSING_TAG_3 -t ~@PASSING_TAG_2  |
    Examples:
      | argument_separator | parallel_processes | parallel_scheme | tags   |
      | blank              | 1                  | scenario        |        |
      | equal              | 1                  | scenario        |        |
      | blank              | 2                  | scenario        |        |
      | equal              | 2                  | scenario        |        |
      | blank              | 1                  | feature         |        |
      | equal              | 1                  | feature         |        |
      | blank              | 2                  | feature         |        |
      | equal              | 2                  | feature         |        |

  @BEHAVEX_ARGUMENTS
  Scenario Outline: Validate BehaveX arguments considering feature name with scenario line
    When I run the behavex command using "<argument_separator>" separator for "passing_tests.feature:13" feature with the following scheme, processes and tags
    | parallel_scheme   | parallel_processes   | tags     |
    | <parallel_scheme> | <parallel_processes> | <tags>   |
    Then I should see the following behavex console outputs and exit code "0"
    | output_line                                   |
    | PARALLEL_PROCESSES  \| <parallel_processes>   |
    | PARALLEL_SCHEME     \| <parallel_scheme>      |
    | Exit code: 0                                  |
    And I should not see error messages in the output
    And I should see the same number of scenarios in the reports not considering the skipped scenarios
    Examples:
      | argument_separator | parallel_processes | parallel_scheme | tags  |
      | blank              | 1                  | scenario        |       |
      | equal              | 1                  | feature         |       |
      | blank              | 2                  | scenario        |       |
      | equal              | 2                  | feature         |       |


  @BEHAVEX_ARGUMENTS
  Scenario Outline: Validate BehaveX arguments with multiple feature paths
    When I run the behavex command using "<argument_separator>" separator for "passing_tests.feature" and "failing_tests.feature" features with the following scheme, processes and tags
    | parallel_scheme   | parallel_processes   | tags     |
    | <parallel_scheme> | <parallel_processes> | <tags>   |
    Then I should see the following behavex console outputs and exit code "1"
    | output_line                                   |
    | PARALLEL_PROCESSES  \| <parallel_processes>   |
    | PARALLEL_SCHEME     \| <parallel_scheme>      |
    | Exit code: 1                                  |
    And I should not see exception messages in the output
    And I should see the same number of scenarios in the reports not considering the skipped scenarios
    And I should see the generated HTML report does not contain internal BehaveX variables and tags
    Examples:
      | argument_separator | parallel_processes | parallel_scheme | tags  |
      | blank              | 1                  | scenario        |       |
      | equal              | 1                  | feature         |       |
      | blank              | 2                  | scenario        |       |
      | equal              | 2                  | feature         |       |


@BEHAVEX_ARGUMENTS @SCENARIO_NAME
  Scenario Outline: Validate BehaveX arguments by running a scenario by its name
    When I run the behavex command with scenario name "<test_scenario_name>" and the following scheme, processes and tags
    | parallel_scheme   | parallel_processes   | tags     |
    | <parallel_scheme> | <parallel_processes> | <tags>   |
    Then I should see the following behavex console outputs and exit code "0"
    | output_line                                   |
    | PARALLEL_PROCESSES  \| <parallel_processes>   |
    | PARALLEL_SCHEME     \| <parallel_scheme>      |
    | Exit code: 0                                  |
    And I should not see exception messages in the output
    And I should see the HTML report was generated and contains "<total_scenarios>" scenarios
    And I should see the same number of scenarios in the reports not considering the skipped scenarios
    And I should see the generated HTML report does not contain internal BehaveX variables and tags
    Examples:
      | argument_separator | parallel_processes | parallel_scheme | tags              | test_scenario_name                       | total_scenarios |
      | blank              | 1                  | scenario        |                   | This test should pass and contains       | 4               |
      | equal              | 1                  | feature         |                   | This test should pass and contains       | 4               |
      | blank              | 2                  | scenario        |                   | This test should pass and contains       | 4               |
      | equal              | 2                  | feature         |                   | This test should pass and contains       | 4               |
      | equal              | 2                  | feature         |                   | Non existing scenario                    | 0               |
      | equal              | 2                  | scenario        |                   | Non existing scenario                    | 0               |
      | equal              | 2                  | scenario        |                   | This test should pass and contains a tag | 1               |
      | equal              | 2                  | scenario        | -t PASSING_TAG_1  | This test should pass and contains a tag | 1               |
      | equal              | 2                  | feature         | -t PASSING_TAG_1  | This test should pass and contains a tag | 1               |
      | equal              | 2                  | scenario        | -t @PASSING_TAG_1 | This test should pass and contains a tag | 1               |
      | equal              | 2                  | feature         | -t @PASSING_TAG_1 | This test should pass and contains a tag | 1               |

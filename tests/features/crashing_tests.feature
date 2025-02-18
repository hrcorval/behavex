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
      # TODO: Uncomment when it is possible to detect the errors in after_feature and after_all hooks
      # | after_all       | 1                  | scenario        |
      # | after_feature   | 1                  | scenario        |
      | after_scenario  | 1                  | scenario        |
      | after_step      | 1                  | scenario        |
      | after_tag       | 1                  | scenario        |
      | before_all      | 2                  | scenario        |
      | before_feature  | 2                  | scenario        |
      | before_scenario | 2                  | scenario        |
      | before_step     | 2                  | scenario        |
      | before_tag      | 2                  | scenario        |
      # TODO: Uncomment when it is possible to detect the errors in after_feature and after_all hooks
      # | after_all       | 2                  | scenario        |
      # | after_feature   | 2                  | scenario        |
      | after_scenario  | 2                  | scenario        |
      | after_step      | 2                  | scenario        |
      | after_tag       | 2                  | scenario        |

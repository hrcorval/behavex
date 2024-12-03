Feature: Behavex arguments

  @BEHAVEX_ARGUMENTS
  Scenario Outline: Behavex arguments with <argument_separator> separator
    Given I have installed behavex
    When I run the behavex command using "<argument_separator>" separator with the following scheme, processes and tags
    | parallel_scheme   | parallel_processes   | tags     |
    | <parallel_scheme> | <parallel_processes> | <tags>   |
    Then I should see the following behavex console outputs and exit code "0"
    | output_line                                   |
    | PARALLEL_PROCESSES  \| <parallel_processes>   |
    | PARALLEL_SCHEME     \| <parallel_scheme>      |
    | Exit code: 0                                  |
    Examples:
      | argument_separator | parallel_processes | parallel_scheme | tags                                            |
      | blank              | 1                  | scenario        | -t @PASSING_TAG_1,@PASSING_TAG_2,@PASSING_TAG_3 |
      | equal              | 1                  | scenario        | -t=@PASSING_TAG_1,@PASSING_TAG_2,@PASSING_TAG_3 |
      | blank              | 2                  | scenario        | -t @PASSING_TAG_1,@PASSING_TAG_2,@PASSING_TAG_3 |
      | equal              | 2                  | scenario        | -t=@PASSING_TAG_1,@PASSING_TAG_2,@PASSING_TAG_3 |

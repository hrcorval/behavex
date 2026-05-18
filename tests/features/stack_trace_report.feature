@STACK_TRACE_REPORT
Feature: Stack Trace in HTML Report
    As a BehaveX user
    I want failed scenarios to expose the full stack trace in the HTML report
    So that I can diagnose chained exceptions without inspecting log files

    @STACK_TRACE_REPORT @SIMPLE_EXCEPTION
    Scenario: Simple exception shows clickable error and stack trace content
        Given I have installed behavex
        When I run the behavex command with chained exception tests
        Then I should see the following behavex console outputs and exit code "1"
            | output_line  |
            | Exit code: 1 |
        And I should see the HTML report was generated
        And the HTML report should contain clickable stack trace markers for failed scenarios
        And the HTML report should contain hidden stack trace content blocks

    @STACK_TRACE_REPORT @CHAINED_EXCEPTION
    Scenario: Chained exception includes all levels in the stack trace
        Given I have installed behavex
        When I run the behavex command with chained exception tests
        Then I should see the following behavex console outputs and exit code "1"
            | output_line  |
            | Exit code: 1 |
        And I should see the HTML report was generated
        And the HTML report should contain the chained exception cause chain

    @STACK_TRACE_REPORT @PASSING_SCENARIO
    Scenario: Passing scenarios do not have stack trace markers
        Given I have installed behavex
        When I run the behavex command with only passing chained exception test
        Then I should see the following behavex console outputs and exit code "0"
            | output_line  |
            | Exit code: 0 |
        And I should see the HTML report was generated
        And the HTML report should not contain stack trace markers

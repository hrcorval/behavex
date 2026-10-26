Feature: Undefined Steps

  Scenario: Every step is defined
    Given a passing step
    And a step defined with the regex matcher of environment.py
    And a step defined in an imported library

  Scenario: One step is undefined
    Given a passing step
    When a step nobody defined
    Then a passing step

  Scenario Outline: One example of an outline uses an undefined step
    Given a <kind> step

    Examples:
      | kind    |
      | passing |
      | missing |

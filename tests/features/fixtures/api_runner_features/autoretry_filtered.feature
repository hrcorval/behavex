Feature: Autoretry Filtered

  @INCLUDED
  Scenario: Included scenario
    Given a passing step

  @AUTORETRY @INCLUDED
  Scenario: Included autoretry scenario
    Given a passing step

  @AUTORETRY
  Scenario: Autoretry scenario excluded by the tag filter
    Given a passing step

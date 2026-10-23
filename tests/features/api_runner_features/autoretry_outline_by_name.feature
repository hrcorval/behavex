Feature: Autoretry Outline Filtered By Name

  Scenario: Scenario excluded by the name filter
    Given a passing step

  @AUTORETRY
  Scenario Outline: Autoretry outline row <row>
    Given a passing step
    Examples:
      | row      |
      | selected |
      | excluded |

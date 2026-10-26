Feature: Undefined Background Step

  Background:
    Given a background step nobody defined

  Scenario: Inherits the undefined background step
    Given a passing step

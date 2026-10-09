Feature: Partial hook failure

  Scenario: First scenario passes cleanly
    Given a passing condition

  Scenario: Second scenario fails its before_scenario hook
    Given a passing condition

  Scenario: Third scenario should also pass cleanly
    Given a passing condition

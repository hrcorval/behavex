Feature: Worker Hooks With A Behave Stage

  Scenario: Staged environment shares values through the worker hooks
    Then the shared stage name should be "product"

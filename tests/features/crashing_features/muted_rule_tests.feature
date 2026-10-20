Feature: Muted Rule Tests

  Rule: Muted rule

    @CRASHING @SERIAL @MUTE
    Scenario: Muted passing scenario under a rule
      Given a passing condition
      Then I perform the condition

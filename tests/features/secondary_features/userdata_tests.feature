Feature: Userdata Tests

  @USERDATA
  Scenario: Userdata key is accessible via define parameter
    Given the userdata key "test_udkey" equals "test_udvalue"

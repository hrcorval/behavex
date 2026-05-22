Feature: Configuration file support

  BehaveX auto-discovers a behavex.cfg or behavex.ini file in the current
  working directory and reads params from it. CLI arguments always take
  priority over config file values.

  Background:
    Given I have installed behavex


  # ─────────────────────────────────────────────────────────────────────────
  # Params read from config file (behavex.cfg)
  # ─────────────────────────────────────────────────────────────────────────

  @CONFIG_FILE @CONFIG_FILE_PARAMS
  Scenario Outline: BehaveX reads <param> from a behavex.cfg config file
    Given a "behavex.cfg" config file with param "<param>" set to "<value>"
    When I run behavex from the config file directory for feature "passing_tests.feature"
    Then I should see the following behavex console outputs and exit code "0"
      | output_line       |
      | <expected_output> |

    Examples:
      | param              | value   | expected_output                |
      | parallel_processes | 2       | PARALLEL_PROCESSES  \| 2       |
      | parallel_scheme    | feature | PARALLEL_SCHEME     \| feature |
      | logging_level      | DEBUG   | LOGGING_LEVEL       \| DEBUG   |

  @CONFIG_FILE @CONFIG_FILE_PARAMS
  Scenario: BehaveX reads dry_run from a behavex.cfg config file
    Given a "behavex.cfg" config file with param "dry_run" set to "True"
    When I run behavex from the config file directory for feature "passing_tests.feature"
    Then I should see the following behavex console outputs and exit code "0"
      | output_line       |
      | Dry run completed |

  @CONFIG_FILE @CONFIG_FILE_PARAMS
  Scenario: BehaveX reads tags_to_skip from [test_run] section of behavex.cfg
    Given a "behavex.cfg" config file with section "[test_run]" param "tags_to_skip" set to "PASSING_TAG_1"
    When I run behavex from the config file directory for feature "passing_tests.feature"
    Then I should see the following behavex console outputs and exit code "0"
      | output_line        |
      | 4 scenarios passed |

  @CONFIG_FILE @CONFIG_FILE_PARAMS
  Scenario: BehaveX reads define from a behavex.cfg config file
    Given a "behavex.cfg" config file with param "define" set to "test_udkey=test_udvalue"
    When I run behavex from the config file directory for feature "userdata_tests.feature"
    Then I should see the following behavex console outputs and exit code "0"
      | output_line       |
      | 1 scenario passed |

  @CONFIG_FILE @CONFIG_FILE_PARAMS
  Scenario: BehaveX reads show_progress_bar from a behavex.cfg config file
    Given a "behavex.cfg" config file with params
      | param              | value |
      | show_progress_bar  | True  |
      | parallel_processes | 2     |
    When I run behavex from the config file directory for feature "passing_tests.feature"
    Then I should see the following behavex console outputs and exit code "0"
      | output_line               |
      | Executed scenarios: 100%\| |

  @CONFIG_FILE @CONFIG_FILE_PARAMS
  Scenario: BehaveX reads tags from a behavex.cfg config file
    Given a "behavex.cfg" config file with param "tags" set to "@PASSING_TAG_1"
    When I run behavex from the config file directory for feature "passing_tests.feature"
    Then I should see the following behavex console outputs and exit code "0"
      | output_line                        |
      | TAGS                \| @PASSING_TAG_1 |
      | 1 scenario passed                  |

  @CONFIG_FILE @CONFIG_FILE_PARAMS
  Scenario: BehaveX reads output path from the [output] section of behavex.cfg
    Given a "behavex.cfg" config file with section "[output]" param "path" set to "cfg_custom_output"
    And no explicit output folder is provided
    When I run behavex from the config file directory for feature "passing_tests.feature"
    Then I should see the following behavex console outputs and exit code "0"
      | output_line       |
      | cfg_custom_output |


  # ─────────────────────────────────────────────────────────────────────────
  # behavex.ini and behave.ini are also auto-discovered
  # ─────────────────────────────────────────────────────────────────────────

  @CONFIG_FILE @CONFIG_FILE_INI
  Scenario Outline: BehaveX reads <param> from a behavex.ini config file
    Given a "behavex.ini" config file with param "<param>" set to "<value>"
    When I run behavex from the config file directory for feature "passing_tests.feature"
    Then I should see the following behavex console outputs and exit code "0"
      | output_line       |
      | <expected_output> |

    Examples:
      | param              | value   | expected_output                |
      | parallel_processes | 2       | PARALLEL_PROCESSES  \| 2       |
      | parallel_scheme    | feature | PARALLEL_SCHEME     \| feature |

  @CONFIG_FILE @CONFIG_FILE_INI
  Scenario: BehaveX reads tags from a behavex.ini config file
    Given a "behavex.ini" config file with param "tags" set to "@PASSING_TAG_2"
    When I run behavex from the config file directory for feature "passing_tests.feature"
    Then I should see the following behavex console outputs and exit code "0"
      | output_line                        |
      | TAGS                \| @PASSING_TAG_2 |
      | 1 scenario passed                  |

  @CONFIG_FILE @CONFIG_FILE_INI
  Scenario: BehaveX reads parallel_processes from a behave.ini config file
    Given a "behave.ini" config file with param "parallel_processes" set to "2"
    When I run behavex from the config file directory for feature "passing_tests.feature"
    Then I should see the following behavex console outputs and exit code "0"
      | output_line                     |
      | PARALLEL_PROCESSES  \| 2        |


  # ─────────────────────────────────────────────────────────────────────────
  # CLI arguments take priority over the config file
  # ─────────────────────────────────────────────────────────────────────────

  @CONFIG_FILE @CONFIG_FILE_PRIORITY
  Scenario Outline: CLI argument overrides config file value for <param>
    Given a "behavex.cfg" config file with param "<param>" set to "<config_value>"
    And the CLI args "<cli_args>"
    When I run behavex from the config file directory for feature "passing_tests.feature"
    Then I should see the following behavex console outputs and exit code "0"
      | output_line       |
      | <expected_output> |

    Examples:
      | param              | config_value | cli_args                    | expected_output                 |
      | parallel_processes | 3            | --parallel-processes 1      | PARALLEL_PROCESSES  \| 1        |
      | parallel_scheme    | feature      | --parallel-scheme scenario  | PARALLEL_SCHEME     \| scenario  |
      | logging_level      | DEBUG        | --logging-level WARNING     | LOGGING_LEVEL       \| WARNING   |

  @CONFIG_FILE @CONFIG_FILE_PRIORITY
  Scenario: CLI tag overrides tags defined in config file
    Given a "behavex.cfg" config file with param "tags" set to "@PASSING_TAG_1"
    And the CLI args "-t @PASSING_TAG_2"
    When I run behavex from the config file directory for feature "passing_tests.feature"
    Then I should see the following behavex console outputs and exit code "0"
      | output_line                        |
      | TAGS                \| @PASSING_TAG_2 |
      | 1 scenario passed                  |
    And I should not see the following in the behavex console output
      | output_line                        |
      | TAGS                \| @PASSING_TAG_1 |


  # ─────────────────────────────────────────────────────────────────────────
  # Explicit --config overrides auto-discovered file
  # ─────────────────────────────────────────────────────────────────────────

  @CONFIG_FILE @CONFIG_FILE_PRIORITY
  Scenario: Explicit --config flag takes priority over auto-discovered behavex.cfg
    Given a "behavex.cfg" config file with param "parallel_processes" set to "3"
    And an explicit config file with param "parallel_processes" set to "2"
    When I run behavex from the config file directory for feature "passing_tests.feature"
    Then I should see the following behavex console outputs and exit code "0"
      | output_line                 |
      | PARALLEL_PROCESSES  \| 2   |

  @CONFIG_FILE @CONFIG_FILE_PRIORITY
  Scenario: behavex.cfg takes priority over behavex.ini when both are present
    Given a "behavex.cfg" config file with param "parallel_processes" set to "2"
    And a "behavex.ini" config file with param "parallel_processes" set to "3"
    When I run behavex from the config file directory for feature "passing_tests.feature"
    Then I should see the following behavex console outputs and exit code "0"
      | output_line                 |
      | PARALLEL_PROCESSES  \| 2   |

  @CONFIG_FILE @CONFIG_FILE_PRIORITY
  Scenario: behavex.ini takes priority over behave.ini when both are present
    Given a "behavex.ini" config file with param "parallel_processes" set to "2"
    And a "behave.ini" config file with param "parallel_processes" set to "3"
    When I run behavex from the config file directory for feature "passing_tests.feature"
    Then I should see the following behavex console outputs and exit code "0"
      | output_line                 |
      | PARALLEL_PROCESSES  \| 2   |


  # ─────────────────────────────────────────────────────────────────────────
  # Warnings for params incompatible with parallel execution
  # ─────────────────────────────────────────────────────────────────────────

  @CONFIG_FILE @CONFIG_FILE_WARNINGS
  Scenario: BehaveX prints a warning when a parallel-incompatible param is set in the config file
    Given a "behavex.cfg" config file with params
      | param              | value |
      | parallel_processes | 2     |
      | stop               | True  |
    When I run behavex from the config file directory for feature "passing_tests.feature"
    Then I should see the following behavex console outputs and exit code "0"
      | output_line                            |
      | not compatible with parallel execution |


  # ─────────────────────────────────────────────────────────────────────────
  # behave.ini compatibility (Issue #247 — Bug 1)
  # ConfigObj cannot parse configparser-style multi-line continuation values.
  # BehaveX must skip behave.ini when it contains no BehaveX-specific sections.
  # ─────────────────────────────────────────────────────────────────────────

  @CONFIG_FILE @CONFIG_FILE_BEHAVE_INI_COMPAT
  Scenario: BehaveX does not crash when behave.ini has multi-line continuation values
    Given a "behave.ini" file with only Behave-native settings and multi-line format values
    When I run behavex from the config file directory for feature "passing_tests.feature"
    Then I should see the following behavex console outputs and exit code "0"
      | output_line       |
      | 5 scenarios passed |

  @CONFIG_FILE @CONFIG_FILE_BEHAVE_INI_COMPAT
  Scenario: behave.ini with only Behave-native sections is not used for BehaveX configuration
    Given a "behave.ini" file with only a "[behave]" section
    When I run behavex from the config file directory for feature "passing_tests.feature"
    Then I should see the following behavex console outputs and exit code "0"
      | output_line                  |
      | PARALLEL_PROCESSES  \| 1    |

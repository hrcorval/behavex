# Changelog

All notable changes to BehaveX are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [4.6.3] - 2026-05-19

### Added
- **Config file: `define` parameter support** — `define = key=value` entries in `behavex.cfg` are now correctly passed to Behave as `--define` arguments, making userdata accessible via `context.config.userdata`.
- **Behavioral test coverage for config file parameters** — New test scenarios validate that `dry_run`, `tags_to_skip`, `define`, and `show_progress_bar` actually change system behavior when set in the config file, not just that their values are echoed in the startup summary.
- **Config file discovery hierarchy tests** — New tests verify that `behavex.cfg` takes priority over `behavex.ini`, and `behavex.ini` takes priority over `behave.ini`, when multiple config files are present.

### Fixed
- **`tags_to_skip` ignored without a tags filter** — Tags listed under `[test_run] tags_to_skip` were silently dropped when no `tags` filter was set. They are now applied unconditionally.
- **`define` single-value parsed as string** — When a single `define` entry was set in the config file, configobj returned a plain string instead of a list, causing the value to be iterated character by character. It is now correctly normalized to a list before being passed to Behave.

### Changed
- README Configuration File section updated: the `[params]` example block now only shows parameters that are fully applied from the config file. A new "Behave Arguments Not Yet Supported in Config File" subsection documents which Behave arguments are not yet applied when set via config file.

---

## [4.6.2] - 2026-05-18

### Added
- **Gherkin Rule section support** — BehaveX now correctly handles `Rule:` blocks in feature files, including proper rendering in HTML and XML reports.
- **Stack trace on error** — Clicking on a failed step in the HTML report now expands the full stack trace inline.

### Fixed
- **Non-zero exit code on parallel process failure** — Parallel runs now correctly return a non-zero exit code when any worker process fails *(contributed by [@AppeltansPieter](https://github.com/AppeltansPieter))*.
- **Exit code on ImportError** — Returns exit code 1 when step loading fails due to an `ImportError`, preventing silent failures.
- **Missing `error_lines` key** — Fixed `KeyError` in XML report generation when `error_lines` was absent from scenario data.
- **Formatter output in console** — Output from formatters is now shown in single-process runs and suppressed in multiprocess runs, eliminating duplicate console output.
- **False positive in error detection** — Fixed false positive in `then_no_error_messages` triggered when formatter output contained tag lines.
- **Allure: background steps missing** — Background steps are now correctly included in Allure report output *(contributed by [@iamkenos](https://github.com/iamkenos))*.
- **Allure: background step serialization** — Corrected background step type handling and serialization in the Allure formatter *(contributed by [@iamkenos](https://github.com/iamkenos))*.
- **Allure: exception details on background steps** — Exception and error details are now included in JSON formatter output for background steps.
- **JSON formatter: exception details** — Exception details now correctly appear in JSON output for background step failures.
- **Utils: environment variable table alignment** — Fixed column width alignment and empty key handling when printing environment variables *(contributed by [@iamkenos](https://github.com/iamkenos))*.

---

## [4.6.0] - 2025-09-12

### Added
- **Tag Expressions v2** — Native support for Cucumber-style tag expressions with boolean logic (`and`, `or`, `not`), parentheses grouping, wildcard matching (`@prefix*`, `@*suffix`, `@*substring*`), and complex filtering. Supported in Behave 1.3.0+ with zero external dependencies.

### Changed
- Removed dependency on the external `cucumber-tag-expressions` library — now fully handled natively.

---

## [4.5.1] - 2025-08-20

### Fixed
- Allure formatter now correctly distinguishes between **Product Defects** and **Test Defects** in defect categorization.

---

## [4.5.0] - 2025-08-20

### Added
- **Behave 1.3.0+ support** — BehaveX now supports newer Behave versions alongside the stable 1.2.6.
- **Interactive Execution Timeline** — New visual timeline in HTML reports displaying scenario execution order, duration, and status across parallel processes.
- **Performance overhaul** — Direct Behave Runner class integration for better programmatic control and improved status detection efficiency.

### Fixed
- HTML escaping vulnerability in step text content in HTML reports.
- Log handler issues affecting execution summary output.

---

## [4.4.2] - 2025-08-06

### Added
- Allure report support for `@allure.link` and `@allure.testcase` tags.
- Full traceback in error output with clean separation of exception message.

### Fixed
- Python 3.8 compatibility issue.
- Tag handling improvements in the Allure formatter.

---

## [4.4.1] - 2025-08-04

### Added
- **Strict ordering mode** (`--order-tests-strict`) — scenarios wait for all lower-order tests to complete before executing, enabling dependency-aware parallel runs.

### Fixed
- Execution order of scenarios when `--order-tests` flag is set.

---

## [4.4.0] - 2025-07-25

### Added
- **Test Execution Ordering** — Control the sequence of scenario and feature execution during parallel runs using `@ORDER_001`, `@ORDER_010` tags.

---

## [4.3.1] - 2025-07-16

### Fixed
- Dependency version resolution issue affecting clean installs.

---

## [4.3.0] - 2025-07-09

### Changed
- Dependency improvements for better compatibility across environments.
- Updated GitHub Actions to run tests without setuptools to catch hidden dependency issues.

---

## [4.2.4] - 2025-07-04

### Changed
- Default logging level set to `INFO`.
- Updated `behavex-images` dependency to latest version.

---

## [4.2.3] - 2025-06-27

### Fixed
- Improved handling of execution interruption — runs can now be cleanly stopped.
- `TeePrint` stdout wrapper now supports a complete file-like interface, preventing `AttributeError` exceptions.
- Python 3.8 compatibility fix.

---

## [4.2.2] - 2025-06-19

### Added
- Allure formatter now includes a **thread label** to associate scenarios with their parallel worker process.

### Fixed
- Exception handling in concurrent execution now properly catches `SystemExit`, `KeyboardInterrupt`, and `GeneratorExit` for more robust parallel runs.
- Resource cleanup in parallel execution: optimized future reference management and immediate temporary file cleanup.

---

## [4.2.1] - 2025-06-06

### Fixed
- Multiple Allure formatter issues reported by users.
- Python version compatibility fix in Allure formatter (`removesuffix` call).
- Added `--no-formatter-attach-logs` parameter support.

---

## [4.2.0] - 2025-05-28

### Added
- **Allure Reports Integration** — Generate Allure reports from BehaveX executions. Includes support for Gherkin tables, additional evidence, and hierarchical suite organization.

---

## [4.1.2] - 2025-04-07

### Added
- **Python 3.13 support**.
- HTML report minification for smaller output files.

### Fixed
- Missing context variable in BehaveX test outputs.
- Crash handling improvements for unstable test scenarios.

---

## [4.1.0] - 2025-02-17

### Added
- Process ID prefix in BehaveX output files to avoid conflicts when multiple BehaveX instances run simultaneously.

### Fixed
- `environment.py` hooks no longer execute during dry runs.
- Feature path handling: removed line breaks that caused path resolution issues.

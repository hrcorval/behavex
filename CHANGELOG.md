# Changelog

All notable changes to BehaveX are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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

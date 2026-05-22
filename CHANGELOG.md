# Changelog

All notable changes to BehaveX are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [4.7.0] - Unreleased

### Added
- **`BehaveXRunner` Python API** — BehaveX can now be invoked programmatically from Python without the CLI. `BehaveXRunner` accepts all CLI parameters as typed keyword arguments and returns a structured `RunResult`. Designed for AI agents, test orchestrators, and any automation that drives BehaveX programmatically.
- **Pydantic result models** (`behavex[api]` optional extra) — `RunResult`, `FeatureResult`, `ScenarioResult`, `StepResult`, `BackgroundResult`, and `RunSummary` provide a typed, structured view of test results. Includes convenience properties: `result.passed`, `result.summary`, `result.failed_scenarios`, `scenario.failed`, `feature.failed_scenarios`, and more.
- **`[api]` optional extra** — Pydantic is an optional dependency, not added to the base install. Existing `pip install behavex` users are fully unaffected. Install with `pip install 'behavex[api]'` to activate the Python API.

---

## [4.6.4] - 2026-05-21

### Added
- **`before_all_workers` / `after_all_workers` hooks** — Two new lifecycle hooks available in `environment.py` that run once in the coordinator process, before any parallel worker is spawned and after all workers have finished. Values set on `context` in `before_all_workers` are transparently injected into every worker's Behave context before `before_all` fires, making them readable from all hooks and step definitions as plain `context` attributes. Non-JSON-serializable values (e.g. database connections, sockets) raise a `TypeError` immediately with a clear message and a list of supported types.
- **`context.behavex` execution metadata** — BehaveX now injects a `context.behavex` namespace into every worker process, available from `before_all` onwards in any hook or step definition. Attributes: `parallel_scheme` (`'scenario'` or `'feature'`), `parallel_processes` (int), `is_worker` (bool), `worker_id` (int). Replaces the previous pattern of reading `context.config.userdata['worker_id']` directly.
- **`--no-report` flag** — Disables all file output: no output folder is created, no HTML/JSON/XML reports are written, no failures file. Evidence, logs, and images are silently redirected to the system temp directory. The exit code still reflects pass/fail. Designed for read-only environments such as Docker containers or CI runners with restricted filesystem access. The path to temporary assets is printed to the console at the end of the run.
- **Hooks in Parallel Execution documentation** — New README section with a hook firing matrix table showing exactly when each hook fires across sequential, feature-parallel, and scenario-parallel modes; full documentation for `before_all_workers` / `after_all_workers`; and a `context.behavex` attribute reference with usage examples.
- **Documentation restructured into multi-page site** — The single 1,046-line README has been split into seven focused pages on ReadTheDocs: Getting Started, Tag Expressions, Parallel Execution, Reporting, Test Management, CLI Reference, and Utilities. README is now a concise landing page linking to the full docs.

### Contributors
- Thanks to [@ngonzalez625](https://github.com/ngonzalez625) for raising the need for a no-report execution mode ([Discussion #222](https://github.com/hrcorval/behavex/discussions/222)).
- Thanks to [@sk3-25](https://github.com/sk3-25) for the discussion and design ideas behind `before_all_workers` / `after_all_workers` ([Discussion #239](https://github.com/hrcorval/behavex/discussions/239)).

---

## [4.6.3] - 2026-05-20

### Added
- **Config file: `define` parameter support** — `define = key=value` entries in `behavex.cfg` are now correctly passed to Behave as `--define` arguments, making userdata accessible via `context.config.userdata`.
- **Behavioral test coverage for config file parameters** — New test scenarios validate that `dry_run`, `tags_to_skip`, `define`, and `show_progress_bar` actually change system behavior when set in the config file, not just that their values are echoed in the startup summary.
- **Config file discovery hierarchy tests** — New tests verify that `behavex.cfg` takes priority over `behavex.ini`, and `behavex.ini` takes priority over `behave.ini`, when multiple config files are present.

### Fixed
- **`tags_to_skip` ignored without a tags filter** — Tags listed under `[test_run] tags_to_skip` were silently dropped when no `tags` filter was set. They are now applied unconditionally.
- **`define` single-value parsed as string** — When a single `define` entry was set in the config file, configobj returned a plain string instead of a list, causing the value to be iterated character by character. It is now correctly normalized to a list before being passed to Behave.
- **`dry_run` HTML report false positive on `BHX_` check** — The assertion that verifies no internal BehaveX variables appear in the HTML report used a case-insensitive search. Test keys named `bhx_test_key` / `bhx_test_value` were matching the `BHX_` prefix, causing the check to fail erroneously. Test keys renamed to avoid the collision.
- **`config file with params` step undefined on behave 1.2.6** — behave 1.2.6 strips the trailing colon from step text when a data table follows, so the step pattern `a "{filename}" config file with params:` was never matched on that version. Removed the colon from the pattern and feature file for full cross-version compatibility.

### Changed
- README Configuration File section updated: the `[params]` example block now only shows parameters that are fully applied from the config file. A new "Behave Arguments Not Yet Supported in Config File" subsection documents which Behave arguments are not yet applied when set via config file.

---

## [4.6.2] - 2026-05-18

### Added
- **Gherkin Rule section support** — BehaveX now correctly handles `Rule:` blocks in feature files, including proper rendering in HTML and XML reports. Scenarios inside `Rule` blocks are rendered under a dedicated header row in the HTML report. The `rule` field is also included in the JSON report for each scenario (`null` for scenarios outside any Rule block).
- **Stack trace on error** — Clicking on a failed step in the HTML report now expands the full stack trace inline, including chained exception cause chains. The error element is rendered with a pointer cursor and tooltip to indicate it is interactive.
- **Rule processing test suite** — New scenarios validate Rule section display in the HTML report (header row presence, correct header count per feature) and Rule metadata in the JSON report.

### Fixed
- **Non-zero exit code on parallel process failure** — Parallel runs now correctly return a non-zero exit code when any worker process fails *(contributed by [@AppeltansPieter](https://github.com/AppeltansPieter))*.
- **Exit code on ImportError** — Returns exit code 1 when step loading fails due to an `ImportError`, preventing misleading green results when the test suite was never actually executed.
- **Missing `error_lines` key** — Fixed `KeyError` in XML report generation when `error_lines` was absent from scenario data.
- **Formatter output in console** — Output from formatters is now shown in single-process runs and suppressed in multiprocess runs, eliminating duplicate console output.
- **False positive in error detection** — Fixed false positive in `then_no_error_messages` triggered when formatter output contained tag lines.
- **Parallel-execution Rule edge case** — The shallow feature copy used when dispatching a single scenario still referenced the original `feature.rules`, causing `get_all_feature_scenarios` to double-count rule scenarios in JSON reports.
- **Allure: background steps missing** — Background steps are now correctly included in Allure report output *(contributed by [@iamkenos](https://github.com/iamkenos))*.
- **Allure: background step serialization** — Corrected background step type handling and serialization in the Allure formatter *(contributed by [@iamkenos](https://github.com/iamkenos))*.
- **Allure: exception details on background steps** — Exception and error details are now included in JSON formatter output for background steps.
- **JSON formatter: exception details** — Exception details now correctly appear in JSON output for background step failures.
- **Utils: environment variable table alignment** — Fixed column width alignment and empty key handling when printing environment variables *(contributed by [@iamkenos](https://github.com/iamkenos))*.

### Breaking Changes
- Dropped support for Python 3.5, 3.6, and 3.7. The minimum supported Python version is now 3.8.

### Contributors
- Thanks to [@bombsimon](https://github.com/bombsimon) for contributing the full stack trace visibility feature in the HTML report ([PR #238](https://github.com/hrcorval/behavex/pull/238)).
- Thanks to [@chriskite](https://github.com/chriskite) for contributing support for Gherkin Rule sections ([PR #241](https://github.com/hrcorval/behavex/pull/241)).

---

## [4.6.0] - 2025-09-12

### Added
- **Tag Expressions v2** — Native support for Cucumber-style tag expressions with boolean logic (`and`, `or`, `not`), parentheses grouping, wildcard matching (`@prefix*`, `@*suffix`, `@*substring*`), case-insensitive keywords, deeply nested expressions, and complex multi-level filtering. Supported in Behave 1.3.0+ with zero external dependencies, with full backward compatibility for v1 expressions and Behave 1.2.6. Includes 39 test scenarios covering all supported patterns.

### Fixed
- Strict test execution ordering issue where scenario outlines with the same ORDER tag were running sequentially instead of in parallel. Scenarios with identical ORDER tags (e.g., `@ORDER_001`) now correctly run in parallel within their order group.

### Changed
- Removed dependency on the external `cucumber-tag-expressions` library — now fully handled natively.

### Contributors
- Thanks to [@OliverHill-Boost](https://github.com/OliverHill-Boost) for reporting the strict ordering issue with scenario outlines ([Issue #225](https://github.com/hrcorval/behavex/issues/225)).
- Thanks to [@qarampage](https://github.com/qarampage) for their insights and feature request that helped guide the development of Tag Expressions v2 support.

---

## [4.5.1] - 2025-08-20

### Fixed
- Allure formatter now correctly distinguishes between **Product Defects** and **Test Defects** in defect categorization. `failed` scenarios (assertion failures) are categorized as Product Defects; `error` and `undefined` scenarios are categorized as Test Defects. Also fixed BehaveX-to-Allure status mapping where `error` and `undefined` statuses are now properly converted to `broken` in Allure reports.

---

## [4.5.0] - 2025-08-20

### Added
- **Behave 1.3.0+ support** — BehaveX now supports newer Behave versions alongside the stable 1.2.6, using normal imports with compatibility shims to handle differences between versions.
- **Interactive Execution Timeline** — New visual timeline in HTML reports displaying scenario execution order, duration, and status with interactive tooltips across parallel workers. Only executed scenarios (passed/failed/error) are shown, with proper handling for edge cases like dry runs or empty test suites.
- **Performance overhaul** — Replaced `behave_script.main()` with direct Behave Runner class integration for better programmatic control. Execution status is now determined directly from the runner instance, eliminating all file I/O operations for status detection and removing temporary stdout file generation and merging.
- **Improved execution summary** — Enhanced data collection and more accurate status tracking throughout the test execution lifecycle, including improved handling of `error` status for features, scenarios, and steps.

### Fixed
- `worker_id` incorrectly set to process ID values in JSON reports. The `worker_id` field now properly defaults to `'0'` for non-parallel execution.
- HTML escaping vulnerability in step text content in HTML reports.
- Log handler issues affecting execution summary output.

### Changed
- Improved code organization by consolidating all imports at the top of modules (PEP 8).
- Cleaned up `setup.py` by removing redundant metadata now properly defined in `pyproject.toml`.

---

## [4.4.2] - 2025-08-06

### Added
- Allure report support for `@allure.link` and `@allure.testcase` tags, with comprehensive tag validation that gracefully handles malformed `@allure.*` tags without crashes.
- Full traceback in error output with clean separation of exception message.

### Fixed
- Python 3.8 compatibility issue.
- Allure formatter tag handling improvements.

### Contributors
- Thanks to [@BackstageBones](https://github.com/BackstageBones) for contributing the enhanced error parsing and Allure tag support functionality.

---

## [4.4.1] - 2025-08-04

### Added
- **Strict ordering mode** (`--order-tests-strict`) — scenarios wait for all lower-order tests to complete before executing, enabling dependency-aware parallel runs with guaranteed sequential completion across order groups.

### Fixed
- Execution order of scenarios when `--order-tests` flag is set.

---

## [4.4.0] - 2025-07-25

### Added
- **Test Execution Ordering** — Control the sequence of scenario and feature execution during parallel runs using `@ORDER_001`, `@ORDER_010` tags. Scenarios without order tags receive default order 9999.

---

## [4.3.1] - 2025-07-16

### Added
- Enhanced test suite with a dependency validation system to catch missing optional dependencies (such as `behavex-images`) during testing. Tests now fail clearly when required dependencies are missing, rather than silently skipping.

### Fixed
- Dependency version resolution issue affecting clean installs.

---

## [4.3.0] - 2025-07-09

### Changed
- Dependency improvements for better compatibility across environments.
- Updated GitHub Actions to run tests without `setuptools` to catch hidden dependency issues.

---

## [4.2.4] - 2025-07-04

### Added
- Improved formatter output directory management with dynamic detection of formatter-specific output directories, ensuring consistent paths between evidence storage and formatter output.
- Standardized `formatter_manager` architecture with a `DEFAULT_OUTPUT_DIR` class attribute on formatters, enabling generic and extensible formatter loading without hardcoded dependencies.

### Changed
- Default logging level set to `INFO`.
- Updated `behavex-images` dependency to latest version.

---

## [4.2.3] - 2025-06-27

### Fixed
- Improved handling of execution interruption (Ctrl+C) — `KeyboardInterrupt` and `SystemExit` are now properly propagated for graceful termination in both single-process and parallel execution modes.
- `TeePrint` stdout wrapper now supports a complete file-like interface (`isatty()`, `encoding`, `closed`, `fileno()`, etc.), preventing `AttributeError` exceptions when test code calls these methods.
- Python 3.8 compatibility fix.

### Contributors
- Thanks to [@bombsimon](https://github.com/bombsimon) for helping fix the issue with the `TeePrint` stdout wrapper.

---

## [4.2.2] - 2025-06-19

### Added
- Allure formatter now includes a **thread label** to associate scenarios with their parallel worker process.

### Fixed
- Incorrect XML report filenames when handling Windows paths or other edge-case feature paths *(reported by [@AppeltansPieter](https://github.com/AppeltansPieter))*.
- Enhanced robustness in `before_scenario` hook with error handling on every method called within the hook.
- Exception handling in concurrent execution now properly catches `SystemExit`, `KeyboardInterrupt`, and `GeneratorExit` for more robust parallel test execution.
- Resource cleanup in parallel execution: optimized future reference management and immediate temporary file cleanup.

### Contributors
- Thanks to [@withnale](https://github.com/withnale) for contributing the thread label implementation.
- Thanks to [@AppeltansPieter](https://github.com/AppeltansPieter) for reporting the XML report filename issue.

---

## [4.2.1] - 2025-06-06

### Added
- Support for parameters in Scenario Outlines in the Allure formatter.
- `--no-formatter-attach-logs` argument to disable attachment of scenario log files in Allure reports.

### Fixed
- Multiple Allure formatter issues reported by users.
- Allure formatter: stack trace of a failed test was incorrectly categorized as a test parameter.
- Allure formatter: output directory logic now correctly handles custom paths.
- Allure formatter: incorrect package names in generated reports.
- Python version compatibility fix (`removesuffix` call).

---

## [4.2.0] - 2025-05-28

### Added
- **Allure Reports Integration** — Generate Allure reports from BehaveX executions. Includes support for Gherkin tables, additional evidence, hierarchical suite organization, and full parallel execution support.

### Contributors
- Special thanks to [@afritachi](https://github.com/afritachi) for sponsoring BehaveX!

---

## [4.1.2] - 2025-04-07

### Added
- **Python 3.13 support**.
- HTML report minification using `minify-html`, replacing the deprecated `htmlmin` library.

### Fixed
- Missing context variable in BehaveX test outputs.
- Crash handling improvements for unstable test scenarios.

---

## [4.1.1]

### Fixed
- Improved exception reporting: despite the traceback being reported, the exception message was not being displayed. Both are now shown correctly.
- Display the correct exit code when execution crashes in environment hooks.

---

## [4.1.0] - 2025-02-17

### Added
- Process ID prefix in BehaveX output files to avoid conflicts when multiple BehaveX instances run simultaneously.

### Fixed
- `environment.py` hooks no longer execute during dry runs.
- Feature path handling: removed line breaks that caused path resolution issues.
- Re-executing failing scenarios using the `-rf` option now correctly considers all scenario outline examples.

### Changed
- Cosmetic improvements in documentation.

---

## [4.0.10]

### Added
- Multiple BehaveX processes can now run simultaneously by creating unique execution output files in temporary folders for each process.

### Fixed
- `environment.py` hooks are no longer executed when a dry run is performed.

---

## [4.0.9]

### Added
- Support for latest Python versions (3.12).
- Cross-platform validation (Linux, Windows, macOS) as part of the GitHub Actions workflow.
- Support for specifying scenario lines in feature paths when running BehaveX.

### Fixed
- Execution issues on Windows when running BehaveX with a feature path different from the current path.
- Encoding issues in progress bar on Windows.
- Internal `@BHX_MANUAL_DRY_RUN` tag was not removed from scenario tags after dry runs.

---

## [4.0.8]

### Added
- Enhanced parallel scenario execution management using scenario line numbers instead of scenario names. This allows running scenarios that change their name without causing issues in parallel executions.

### Fixed
- Output path hash generation now uses the feature filename and line number instead of the scenario name, preventing path mismatches when scenario names change.

---

## [4.0.7]

### Added
- Improved `KeyboardInterrupt` handling in parallel execution — all child processes are terminated before exiting.
- Simplified library documentation (README.md).
- Additional tests to validate BehaveX with the latest stable Behave version (1.2.6).
- Ability to copy the scenario name from the HTML report.

### Fixed
- Feature path generation when not specified (BehaveX now uses the current path as features path).
- Tag management in scenario outlines.
- Handling of empty feature files.
- Removed ANSI color codes from log files and HTML reporter ([fd3c375](https://github.com/hrcorval/behavex/commit/fd3c3756a13d9e47823f286022980e54e306d6da)).

---

## [4.0.5]

### Added
- `worker_id` in `context.config.userdata` to identify which worker is executing each feature or scenario in parallel runs ([PR #121](https://github.com/hrcorval/behavex/pull/121)).
- `--parallel-delay` argument to enable staggered parallel execution ([Issue #142](https://github.com/hrcorval/behavex/issues/142)).

### Fixed
- Standardized XML report generation for parallel and single-process runs ([Issue #144](https://github.com/hrcorval/behavex/issues/144)).

### Contributors
- Thanks to [@JackHerRrer](https://github.com/JackHerRrer) for implementing the `worker_id` context parameter.

---

## [4.0.2]

### Added
- Switched parallel execution core to `concurrent.futures.ProcessPoolExecutor`, avoiding crashes when a test scenario fails ([Issue #114](https://github.com/hrcorval/behavex/issues/114)).
- Information popup in HTML report with parallel execution settings and execution times (start, end, total, scenario duration).
- Display of "Untested" scenarios in the HTML report.
- `ENVIRONMENT_DETAILS` environment variable to provide environment information in JSON and HTML reports.

### Fixed
- HTML report generation hang when running in parallel and a scenario crashed.
- JUnit reports now mark unexpectedly crashed scenarios as "failed" instead of "skipped".
- Parallel execution summary now accurately reports the number of skipped scenarios.
- Progress bar issue when running tests in parallel by feature.
- Scenario tags in scenario outlines now always include tags from the outline examples.

### Contributors
- Thanks to [@lazareviczoran](https://github.com/lazareviczoran), [@bombsimon](https://github.com/bombsimon), and [@jbridger](https://github.com/jbridger) for reporting and fixing [Issue #114](https://github.com/hrcorval/behavex/issues/114).

---

## [3.3.0]

### Added
- Support for attaching screenshots to the HTML report via the `behavex-images` library.
- Progress bar improvement: trailing content is now removed from the console when the progress bar is printed.

### Contributors
- Thanks to [@abmercado19](https://github.com/abmercado19) for providing the [`behavex-images`](https://github.com/abmercado19/behavex-images) library implementation.

---

## [3.2.13]

### Added
- Progress bar in the console during parallel execution (`-spb` / `--show-progress-bar`).
- GitHub Actions workflow to validate BehaveX in the latest Python versions (3.8–3.11).
- Pre-commit hooks enabled on every commit.

### Fixed
- Blank report issue occurring in some parallel runs.
- Dry run failures when no features/scenarios were tagged as `@MANUAL`.

### Changed
- Removed some parameters that are no longer used.

---

## [3.2.0]

### Added
- Improved rendering of feature background steps in the HTML report.
- Scenarios that crash during execution are now reported as "Untested" in the HTML report.
- Feature tags are added to scenarios in the HTML report.

### Fixed
- Console summary now correctly reports the number of executed scenarios.
- Not all features were considered for execution when running in parallel by feature.
- JUnit reports now include all executed scenarios.

### Contributors
- Thanks to [@AxelFurlanF](https://github.com/AxelFurlanF) for fixing a deprecation warning with the latest Behave 1.2.6 ([PR #116](https://github.com/hrcorval/behavex/pull/116)).

---

## [3.0.0]

### Added
- Support for executing features located in multiple paths (`behavex path1 path2 ... pathN`).
- HTML output report path printed in the console at the end of execution.
- Feature paths printed in the console when BehaveX starts ([Issue #88](https://github.com/hrcorval/behavex/issues/88)).
- Execution summary printed when running tests in parallel.
- Full support for re-executing all failing scenarios in parallel.
- Scenario outlines can now be executed in parallel (outline examples run in parallel).
- HTML report layout improvements for long Gherkin steps and long failure messages ([Issue #81](https://github.com/hrcorval/behavex/issues/81)).
- Error exit code when parallel execution cannot be launched due to duplicated scenario names ([Issue #86](https://github.com/hrcorval/behavex/issues/86)).

### Fixed
- Exception logging in `environment.py` module.
- Tags associated with scenario outline examples are now correctly processed ([Issue #85](https://github.com/hrcorval/behavex/issues/85)).
- Scenarios written in non-English languages are now correctly detected ([Issue #77](https://github.com/hrcorval/behavex/issues/77)).
- `step.text` now renders correctly in HTML reports ([Issue #79](https://github.com/hrcorval/behavex/issues/79)).
- Empty feature files are now parsed without errors.

### Contributors
- Thanks to [@sebns](https://github.com/sebns) for fixing the issue with tags on scenario outline examples.

---

## [2.0.1]

### Added
- Support for executing features from a path specified as argument (`behavex <features_path>`).
- Number of features displayed in the "Feature" column of the HTML report.
- Number of unique steps and total step executions shown in the "Steps" chart.

### Fixed
- Parsing of scenario outlines containing names in examples.
- Added missing webhooks for tags (`before_tag` and `after_tag`).

---

## [1.6.0]

### Added
- Reusing `FEATURES_PATH` environment variable to indicate where features are located.

### Fixed
- Execution order of events in `environment.py`: `before_*` BehaveX events now have precedence over the same events in the testing solution, and `after_*` BehaveX events follow after the testing solution's events.
- Scenarios dynamically skipped or removed from the execution list are now handled correctly.
- Scenario outlines with examples containing white spaces in descriptions are now correctly published in execution reports.

---

## [1.5.12]

### Added
- Average reusability of test steps reported in metrics.
- Both scenario description and feature description are now considered when creating the evidence path, avoiding issues with duplicate scenario names.
- HTML report improvement: line breaks are correctly handled in reported error messages in failing steps.

### Fixed
- Fixed issue when executing scenarios using the `--include` argument.

---

## [1.5.11]

### Added
- BehaveX can now be executed using the `__main__` entry point: `python -m behavex -t @TAG ...`.

---

## [1.5.10]

### Changed
- `--rerun-failures` (`-rf`) argument now requires the `failing_scenarios.txt` path as its value.

### Fixed
- Re-executing failing scenarios with blank spaces in path or filename now works correctly.

---

## [1.5.9]

### Fixed
- Additional encoding fix for the HTML report to avoid breaking it on failing scenarios.

### Contributors
- Thanks to [@salunkhe-ravi](https://github.com/salunkhe-ravi) for sharing the [behavex-boilerplate-framework](https://github.com/salunkhe-ravi/behavex-boilerplate-framework) sample project.

---

## [1.5.8]

### Fixed
- Additional encoding fix to restore stable operation.

---

## [1.5.7]

### Fixed
- Reverted scenario name normalization to restore backward compatibility.
- Additional encoding issues reported by users.

---

## [1.5.6]

### Fixed
- Side effect with `--rerun-failures` (`-rf`) argument that was not considered in local tests.

---

## [1.5.5]

### Added
- `--rerun-failures` (`-rf`) now stores the failures file in the root folder instead of the output folder, preventing it from being deleted after a re-execution.

### Changed
- Documentation updated with instructions for re-executing failing scenarios.

---

## [1.5.4]

### Fixed
- Scenario outlines with quotes in the description are now parsed correctly.
- Encoding issues with step descriptions in the HTML report.

### Changed
- Enabled wrapper to run with the latest Python versions.

---

## [1.5.3]

### Added
- Support for examples arguments in scenario outline descriptions.

### Changed
- HTML report screenshots added to documentation.

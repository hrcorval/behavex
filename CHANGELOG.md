# Changelog

All notable changes to BehaveX are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [4.7.0] - Unreleased

### Added
- **`BehaveXRunner` BehaveX API** — BehaveX can now be invoked programmatically from Python without the CLI. `BehaveXRunner` accepts the main CLI parameters (paths, tags, parallel, filtering, reporting, ordering and formatter options) as typed keyword arguments and returns a structured `RunResult`; an invalid argument or a missing path raises `ValueError` instead of exiting the process. Designed for AI agents, test orchestrators, and any automation that drives BehaveX programmatically.
- **Pydantic result models** (`behavex[api]` optional extra) — `RunResult`, `FeatureResult`, `ScenarioResult`, `StepResult`, `BackgroundResult`, and `RunSummary` provide a typed, structured view of test results. Includes convenience properties: `result.passed`, `result.summary`, `result.failed_scenarios` (computed fields, so `model_dump()` includes them), `scenario.failed`, `feature.failed_scenarios`, and more.
- **`[api]` optional extra** — Pydantic is an optional dependency, not added to the base install. Existing `pip install behavex` users are fully unaffected. Install with `pip install 'behavex[api]'` to activate the BehaveX API.
- **`run_id` in `RunResult`** — Every `BehaveXRunner.run()` call now returns a unique UUID4 `run_id`, enabling agents and orchestrators to correlate runs with logs, traces, or external systems without ambiguity.
- **`on_progress` callback on `BehaveXRunner`** — Optional callable invoked once for every scenario in the run's results, in both parallel and non-parallel modes. Events arrive as each scenario finishes in single-process runs and with `parallel_scheme="scenario"`, and together per feature with `parallel_scheme="feature"`. Receives a `ProgressEvent` with `scenario_name`, `feature_name`, `status`, `duration`, a monotonically increasing `completed_count`, and, for parallel runs with `parallel_scheme="scenario"`, the `total` number of events. Exceptions raised inside the callback are silently swallowed and never affect the exit code or the run.
- **`BehaveXRunner.stop()`** — Stops a parallel run from starting more scenarios (or features), including the remaining `@SERIAL` ones, and cancels the queued ones (on Python 3.8 queued ones still run); running ones finish and `run()` returns the results gathered so far. When this skipped any work, `RunResult.stopped` is set, so `RunResult.passed` is `False`. Safe to call from another thread or from `on_progress`, and honoured even when it comes before the run has submitted any work. Has no effect in single-process mode or outside an active run.
- **`BehaveXRunner.discover()`** — Lists the scenarios a `run()` with the same arguments would report, as `DiscoveredScenario` models (`feature`, `name`, `filename`, `line`, `tags`, `undefined_steps`), without executing anything, running hooks, touching the output folder or printing to stdout. With `check_steps=True` it also lists each scenario's `undefined_steps`, matching the steps as behave's `--dry-run` does, with the steps folder `run()` would use; the step definitions load in a separate process, so the caller is left untouched. A missing path or `rerun_failures` file raises `ValueError` naming it.
- **`BehaveXRunner.load_results(output_folder)`** — Rebuilds the `RunResult` of a finished run, `run_id` included, from the files it wrote to its output folder, so another process can read a run's results without running anything. Works for CLI runs too.
- **`overall_status.json` records the run's `exit_code`, `stopped` and `run_id`** — Next to `status`, so CI pipelines can read the exit code from the file. Every run, from the CLI or the API, gets a `run_id`.
- **Each `BehaveXRunner.run()` runs behave in a worker process** — Also with `parallel_processes=1`, so the step definitions one run loads never reach a later run of another suite in the same process. The console output of a single-process run reaches the caller through its `sys.stdout`, so it can be redirected, and `on_progress` events still arrive as each scenario finishes. The CLI is unchanged.
- **`ProgressEvent` Pydantic model** — Structured payload delivered to `on_progress` callbacks. Available via `from behavex import ProgressEvent`.

### Fixed
- **A run with no feature paths and no `features` folder passed** — BehaveX exited with code 0 after running nothing when no paths were given and the default `features` folder did not exist, so CI saw a green run. It now prints `Specified path was not found: features` and exits with code 1, as it already did for a path given on the command line.
- **`--no-report` parallel runs printed a JUnit file error** — A `--no-report` run with `--parallel-processes` above 1 no longer tries to write the JUnit XML file, so it no longer prints a `FileNotFoundError` traceback and an "Another program is using the files" prompt.
- **An `@AUTORETRY` scenario retried after an error was not marked as retried** — With behave 1.3.x, a scenario retried because a step raised a non-assertion exception or a hook failed is now marked as retried in the HTML and JSON reports. A scenario is marked only when it actually ran again.

---

## [4.6.8] - 2026-10-21

### Fixed
- **JUnit XML report was not well-formed when report text contained `]]>`** ([#251](https://github.com/hrcorval/behavex/pull/251)) — A step, scenario name, file path, traceback or hook error message containing `]]>` ended the CDATA section early, so CI tools could not read the `TESTS-*.xml` file for that feature. The text is now kept intact in both single-process and parallel runs.
- **An output folder holding the project was deleted** — BehaveX empties the output folder before each run, so `-o .` deleted the whole project (features, steps and `.git`) and `-o features` deleted the feature files. BehaveX now refuses an output folder that is, or contains, the current directory or a features path, and exits with an error before deleting anything.
- **A failing cleanup left the run passed** — A cleanup registered with `context.add_cleanup()` that raised an exception was printed as `CLEANUP-ERROR`, but BehaveX exited with code 0. A failing root, feature or rule cleanup now fails the run, as it does with behave; a failing scenario cleanup fails the run unless the scenario is muted. Setting `context.fail_on_cleanup_errors = False` keeps the run passing, as with behave.
- **Features with the same file name in different folders mixed their JUnit XML reports** — With `--parallel-scheme scenario`, features such as `features/api/login.feature` and `features/web/login.feature` shared one temporary file while their results were gathered, so a JUnit file could hold the other feature's scenarios and lose its own. Each feature now gathers its results separately.
- **`--rerun-failures` with a missing or empty file ran every test** — When the `failing_scenarios.txt` file did not exist or was empty, BehaveX printed a warning, then ran the whole suite and exited with code 0 if it passed, so a CI rerun step reported green without rerunning any failure. BehaveX now exits with code 1 without running any test. Since the file is written only when a scenario fails, a rerun step that runs after a passing run now fails too; run it only when the first run fails (`behavex || behavex -rf output/failing_scenarios.txt`).

### Contributors
- Thanks to [@taltal-beep](https://github.com/taltal-beep) for the fix and its regression tests ([PR #251](https://github.com/hrcorval/behavex/pull/251)).

---

## [4.6.7] - 2026-10-17

### Fixed
- **HTML report showed an undefined Background step's error one letter per line** — The `step undefined` message of a scenario whose Background step has no definition is now shown on one line, and `report.json` stores it as a list like every other `error_msg`.

---

## [4.6.6] - 2026-10-15

### Added
- **Python 3.14 support** — Python 3.14 is now declared in the package classifiers and tested in CI across all supported behave versions (1.2.6, 1.3.0, 1.3.1, 1.3.3 and latest) on Linux, Windows and macOS.

### Fixed
- **A `before_scenario` hook failure marked every scenario in the feature as failed under `--parallel-scheme feature`** ([#249](https://github.com/hrcorval/behavex/pull/249)) — When a hook failure is already reflected in behave's per-scenario results, BehaveX now keeps those results instead of replacing them with the "execution crashed" skeleton, so sibling scenarios keep their real status. Parallel runs now report every hook failure with the same feature and scenario statuses as single-process runs: a `before_all` or `before_feature` failure leaves the scenarios untested, and an `after_feature` or `after_all` failure keeps them passed, while the exit code and `overall_status.json` report the failure. Previously these failures marked the scenarios as failed in parallel only. The skeleton is now used only when behave produced no results. The failing hook's `HOOK-ERROR` message is now shown as the scenario's error.
- **Hook failures reported as skipped or with an invalid status** ([#249](https://github.com/hrcorval/behavex/pull/249)) — Behave's `hook_error`/`cleanup_error` statuses (behave 1.2.7+) are now reported as `error` in the console summary, JSON, HTML, JUnit and Allure outputs. Previously the HTML report counted them as skipped, JUnit emitted no failure element, and Allure received an invalid status. Scenarios and steps left `untested` by a hook failure are now reported to Allure as `skipped`, since `untested` is not an Allure status.
- **`overall_status.json` reported a crashed run as passed or skipped** ([#250](https://github.com/hrcorval/behavex/pull/250)) — A hook crash (`before_all`, `before_feature`, `after_all`) could leave `overall_status.json` as `"passed"` or `"skipped"` and `report.json` empty, so CI pipelines gating on it saw a green run. The overall status now treats `error` features as failed and is always `"failed"` when BehaveX exits with code 1; single-process runs keep behave's results instead of an empty report, and the HTML feature badge, summary table and timeline count errors as failures.
- **`before_all_workers` / `after_all_workers` skipped when running a feature file in a subfolder** — BehaveX looked for `environment.py` only next to the given path, so `behavex features/sub/x.feature` (alone or with `--name`, tags or a `:line`) silently skipped both hooks and workers never received the shared context. BehaveX now asks behave for the base directory, so the worker hooks load the same `environment.py` as the workers, including a staged one selected with `BEHAVE_STAGE`.
- **Worker hook failures and dry runs** — The worker hooks no longer run on `--dry-run`, matching behave's hooks. A failing `before_all_workers` or `after_all_workers` is now reported as `HOOK-ERROR in <hook>: ...` instead of `Unexpected error`, `after_all_workers` still runs after a failed `before_all_workers` (as behave runs `after_all`), and `overall_status.json` is `"failed"` in both cases; previously a failing `after_all_workers` left it as `"passed"` and skipped the parallel summary.
- **`--name` only matched the start of the scenario name, and only once** — `--name` now matches any part of the name, as behave does and as the help text says, and can be repeated to run the scenarios matching any of the given names. A `name` set in the config file is now applied in single-process runs too, where it used to run every scenario of the matching features. A run where no scenario matches the name now prints the summary with a single process too, and `name` no longer triggers the "not compatible with parallel execution" warning, since workers now select the same scenarios as the dispatcher.
- **Invalid JUnit XML for scenarios that crashed outside a step** — The `<failure>` element's `type` attribute was unquoted in serial and `--parallel-scheme feature` runs, producing XML that JUnit parsers reject (for example, a `before_scenario` hook failure on behave 1.2.6). In those runs the `<failure>` element was also empty; it now carries the hook's error message.
- **Documented `--stage` option that did not exist** — `docs/cli-reference.md` listed a `--stage` flag that BehaveX rejects; it now points to the `BEHAVE_STAGE` environment variable instead.

### Contributors
- Thanks to [@taltal-beep](https://github.com/taltal-beep) for both hook-failure fixes and their regression tests ([PR #249](https://github.com/hrcorval/behavex/pull/249), [PR #250](https://github.com/hrcorval/behavex/pull/250)).

---

## [4.6.5] - 2026-05-22

### Fixed
- **`behave.ini` with multi-line values crashes BehaveX** ([#247](https://github.com/hrcorval/behavex/issues/247)) — BehaveX auto-discovery now skips `behave.ini` when the file contains no BehaveX-specific sections (`[params]`, `[output]`, `[test_run]`, `[progress_bar]`). ConfigObj (used internally) cannot parse Python `configparser`-style multi-line continuation values such as `format = plain\n    progress`, causing a hard crash on startup. A `behave.ini` with only a `[behave]` section is Behave's own configuration and is now left exclusively for Behave to handle.
- **Local packages not importable from `environment.py` and worker processes** ([#247](https://github.com/hrcorval/behavex/issues/247)) — The project root (current working directory) is now added to `sys.path` at two critical points: (1) before `_call_bhx_hook()` loads `environment.py` in the coordinator process, so top-level imports in `environment.py` resolve before Behave's `PathManager` is active; (2) in `init_multiprocessing()` for each spawned worker process, since macOS and Windows use the `spawn` start method which does not inherit the parent's `sys.path`.

### Contributors
- Thanks to [@qriwty](https://github.com/qriwty) for reporting both regressions in detail with a clear reproduction case ([Issue #247](https://github.com/hrcorval/behavex/issues/247)).

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

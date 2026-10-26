# BehaveX API

BehaveX can be driven programmatically via `BehaveXRunner`, without using the CLI. This is the recommended interface for AI agents, test orchestrators, CI scripts, and any automation that needs structured output.

## Installation

The Python API requires Pydantic, which is an optional dependency:

```bash
pip install 'behavex[api]'
```

The base `pip install behavex` is unaffected — Pydantic is never installed unless you explicitly request `[api]`.

## Quick Start

```python
from behavex import BehaveXRunner

result = BehaveXRunner(
    paths=["tests/features"],
    tags=["@smoke"],
    parallel_processes=4,
    output_folder="output",
).run()

if result.passed:
    print(f"All tests passed ({result.summary.passed} scenarios)")
else:
    for scenario in result.failed_scenarios:
        print(f"FAILED: {scenario.name}")
        print(f"  Error: {scenario.error_msg}")
```

## `BehaveXRunner`

### Constructor Parameters

All parameters are optional. Defaults match the BehaveX CLI defaults.

| Parameter | Type | Description |
|---|---|---|
| `paths` | `list[str]` | Feature file or directory paths to run |
| `tags` | `list[str]` | Tag filters — each entry maps to one `--tags` argument |
| `output_folder` | `str` | Output directory for HTML/JSON/XML reports. It is emptied before each run, so it cannot contain the project or its features. |
| `parallel_processes` | `int` | Number of parallel Behave worker processes |
| `parallel_scheme` | `str` | `'scenario'` or `'feature'` |
| `parallel_delay` | `int` | Delay in milliseconds between parallel process launches |
| `include_paths` | `list[str]` | Additional feature paths to include |
| `dry_run` | `bool` | List scenarios in reports without executing steps |
| `stop_on_failure` | `bool` | Stop execution after the first failure (CLI `--stop`) |
| `show_progress_bar` | `bool` | Display a progress bar during parallel execution |
| `no_report` | `bool` | Skip the reports and the output folder; scenario logs and other temporary assets are still written to a temporary folder, whose path BehaveX prints at the end |
| `config` | `str` | Path to a BehaveX config file |
| `rerun_failures` | `str` | Path to `failing_scenarios.txt` to rerun only failed scenarios |
| `formatter` | `str` | Custom formatter class path (e.g., Allure formatter) |
| `formatter_outdir` | `str` | Output directory for formatter results |
| `formatter_attach_logs` | `bool` | Set to `False` to disable log attachment in formatter reports |
| `order_tests` | `bool` | Sort scenarios by `@ORDER_NNN` tags |
| `order_tests_strict` | `bool` | Strict ordering — scenarios wait for lower-order tests to finish |
| `order_tag_prefix` | `str` | Prefix for order tags (default: `ORDER`) |
| `logging_level` | `str` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `no_snippets` | `bool` | Suppress undefined step snippet output |
| `name` | `str` | Regex pattern to filter scenarios by name |
| `include` | `str` | Regex pattern to include feature files by path |
| `exclude` | `str` | Regex pattern to exclude feature files by path |
| `define` | `list[str]` | User-defined variables as `key=value` strings, accessible via `context.config.userdata` |
| `on_progress` | `Optional[Callable[[ProgressEvent], None]]` | Optional callback invoked once for every scenario in `RunResult.features`, in both parallel and non-parallel modes; see [Stream progress with on_progress](#stream-progress-with-on_progress) for when events arrive. Exceptions inside the callback are silently swallowed and never affect the exit code. |

### `.run()` → `RunResult`

Executes the test run synchronously and returns a `RunResult`. Each call generates a new `run_id`.

An invalid argument, such as an unknown `parallel_scheme` or `logging_level`, raises `ValueError` with the argument parser's message instead of exiting the process. A path that does not exist, or a glob that matches no file, raises `ValueError` whose message names it. A run BehaveX refuses to start for another reason (such as duplicated scenarios) also raises `ValueError`; BehaveX prints the reason first. An `output_folder` that is, or contains, the current directory or one of the `paths` raises `ValueError` before anything is deleted. Values that start with `-`, such as a tag or one of the `paths`, are passed as values, not read as options.

Run one `BehaveXRunner` at a time per process: the run state is module-level, so a `.run()` called while another one is active in the same process (from another thread or from `on_progress`) raises `RuntimeError`.

```python
runner = BehaveXRunner(paths=["tests/features"], no_report=True)

result1 = runner.run()  # run_id: "a1b2c3d4-..."
result2 = runner.run()  # run_id: "e5f6g7h8-..." (always unique)
```

### `.discover(check_steps=False)` → `list[DiscoveredScenario]`

Lists the scenarios a `.run()` with the same constructor arguments would report, applying the same paths, `include_paths`, tags (including the config's `tags_to_skip`), `name`, `include`, `exclude` and `rerun_failures` filters. Scenario Outline examples are listed one by one, as a run reports them. `@MANUAL` and `@WIP` scenarios are listed too: a run reports them as manual without executing them. A parallel run with `parallel_scheme="scenario"` also reports the scenarios that `exclude` skips, as untested; `.discover()` leaves them out.

Nothing is executed and nothing is written: no hooks run, the output folder is neither created nor cleaned, and nothing is printed to `sys.stdout`, so it is safe to call from a process whose stdout carries a protocol (such as an MCP stdio server). Step definitions are not loaded unless `check_steps=True`.

With `check_steps=True`, each `DiscoveredScenario` lists in `undefined_steps` the steps no step definition matches, as behave's `--dry-run` would mark them. It loads `environment.py` (without running its hooks) and the step modules, as behave does, so a `use_step_matcher()` or a custom type registered there applies. It loads them in a new spawned process, one per steps folder, so the calling process is left as it was and the step definitions it already loaded, from an earlier `.run()` for example, are not taken into account; because the process is spawned on every platform, a script that calls it needs an `if __name__ == "__main__":` guard. It uses the steps folder the matching `.run()` would: a single-process run (including a dry run) takes it from the first feature for every feature, while a parallel run takes it from each feature's own folder, so with nested steps folders the two can differ. Steps that a step or hook adds at run time, such as with `context.execute_steps()`, are not checked, as in behave's dry run. A step module that fails to import, or a feature with no steps folder above it, raises `ValueError` naming the error.

An invalid argument, a path that does not exist (including the default `features` folder when no `paths` are given), a glob that matches no file, or a missing or empty `rerun_failures` file raises `ValueError` naming the reason. For a missing or empty `rerun_failures` file, `.run()` instead returns a `RunResult` with `exit_code` 1 and no scenarios. Calling it while a `.run()` is active in the same process raises `RuntimeError`, and a `.run()` started during it does too.

```python
scenarios = BehaveXRunner(paths=["tests/features"], tags=["@smoke"]).discover()
for scenario in scenarios:
    print(f"{scenario.filename}:{scenario.line} {scenario.name}")

# Find the steps without a definition before running anything
for scenario in BehaveXRunner(paths=["tests/features"]).discover(check_steps=True):
    for step in scenario.undefined_steps:
        print(f"{scenario.filename}:{scenario.line} undefined: {step}")
```

### `.stop()`

Stops a parallel run from starting more scenarios (or features), including the remaining `@SERIAL` ones, and cancels the queued ones. Scenarios already running finish, and `.run()` returns the results gathered so far. When this skipped any work, `stopped` is `True`, so `passed` is `False` even though `exit_code` only reflects the scenarios that ran; a `.stop()` that came after every scenario had already started leaves `stopped` `False`. Call it from another thread or from the `on_progress` callback, since `.run()` blocks the calling thread. A `.stop()` that comes while the run is still setting up (for example during `before_all_workers`) takes effect before any scenario is submitted.

Has no effect in single-process mode or when called outside an active run. On Python 3.8, work already queued still runs; only the scenarios not yet submitted are skipped.

```python
import threading
from behavex import BehaveXRunner

runner = BehaveXRunner(
    paths=["tests/features"],
    parallel_processes=4,
    parallel_scheme="scenario",
)

# Cancel the scenarios not started yet after 30 seconds
timer = threading.Timer(30, runner.stop)
timer.start()
result = runner.run()
timer.cancel()

if result.stopped:
    print(f"Timed out after {result.summary.total} scenarios")
```

### `BehaveXRunner.load_results(output_folder)` → `RunResult`

Rebuilds the `RunResult` of a run that has finished, from the `report.json` and `overall_status.json` it wrote to `output_folder`, so another process (or a later session) can read it without running anything. It returns the same `RunResult`, `run_id` included, as the `.run()` that wrote the folder, and works for runs started from the CLI too. It is a static method: call it on the class, with the folder path.

A folder without `overall_status.json` raises `ValueError`; that includes a folder that does not exist and the output folder of a `no_report` run, which writes neither file. So does an `overall_status.json` written by BehaveX 4.6 or earlier, which does not record the exit code. A folder whose run exited 0 but has no `report.json` raises too, and so does a `report.json` without `features`. A run that fails before writing its report (a failing `before_all_workers` hook or an interrupt) exits 1 and leaves no `report.json`; `load_results()` returns it with no features, as `.run()` did. A run that stops before cleaning its output folder (a missing or empty `rerun_failures` file) leaves the previous run's files there, so `load_results()` returns that previous run.

```python
from behavex import BehaveXRunner

result = BehaveXRunner.load_results("output")
print(result.run_id, result.exit_code, result.summary)
```

## Result Models

All models are Pydantic `BaseModel` instances with `extra='ignore'` — unknown keys in the result dicts are silently dropped for forward compatibility.

### `ProgressEvent`

Delivered to the `on_progress` callback once for every scenario in `RunResult.features`, after it completes.

| Field | Type | Description |
|---|---|---|
| `scenario_name` | `str` | Name of the completed scenario |
| `feature_name` | `str` | Name of the feature that owns the scenario |
| `status` | `str` | The scenario's status string (`'passed'`, `'failed'`, `'skipped'`, `'untested'`); hook errors are reported as `'error'` |
| `duration` | `float` | Scenario execution time in seconds |
| `completed_count` | `int` | How many scenarios have completed so far in this run (monotonically increasing) |
| `total` | `Optional[int]` | How many events the run will deliver, set with `parallel_processes > 1` and `parallel_scheme="scenario"`, else `None`; a run that `.stop()` cuts short delivers fewer |

### `RunResult`

Top-level result returned by `BehaveXRunner.run()` and `BehaveXRunner.load_results()`.

| Field / Property | Type | Description |
|---|---|---|
| `run_id` | `str` | Unique UUID4 identifying this specific run |
| `exit_code` | `int` | Process exit code (`0` = all passed) |
| `output_folder` | `str` | Absolute path of the output folder the run used: `output_folder`, else the config file's `[output] path`, else `output` |
| `features` | `list[FeatureResult]` | Feature results of the run (populated with `no_report=True` too) |
| `stopped` | `bool` | `True` when `.stop()` cut the run short |
| `.passed` | `bool` | `True` when `exit_code == 0` and the run was not stopped |
| `.summary` | `RunSummary` | Aggregated scenario counts |
| `.failed_scenarios` | `list[ScenarioResult]` | Scenarios with status `failed` or `error` across all features, including muted ones |

`.passed`, `.summary` and `.failed_scenarios` are computed fields, so `model_dump()`, `model_dump_json()` and the serialization JSON schema include them.

### `RunSummary`

Returned by `RunResult.summary`. The counts don't overlap and add up to `total`: a `@MANUAL` or `@WIP` scenario counts only as `manual`.

| Field | Type | Description |
|---|---|---|
| `total` | `int` | Total number of scenarios |
| `passed` | `int` | Number of passed scenarios |
| `failed` | `int` | Number of failed scenarios |
| `error` | `int` | Number of scenarios with status `error` (e.g. a hook error) |
| `skipped` | `int` | Number of skipped scenarios |
| `untested` | `int` | Number of untested scenarios |
| `manual` | `int` | Number of `@MANUAL` or `@WIP` scenarios |

### `FeatureResult`

| Field / Property | Type | Description |
|---|---|---|
| `name` | `str` | Feature name |
| `status` | `str` | `'passed'`, `'failed'`, or `'skipped'` |
| `duration` | `float` | Total execution time in seconds |
| `filename` | `str` | Relative path to the feature file |
| `scenarios` | `list[ScenarioResult]` | All scenarios in this feature |
| `.passed` | `bool` | `True` when `status == 'passed'` |
| `.failed` | `bool` | `True` when `status == 'failed'` |
| `.failed_scenarios` | `list[ScenarioResult]` | Scenarios with status `failed` or `error` in this feature, including muted ones |

### `ScenarioResult`

| Field / Property | Type | Description |
|---|---|---|
| `name` | `str` | Scenario name |
| `status` | `str` | `'passed'`, `'failed'`, `'error'`, `'skipped'`, or `'untested'` |
| `duration` | `float` | Execution time in seconds |
| `line` | `int` | Line number in the feature file |
| `tags` | `list[str]` | Scenario tags |
| `filename` | `str` | Feature file path |
| `feature` | `str` | Feature name |
| `steps` | `list[StepResult]` | All steps |
| `background` | `BackgroundResult` | Background steps |
| `error_msg` | `list[str]` | Error messages for failed steps |
| `error_lines` | `list[str]` | Error traceback lines |
| `error_step` | `StepResult \| None` | The step that caused the failure |
| `worker_id` | `str` | ID of the parallel worker that ran this scenario |
| `.is_manual` | `bool` | `True` when the scenario is tagged `@MANUAL` or `@WIP` |
| `.passed` | `bool` | `True` when `status == 'passed'` and not `is_manual` |
| `.failed` | `bool` | `True` when `status == 'failed'` and not `is_manual` |
| `.errored` | `bool` | `True` when `status == 'error'` and not `is_manual` |
| `.skipped` | `bool` | `True` when `status == 'skipped'` and not `is_manual` |
| `.untested` | `bool` | `True` when `status == 'untested'` and not `is_manual` |
| `.manual` | `bool` | Same as `is_manual` |

### `DiscoveredScenario`

Returned by `BehaveXRunner.discover()`. Its fields other than `undefined_steps` hold the same values as the `ScenarioResult` a run reports for that scenario.

| Field | Type | Description |
|---|---|---|
| `feature` | `str` | Feature name |
| `name` | `str` | Scenario name |
| `filename` | `str` | Feature file path |
| `line` | `int` | Line number in the feature file |
| `tags` | `list[str]` | Scenario tags, including the feature's and the Examples' |
| `undefined_steps` | `list[str]` | With `check_steps=True`, the scenario's steps (Background included) that no step definition matches, as `"<keyword> <text>"`, e.g. `"When I log in"`; empty otherwise |

### `StepResult`

| Field | Type | Description |
|---|---|---|
| `step_type` | `str` | `'given'`, `'when'`, `'then'`, `'and'`, `'but'` |
| `name` | `str` | Step text |
| `status` | `str` | `'passed'`, `'failed'`, `'skipped'`, `'undefined'` |
| `duration` | `float` | Execution time in seconds |
| `line` | `int` | Line number in the feature file |
| `text` | `str \| None` | Docstring attached to the step |
| `error_msg` | `str \| None` | Error message if the step failed |
| `error_lines` | `list[str]` | Traceback lines |

### `BackgroundResult`

| Field | Type | Description |
|---|---|---|
| `duration` | `float` | Total background execution time |
| `steps` | `list[StepResult]` | Background step results |

## Usage Examples

### Filter by tag and inspect failures

```python
from behavex import BehaveXRunner

result = BehaveXRunner(
    paths=["tests/features"],
    tags=["@regression"],
    output_folder="output/regression",
).run()

print(f"Total: {result.summary.total}")
print(f"Passed: {result.summary.passed}")
print(f"Failed: {result.summary.failed}")

for scenario in result.failed_scenarios:
    print(f"\nFAILED: [{scenario.feature}] {scenario.name}")
    if scenario.error_step:
        print(f"  Step: {scenario.error_step.step_type} {scenario.error_step.name}")
    for line in scenario.error_lines:
        print(f"  {line}")
```

### Parallel execution

```python
result = BehaveXRunner(
    paths=["tests/features"],
    parallel_processes=8,
    parallel_scheme="scenario",
    output_folder="output",
).run()
```

### No output (agent / CI use case)

```python
result = BehaveXRunner(
    paths=["tests/features"],
    tags=["@smoke"],
    no_report=True,
).run()

assert result.passed, f"Smoke tests failed (exit code {result.exit_code})"
```

### Correlate runs with external traces

```python
import logging

runner = BehaveXRunner(paths=["tests/features"], output_folder="output")

result = runner.run()
logging.info("Test run %s completed: exit_code=%d", result.run_id, result.exit_code)
# Pass result.run_id to LangSmith, Datadog, or any observability tool
```

### Rerun only failed scenarios

```python
# First run
result = BehaveXRunner(
    paths=["tests/features"],
    output_folder="output",
).run()

# Rerun failures (BehaveX writes failing_scenarios.txt automatically)
if not result.passed:
    rerun = BehaveXRunner(
        rerun_failures="output/failing_scenarios.txt",
        output_folder="output/rerun",
    ).run()
```

### Stream progress with on_progress

```python
from behavex import BehaveXRunner, ProgressEvent

def handle_progress(event: ProgressEvent) -> None:
    print(f"[{event.completed_count}] {event.status}: {event.feature_name} / {event.scenario_name}")

result = BehaveXRunner(
    paths=["tests/features"],
    parallel_processes=4,
    parallel_scheme="scenario",
    on_progress=handle_progress,
).run()
```

The callback fires once for every scenario in `RunResult.features`, in both parallel and non-parallel modes, so the number of events equals `result.summary.total`. Events are always per scenario, but when they arrive depends on the mode:

- **Single process** and **`parallel_scheme="scenario"`**: each event arrives as its scenario finishes. Use one of these for timely progress.
- **`parallel_scheme="feature"`**: the events of a feature arrive together, after the whole feature finishes in its worker.
- Scenarios behave never ran (after the failure of a single-process `stop_on_failure=True` run, or in a `dry_run=True` run) arrive with status `'untested'` just before `.run()` returns.

Any exception raised inside the callback is silently ignored — it never affects the run or its exit code.

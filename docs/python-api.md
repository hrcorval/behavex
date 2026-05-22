# Python API

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
| `output_folder` | `str` | Output directory for HTML/JSON/XML reports |
| `parallel_processes` | `int` | Number of parallel Behave worker processes |
| `parallel_scheme` | `str` | `'scenario'` or `'feature'` |
| `parallel_delay` | `int` | Delay in seconds between parallel process launches |
| `include_paths` | `list[str]` | Additional feature paths to include |
| `dry_run` | `bool` | List scenarios in reports without executing steps |
| `stop` | `bool` | Stop execution after the first failure |
| `show_progress_bar` | `bool` | Display a progress bar during parallel execution |
| `no_report` | `bool` | Disable all file output — no reports, no output folder |
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

### `.run()` → `RunResult`

Executes the test run synchronously and returns a `RunResult`. Each call generates a new `run_id`.

```python
runner = BehaveXRunner(paths=["tests/features"], no_report=True)

result1 = runner.run()  # run_id: "a1b2c3d4-..."
result2 = runner.run()  # run_id: "e5f6g7h8-..." (always unique)
```

## Result Models

All models are Pydantic `BaseModel` instances with `extra='ignore'` — unknown fields from `report.json` are silently dropped for forward compatibility.

### `RunResult`

Top-level result returned by `BehaveXRunner.run()`.

| Field / Property | Type | Description |
|---|---|---|
| `run_id` | `str` | Unique UUID4 identifying this specific run |
| `exit_code` | `int` | Process exit code (`0` = all passed) |
| `output_folder` | `str` | The configured output folder path |
| `features` | `list[FeatureResult]` | Parsed feature results (empty when `no_report=True` or no `output_folder`) |
| `.passed` | `bool` | `True` when `exit_code == 0` |
| `.summary` | `RunSummary` | Aggregated scenario counts |
| `.failed_scenarios` | `list[ScenarioResult]` | All failed scenarios across all features |

### `RunSummary`

Returned by `RunResult.summary`.

| Field | Type | Description |
|---|---|---|
| `total` | `int` | Total number of scenarios |
| `passed` | `int` | Number of passed scenarios |
| `failed` | `int` | Number of failed scenarios |
| `skipped` | `int` | Number of skipped scenarios |

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
| `.failed_scenarios` | `list[ScenarioResult]` | Failed scenarios in this feature |

### `ScenarioResult`

| Field / Property | Type | Description |
|---|---|---|
| `name` | `str` | Scenario name |
| `status` | `str` | `'passed'`, `'failed'`, or `'skipped'` |
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
| `.passed` | `bool` | `True` when `status == 'passed'` |
| `.failed` | `bool` | `True` when `status == 'failed'` |
| `.skipped` | `bool` | `True` when `status == 'skipped'` |

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

# result.features is empty when no_report=True
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

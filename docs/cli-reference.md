# CLI Reference

## Supported Behave Arguments

The following Behave arguments are supported by BehaveX:

- no_color
- color
- define
- exclude
- include
- no_snippets
- no_capture
- name
- capture
- no_capture_stderr
- capture_stderr
- no_logcapture
- logcapture
- logging_level
- summary
- quiet
- stop
- tags
- tags-help

> **Note:** Some arguments do not apply when running more than one parallel process, such as `stop` and `color`.

## BehaveX-Specific Arguments

| Argument | Description |
|---|---|
| `-o` / `--output-folder` | Output folder for execution reports (JUnit, HTML, JSON) |
| `-d` / `--dry-run` | Perform a dry run — lists scenarios in reports without executing them |
| `--parallel-processes` | Number of parallel Behave processes |
| `--parallel-scheme` | Parallel execution scheme: `scenario` or `feature` |
| `--show-progress-bar` | Display a progress bar in the console during parallel execution |
| `--formatter` | Custom formatter (e.g., Allure formatter class path) |
| `--formatter-outdir` | Output directory for formatter results (default: `output/allure-results`) |
| `--no-formatter-attach-logs` | Disable automatic attachment of scenario log files to formatter reports |
| `--order-tests` | Enable scenario/feature sorting by order tags (parallel execution only) |
| `--order-tests-strict` | Strict ordering — tests wait for lower-order tests to complete (enables `--order-tests` automatically) |
| `--order-tag-prefix` | Prefix for order tags (default: `ORDER`) |
| `-rf` / `--rerun-failures` | Path to `failing_scenarios.txt` file to rerun failed scenarios |

## Configuration File

Instead of passing arguments on every command line invocation, you can place a configuration file in your project root. BehaveX auto-discovers it in this order:

| Priority | Source |
|---|---|
| 1 (highest) | `--config <path>` — explicit path |
| 2 | `behavex.cfg` in the current working directory |
| 3 | `behavex.ini` in the current working directory |
| 4 | `behave.ini` in the current working directory |
| 5 (lowest) | Built-in defaults |

### Format

The file uses INI syntax. All CLI arguments go under `[params]`. BehaveX also recognises `[output]`, `[progress_bar]`, and `[test_run]` for settings that have no CLI equivalent.

```ini
[output]
path = test-results              # folder where HTML/JSON/JUnit reports are written

[progress_bar]
print_updates_in_new_lines = True    # True: each update on a new line; False: overwrite

[test_run]
tags_to_skip = @SKIP, @MANUAL   # always excluded, regardless of --tags

[params]
# Filtering
tags               = @SMOKE, @REGRESSION        # AND-ed; equivalent to multiple --tags
name               = checkout                   # substring match on scenario name (not compatible with parallel execution)
exclude            = .*draft.*                  # regex — matching feature files are skipped

# Parallelism
parallel_processes = 4
parallel_scheme    = scenario                   # scenario | feature
parallel_delay     = 500                        # ms delay between spawning each worker

# Output & formatters
show_progress_bar  = True
formatter          = behavex.outputs.formatters.allure_behavex_formatter:AllureBehaveXFormatter
formatter_outdir   = allure-results
formatter_attach_logs = True

# Test ordering
order_tests        = True
order_tests_strict = False
order_tag_prefix   = PRIORITY

# Rerun failures
rerun_failures     = output/failing_scenarios.txt
include_paths      = tests/smoke, tests/regression

# Behave pass-through
dry_run            = False
logging_level      = DEBUG                      # CRITICAL | ERROR | WARNING | INFO | DEBUG | NOTSET
define             = env=staging db_host=localhost
```

> **Tip:** Use `--config` to target any file explicitly — useful for environment-specific configs:
> ```bash
> behavex features/ --config ci/behavex_ci.cfg
> ```

### Parameters Incompatible with Parallel Execution

`stop`, `wip`, and `name` are accepted in the config file but do not work correctly when `parallel_processes > 1`:

| Parameter | Problem |
|---|---|
| `stop` | Only stops the worker that hits the first failure; other workers keep running |
| `wip` | May cause individual workers to fail when no `@wip` scenarios are assigned to them |
| `name` | Filter runs inside each worker after scenarios have already been dispatched, which can silently drop scenarios |

Use `--tags @WIP` instead of `wip`. For fail-fast behaviour, combine `stop` with `--parallel-processes 1`.

### Behave Arguments Not Yet Supported in Config File

| Behave Argument | Description |
|---|---|
| `--no-color` | Disable colored output |
| `--no-capture` | Don't capture stdout from steps |
| `--capture-stderr` | Capture stderr from steps |
| `--no-logcapture` | Don't capture logging output from steps |
| `--no-snippets` | Suppress undefined step snippets |
| `--logging-format` | Custom log format string |
| `--logging-datefmt` | Custom log date format |
| `--logging-filter` | Logging filter name |
| `--lang` | Feature file language code (e.g. `es`, `fr`) |
| `--stage` | Steps sub-directory stage prefix |

## Constraints

- Not all Behave arguments are yet supported.
- Parallel execution is implemented using concurrent Behave processes. Hook firing frequency varies by parallel scheme — see [Hooks in Parallel Execution](parallel-execution.md).

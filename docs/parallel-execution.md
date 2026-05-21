# Parallel Execution

BehaveX manages concurrent Behave instances across multiple processes. You can run tests in parallel by feature or by scenario. When using the scenario scheme, examples within a scenario outline are also parallelized.

![Parallel Test Executions](https://github.com/hrcorval/behavex/blob/master/img/behavex_parallel_executions.png?raw=true)

## Basic Usage

```bash
behavex --parallel-processes=3
behavex -t=@TAG --parallel-processes=3
behavex -t=@TAG --parallel-processes=2 --parallel-scheme=scenario
behavex -t=@TAG --parallel-processes=5 --parallel-scheme=feature
behavex -t=@TAG --parallel-processes=5 --parallel-scheme=feature --show-progress-bar
```

## Worker ID

BehaveX injects the `worker_id` variable into each Behave process context. With `--parallel-processes 2`, the first instance receives `worker_id=0` and the second receives `worker_id=1`.

Access it in step definitions or hooks:

```python
context.config.userdata['worker_id']
```

## Hooks in Parallel Execution

### Hook Firing Matrix

| Hook | Sequential | `--parallel-scheme feature` | `--parallel-scheme scenario` |
|---|---|---|---|
| `before_all_workers` | Once — coordinator | Once — coordinator | Once — coordinator |
| `before_all` | Once | Once per worker | Once per worker |
| `before_feature` | Once per feature | Once per feature ✓ | Once per scenario ⚠ |
| `before_scenario` | Once per scenario | Once per scenario | Once per scenario |
| `after_scenario` | Once per scenario | Once per scenario | Once per scenario |
| `after_feature` | Once per feature | Once per feature ✓ | Once per scenario ⚠ |
| `after_all` | Once | Once per worker | Once per worker |
| `after_all_workers` | Once — coordinator | Once — coordinator | Once — coordinator |

> **⚠ scenario scheme**: Each worker process runs a single scenario. As a result, `before_feature` and `after_feature` fire once per scenario — the same frequency as `before_scenario` / `after_scenario`.

### BehaveX-Specific Hooks

BehaveX adds `before_all_workers` and `after_all_workers`, which run once in the **coordinator process** — before any worker starts and after all workers finish. They are the right place for global setup/teardown that must not repeat across workers.

```python
def before_all_workers(context):
    # Values set here are injected into every worker's context before before_all fires.
    context.base_url = "https://staging.example.com"
    context.db_name = "test_db"
    context.retry_count = 3

def after_all_workers(context):
    print(f"All workers finished. Base URL was: {context.base_url}")
```

> **Important:** Values set on `context` in `before_all_workers` must be JSON-serializable (str, int, float, bool, list, dict, or None). Non-serializable values (e.g., database connections, sockets) raise a `TypeError` immediately.

### Execution Metadata: `context.behavex`

BehaveX injects a `context.behavex` namespace in every worker process, available from `before_all` onwards:

| Attribute | Type | Description |
|---|---|---|
| `context.behavex.parallel_scheme` | `str` | `'scenario'` or `'feature'` |
| `context.behavex.parallel_processes` | `int` | Number of parallel workers configured |
| `context.behavex.is_worker` | `bool` | `True` when running inside a worker subprocess |
| `context.behavex.worker_id` | `int` | Worker index (0 in single-process mode) |

**Guard feature-level setup in scenario-parallel mode:**

```python
def before_feature(context, feature):
    if context.behavex.parallel_scheme == 'scenario':
        return  # fires once per scenario here — move setup to before_scenario
    setup_feature_database(feature.name)

def after_feature(context, feature):
    if context.behavex.parallel_scheme == 'scenario':
        return
    teardown_feature_database(feature.name)
```

**Allocate resources per worker:**

```python
def before_all(context):
    if context.behavex.is_worker:
        context.browser = create_browser(worker_id=context.behavex.worker_id)

def after_all(context):
    if context.behavex.is_worker:
        context.browser.quit()
```

## Test Execution Ordering

BehaveX lets you control the execution order of scenarios and features in parallel runs using special order tags.

### Use Cases

- **Setup/teardown**: Ensure setup scenarios run first and cleanup runs last
- **Data dependencies**: Run data-creation tests before tests that consume that data
- **Smoke testing**: Prioritize critical smoke tests
- **Parallel optimization**: Run slower scenarios first to maximize worker utilization

### Order Tags

Add `@ORDER_NNN` tags to your scenarios or features:

```gherkin
@ORDER_001
Scenario: Run first
    Given I perform initial setup

@ORDER_010
Scenario: Run second
    Given the initial setup is complete

@ORDER_100
Scenario: Run last
    Given all previous tests have completed
```

**Rules:**
- Lower numbers execute first (`@ORDER_001` before `@ORDER_010`)
- Scenarios without order tags get default order `9999`
- Use zero-padded numbers for clarity (`001`, `010`, `100`)
- Ordering only works with `--parallel-processes > 1`

### Regular vs Strict Ordering

#### Regular Ordering (`--order-tests`)

Tests are sorted by order tags but can run simultaneously if parallel processes are available.

```bash
behavex --order-tests --parallel-processes=4 -t=@SMOKE
```

- **Faster**: all processes run concurrently
- Best for: performance optimization, general prioritization

#### Strict Ordering (`--order-tests-strict`)

Tests wait for all lower-order tests to complete before starting.

```bash
behavex --order-tests-strict --parallel-processes=3 -t=@INTEGRATION
```

- **Slower but guaranteed**: `@ORDER_002` won't start until all `@ORDER_001` tests finish
- Best for: setup/teardown sequences, strict data dependencies
- `--order-tests-strict` automatically enables `--order-tests`

**Performance comparison:**
```
Scenario: 6 tests tagged ORDER_001, ORDER_002, ORDER_003 with 3 parallel processes

Regular ordering (--order-tests):
  Time 0: ORDER_001, ORDER_002, ORDER_003 all start simultaneously
  Total time: ~1 minute

Strict ordering (--order-tests-strict):
  Time 0: Only ORDER_001 tests start
  Time 1: ORDER_001 finishes → ORDER_002 starts
  Time 2: ORDER_002 finishes → ORDER_003 starts
  Total time: ~3 minutes
```

### Custom Order Prefix

```bash
behavex --order-tests --order-tag-prefix=PRIORITY --parallel-processes=3
```

```gherkin
@PRIORITY_001
Scenario: High priority scenario

@PRIORITY_050
Scenario: Medium priority scenario

@PRIORITY_100
Scenario: Low priority scenario
```

### Feature-Level Ordering

When using `--parallel-scheme=feature`, place order tags on the feature itself:

```gherkin
@ORDER_001
Feature: Database Setup
    Scenario: Create schema
    Scenario: Insert initial data

@ORDER_002
Feature: Application Tests
    Scenario: Test user login

Feature: Unordered Feature
    # No ORDER tag — gets default order 9999
```

# Migrating from Behave to BehaveX

BehaveX is a drop-in wrapper over Behave — your existing feature files and step definitions work unchanged. However, there are a few behavioral differences to be aware of when migrating, particularly when running tests in parallel.

## 1. Hooks Behavior

Behave's standard hooks (`before_all`, `before_feature`, `before_scenario`, etc.) work in BehaveX, but their **firing frequency changes depending on the parallel scheme**. For example, in `--parallel-scheme scenario`, `before_feature` and `after_feature` fire once per scenario rather than once per feature. Review the [Hook Firing Matrix](parallel-execution.md) before migrating any setup or teardown logic.

BehaveX also introduces two new hooks not available in Behave:

- **`before_all_workers`** — runs once in the coordinator process before any parallel worker starts.
- **`after_all_workers`** — runs once in the coordinator process after all workers finish.

These fill a critical gap in Behave's lifecycle: they give you a single place for global setup and teardown that must not repeat across workers. See [BehaveX-Specific Hooks](parallel-execution.md) for full documentation and examples.

## 2. Logs in Parallel Execution

When running tests in parallel, log output is **not printed to the console** during execution. Instead, BehaveX generates a dedicated log file for each scenario, which is linked directly in the HTML report. This keeps the console clean during parallel runs while still giving you full per-scenario log detail in the report.

## 3. Supported Arguments

Not all Behave CLI arguments are supported by BehaveX, and BehaveX adds its own set of arguments for parallel execution, reporting, and test control. Before migrating your CI scripts or run configurations, review:

- [Supported Behave Arguments](cli-reference.md)
- [BehaveX-Specific Arguments](cli-reference.md)

## 4. Using an existing behave.ini

BehaveX auto-discovers `behavex.cfg`, `behavex.ini`, and `behave.ini` in the current working directory. It reads BehaveX parameters only from files that contain at least one BehaveX-specific section (`[params]`, `[output]`, `[test_run]`, or `[progress_bar]`).

If your project already has a `behave.ini` with only a `[behave]` section, BehaveX leaves it untouched and lets Behave handle it. This means:

- Multi-line continuation values in `behave.ini` (standard `configparser` syntax) are fully supported — BehaveX will not try to parse them.
- There is no need to maintain separate config files for BehaveX and Behave if you only need Behave settings.

To add BehaveX-specific settings alongside your existing `behave.ini`, either add a `[params]` section to it or create a separate `behavex.cfg` / `behavex.ini` file in the same directory.

See [CLI Reference](cli-reference.md) for the full list of configurable parameters.

## 5. Local packages and sys.path

BehaveX automatically adds the project root (the directory you run `behavex` from) to `sys.path`. This means local packages sitting alongside your `features/` folder are importable from `environment.py` and step definitions without any extra configuration:

```
project/
├── automation/        ← importable as "from automation import ..."
└── features/
    ├── environment.py
    └── steps/
```

This works in all execution modes — single-process, feature-parallel, and scenario-parallel — including inside spawned worker processes on macOS and Windows. There is no need to set `PYTHONPATH=.` when running BehaveX.

## 6. Allure Reports

If you were using Behave's standard Allure formatter, **do not use it with BehaveX**. The standard formatter breaks under parallel execution because each worker writes to the same output directory concurrently, producing incomplete or corrupted reports.

BehaveX ships its own Allure formatter that processes the consolidated `report.json` after all parallel workers finish, ensuring results from all processes are correctly aggregated. See [Allure Reports Integration](reporting.md) for setup instructions.

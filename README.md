[![Downloads](https://static.pepy.tech/badge/behavex/month)](https://pepy.tech/project/behavex)
[![PyPI version](https://badge.fury.io/py/behavex.svg)](https://badge.fury.io/py/behavex)
[![Python Versions](https://img.shields.io/pypi/pyversions/behavex.svg)](https://pypi.org/project/behavex/)
[![Dependency Status](https://img.shields.io/librariesio/github/hrcorval/behavex)](https://libraries.io/github/hrcorval/behavex)
[![License](https://img.shields.io/github/license/hrcorval/behavex.svg)](https://github.com/hrcorval/behavex/blob/main/LICENSE)
[![Build Status](https://github.com/hrcorval/behavex/actions/workflows/python-package.yml/badge.svg)](https://github.com/hrcorval/behavex/actions)
[![GitHub last commit](https://img.shields.io/github/last-commit/hrcorval/behavex.svg)](https://github.com/hrcorval/behavex/commits/main)

# BehaveX

> Production-grade test orchestration for Python BDD.

![BehaveX HTML Report Demo](https://github.com/hrcorval/behavex/blob/master/img/demo.gif?raw=true)

**BehaveX** extends [Behave](https://behave.readthedocs.io) with parallel execution, enterprise-grade reporting, and the operational controls needed to run test suites at scale. Downloaded **121,000+ times per month**.

## ✨ Latest Features

🪝 **`before_all_workers` / `after_all_workers` hooks** *(v4.6.4)* — New lifecycle hooks that run once in the coordinator process, before any worker starts and after all finish. Values set on `context` are injected into every worker automatically.

📊 **`context.behavex` execution metadata** *(v4.6.4)* — BehaveX now injects a `context.behavex` namespace into every worker: `parallel_scheme`, `parallel_processes`, `is_worker`, `worker_id`.

🚫 **`--no-report` flag** *(v4.6.4)* — Disables all file output. No HTML/JSON/XML reports or output folder are created. Evidence is redirected to the system temp directory. Designed for read-only CI environments.

🔍 **Stack Trace on Error** *(v4.6.2)* — Click on any failed step in the HTML report to expand the full stack trace inline.

📐 **Gherkin Rule Section Support** *(v4.6.2)* — Full support for `Rule:` blocks in feature files.

🏷️ **Tag Expressions v2** *(v4.6.0)* — Native Cucumber-style tag expressions with boolean logic, parentheses, and wildcards.

🚀 **Enhanced Behave Integration** *(v4.5.0)* — Support for Behave >= 1.3.0. Major performance overhaul.

📊 **Interactive Execution Timeline** *(v4.5.0)* — Visual timeline showing scenario execution across parallel workers.

🎯 **Test Execution Ordering** *(v4.4.1)* — Control scenario/feature order in parallel runs with `@ORDER_001` tags.

## Installation

```bash
pip install behavex
```

## Quick Start

```bash
# Run all scenarios
behavex

# Run scenarios tagged @smoke with 4 parallel processes
behavex -t=@smoke --parallel-processes=4 --parallel-scheme=scenario

# Cucumber-style tag filtering (Behave 1.3.0+)
behavex -t="(@smoke or @regression) and not @slow" --parallel-processes=4

# Dry run — list all scenarios in HTML report without executing
behavex -t=@smoke --dry-run
```

## BehaveX vs Behave

BehaveX is a zero-friction upgrade — your existing feature files and step definitions work unchanged.

| Capability | Behave | BehaveX |
|---|---|---|
| Parallel execution | ❌ | ✅ By feature or scenario, N processes |
| HTML report | ❌ | ✅ With screenshots, logs, evidence |
| Allure integration | ❌ | ✅ Full support with thread labels |
| Auto-retry on failure | ❌ | ✅ `@AUTORETRY` / `@AUTORETRY_3` |
| Test muting | ❌ | ✅ `@MUTE` — run but exclude from CI results |
| Execution ordering | ❌ | ✅ `@ORDER_001` tags for dependency-aware runs |
| Execution timeline | ❌ | ✅ Visual timeline across parallel workers |
| Pass rate & automation metrics | ❌ | ✅ Per-run dashboard in HTML report |
| Dry run with HTML report | Basic | ✅ Shareable spec report |
| Per-scenario log files | ❌ | ✅ Linked directly in HTML report |
| Screenshot evidence | ❌ | ✅ Via `behavex-images` |

## Who Uses BehaveX

- **[Apache NiFi MiNiFi C++](https://github.com/apache/nifi-minifi-cpp)** — The Apache Foundation uses BehaveX for their C++ dataflow agent.
- **[LambdaTest](https://github.com/LambdaTest/Python-Behave-Selenium)** — Featured in LambdaTest's official Python BDD documentation.
- **[SovereignCloudStack](https://github.com/SovereignCloudStack/scs-health-monitor)** — Used for real-life IaaS/KaaS health monitoring in the Gaia-X ecosystem.
- **[Qase](https://github.com/rmontemor-qase/behavex-qase-integration)** — Official integration with the Qase enterprise test management platform.

*Using BehaveX? [Open a PR](https://github.com/hrcorval/behavex/pulls) to be listed here.*

## Documentation

Full documentation at **[behavex.readthedocs.io](https://behavex.readthedocs.io)**

- [Getting Started](https://behavex.readthedocs.io/getting-started.html)
- [Migrating from Behave](https://behavex.readthedocs.io/migrating-from-behave.html)
- [Tag Expressions](https://behavex.readthedocs.io/tag-expressions.html)
- [Parallel Execution](https://behavex.readthedocs.io/parallel-execution.html)
- [Reporting](https://behavex.readthedocs.io/reporting.html)
- [Test Management](https://behavex.readthedocs.io/test-management.html)
- [CLI Reference](https://behavex.readthedocs.io/cli-reference.html)
- [Utilities](https://behavex.readthedocs.io/utilities.html)

## Get Involved

BehaveX grows through community use and contribution. If it's useful to your team:

- **⭐ Star the repo** — helps other teams discover the project
- **🐛 Report issues** — your use case helps improve BehaveX for everyone
- **🔧 Contribute** — PRs are welcome, from docs to features
- **📢 Spread the word** — mention BehaveX when you talk about Python testing

Used by the **Apache Foundation**, **LambdaTest**, **SovereignCloudStack**, and teams worldwide.

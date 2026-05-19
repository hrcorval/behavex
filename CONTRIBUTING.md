# Contributing to BehaveX

Thank you for your interest in contributing to BehaveX. Every contribution — code, bug reports, ideas, or documentation — helps make the framework better for everyone.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Running the Tests](#running-the-tests)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Reporting Issues](#reporting-issues)
- [Contributors](#contributors)

---

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a branch for your change (`git checkout -b fix/my-fix` or `feat/my-feature`)
4. Make your changes
5. Run the test suite
6. Open a pull request

---

## Development Setup

BehaveX uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
# Clone and install
git clone https://github.com/hrcorval/behavex.git
cd behavex
uv sync
```

Always invoke BehaveX via `uv run behavex`. Never use `python -m behavex` or bare `behavex`.

---

## Running the Tests

BehaveX is tested using BehaveX itself (meta-testing). The test suite lives in `tests/features/`.

```bash
# Run the full test suite
uv run behavex tests/features/ --output output/test_run

# Run in parallel (faster)
uv run behavex tests/features/ --output output/test_run --parallel-processes 2 --parallel-scheme scenario

# Run a specific feature
uv run behavex tests/features/my_feature.feature --output output/test_run
```

When adding new functionality, add corresponding BDD scenarios under `tests/features/`. When fixing a bug, add a scenario that reproduces it.

---

## Submitting a Pull Request

- Keep PRs focused — one fix or feature per PR
- Add or update tests for your change
- Follow existing code style (Python type hints where applicable)
- Write commit messages in English
- Reference any related issue in the PR description

For significant changes, open an issue or a [Discussion](https://github.com/hrcorval/behavex/discussions) first to align on approach before investing time in implementation.

---

## Reporting Issues

Please open a [GitHub Issue](https://github.com/hrcorval/behavex/issues) with:

- BehaveX version (`uv run behavex --version`)
- Python version
- Operating system
- Minimal reproduction case (feature file + steps if applicable)
- Full error output

---

## Contributors

BehaveX has been shaped by many contributors over the years. Thank you to everyone who has submitted a pull request, reported a bug, or proposed an idea.

### Code Contributors

| Contributor | Contributions |
|---|---|
| [@iamkenos](https://github.com/iamkenos) | Allure formatter fixes (background steps, step serialization), ANSI code stripping in reports, scenario UUID hashing, path resolution fix, env var table alignment |
| [@anibalinn](https://github.com/anibalinn) | Documentation improvements, dry-run examples, release support |
| [@AppeltansPieter](https://github.com/AppeltansPieter) | Non-zero exit code on parallel process failure, XML report fix when running from features folder |
| [@balaji2711](https://github.com/balaji2711) | Documentation fixes and parallel execution examples |
| [@danzou56](https://github.com/danzou56) | Replaced `htmlmin` with `minify_html` for report minification |
| [@JackHerRrer](https://github.com/JackHerRrer) | Added unique ID to each Behave instance |
| [@AxelFurlanF](https://github.com/AxelFurlanF) | Fixed Behave `DeprecationWarning` for pattern usage |
| [@sebns](https://github.com/sebns) | Fixed tag collection in feature files |
| [@ido-ran](https://github.com/ido-ran) | Added support for `before_tag` hook |
| [@warshaya](https://github.com/warshaya) | Environment variable handling improvement |
| [@RemoYukoff](https://github.com/RemoYukoff) | Fixed invalid escape sequences |

### Bug Reporters

These contributors reported issues that led to concrete fixes in BehaveX:

| Contributor | Issue | Fix |
|---|---|---|
| [@rsapping3](https://github.com/rsapping3) | `KeyError: 'error_lines'` in XML report generation | Fixed in v4.6.1 |
| [@jbridger](https://github.com/jbridger) | `ImportError` during step loading produced misleading results | Fixed in v4.6.1 |
| [@karl0ss](https://github.com/karl0ss) | Scenario output not visible in console | Fixed in v4.6.2 |
| [@kconkas](https://github.com/kconkas) | `environment.py` hooks executing during dry runs; `NameError: as_completed` | Fixed in v4.1.0 |
| [@michalkovy](https://github.com/michalkovy) | Exit code 0 when `before_all` hook fails | Fixed in v4.4.x |
| [@vibin-c](https://github.com/vibin-c) | Python 3.12 `distutils` incompatibility; Snyk vulnerability in Zipp | Fixed in v4.4.2 |
| [@Kikkomanq](https://github.com/Kikkomanq) | Python 3.13 installation failure | Fixed in v4.1.2 |
| [@athiradamodaran](https://github.com/athiradamodaran) | Scenario outline names not displayed correctly in reports | Fixed in v4.3.x |
| [@AppeltansPieter](https://github.com/AppeltansPieter) | Zero exit code when parallel process fails | Fixed in v4.6.2 |
| [@Mahul1992](https://github.com/Mahul1992) | Configuration params not read from `behavex.cfg` / `behavex.ini` | Fixed in v4.6.2 |

### Ideas and Inspiration

These contributors proposed features or opened PRs whose ideas directly shaped what was ultimately implemented:

| Contributor | Contribution |
|---|---|
| [@bombsimon](https://github.com/bombsimon) | Proposed full stack trace display on errors and `isatty` support for TeePrinter |
| [@BackstageBones](https://github.com/BackstageBones) | Proposed enhanced error parsing with full traceback |
| [@chriskite](https://github.com/chriskite) | Proposed Gherkin `Rule` section support |
| [@jbridger](https://github.com/jbridger) | Reported and investigated parallel execution issues |
| [@lawnmowerlatte](https://github.com/lawnmowerlatte) | Proposed feature sorting for optimized parallel runtime |
| [@zizzard](https://github.com/zizzard) | Proposed temporary file prefix configuration |

---
name: Bug report
about: Report a bug or unexpected behavior in BehaveX
title: '[BUG] '
labels: bug
assignees: ''

---

## Description

A clear and concise description of the bug.

## Environment

- **BehaveX version** (`uv run behavex --version`):
- **Behave version** (`pip show behave | grep Version`):
- **Python version** (`python --version`):
- **Operating system**:

## Reproduction

Minimal feature file and steps to reproduce the issue:

```gherkin
Feature: Example
  Scenario: Failing scenario
    Given ...
    When ...
    Then ...
```

```python
# steps/example.py
@given('...')
def step_impl(context):
    ...
```

**Command used:**
```bash
uv run behavex features/example.feature --parallel-processes 2
```

## Expected behavior

What you expected to happen.

## Actual behavior

What actually happened.

## Full error output

```
paste full traceback or error output here
```

## Additional context

Any other context (e.g., `environment.py` hooks, custom formatters, CI environment).

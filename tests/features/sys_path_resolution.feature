Feature: Project root is in sys.path for environment.py imports and worker processes

  BehaveX must add the project root (CWD) to sys.path before loading environment.py
  and before spawning worker processes, so that local packages are importable.
  Regression: Issue #247 — Bug 2.

  Background:
    Given I have installed behavex

  # ── Exact reporter scenario: environment.py with NO BehaveX hooks ───────────
  # The crash in 4.6.4 happened when _call_bhx_hook loaded environment.py to
  # check for before_all_workers. If the file has a top-level import from a
  # local package, it fails before any hook is even called.

  @SYS_PATH @SYS_PATH_COORDINATOR
  Scenario: environment.py without BehaveX hooks can import local packages with a single process
    Given a project directory with a local package and a plain environment.py that imports from it
    When I run behavex from that project directory with "1" parallel process
    Then behavex should exit with code 0 and no ImportError

  @SYS_PATH @SYS_PATH_WORKER
  Scenario: environment.py without BehaveX hooks can import local packages with parallel worker processes
    Given a project directory with a local package and a plain environment.py that imports from it
    When I run behavex from that project directory with "2" parallel processes
    Then behavex should exit with code 0 and no ImportError

  # ── Variant: environment.py with before_all_workers ───────────────────────

  @SYS_PATH @SYS_PATH_COORDINATOR
  Scenario: environment.py with before_all_workers can import local packages with a single process
    Given a project directory with a local package and an environment.py that imports from it
    When I run behavex from that project directory with "1" parallel process
    Then behavex should exit with code 0 and no ImportError

  @SYS_PATH @SYS_PATH_WORKER
  Scenario: environment.py with before_all_workers can import local packages with parallel worker processes
    Given a project directory with a local package and an environment.py that imports from it
    When I run behavex from that project directory with "2" parallel processes
    Then behavex should exit with code 0 and no ImportError

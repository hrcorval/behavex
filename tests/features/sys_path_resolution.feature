Feature: Project root is in sys.path for environment.py imports and worker processes

  BehaveX must add the project root (CWD) to sys.path before loading environment.py
  and before spawning worker processes, so that local packages are importable.
  Regression: Issue #247 — Bug 2.

  Background:
    Given I have installed behavex

  @SYS_PATH @SYS_PATH_COORDINATOR
  Scenario: environment.py can import local packages with a single process
    Given a project directory with a local package and an environment.py that imports from it
    When I run behavex from that project directory with "1" parallel process
    Then behavex should exit with code 0 and no ImportError

  @SYS_PATH @SYS_PATH_WORKER
  Scenario: environment.py can import local packages with parallel worker processes
    Given a project directory with a local package and an environment.py that imports from it
    When I run behavex from that project directory with "2" parallel processes
    Then behavex should exit with code 0 and no ImportError

# -*- coding: utf-8 -*-
"""BehaveX programmatic API."""
from __future__ import absolute_import

import contextlib
import io
import json
import os
import sys
import threading
from typing import Callable, List, Optional

from behavex import runner
from behavex.arguments import parse_arguments
from behavex.conf_mgr import get_env
from behavex.global_vars import global_vars
from behavex.outputs.report_utils import text
from behavex.utils import get_json_results

try:
    from behavex.models import DiscoveredScenario, FeatureResult, ProgressEvent, RunResult  # noqa: F401
except ImportError:
    raise ImportError(
        "BehaveXRunner requires pydantic. Install it with: pip install 'behavex[api]'"
    )


_run_lock = threading.Lock()
_running_instance: Optional["BehaveXRunner"] = None


@contextlib.contextmanager
def _exclusive_run():
    if not _run_lock.acquire(blocking=False):
        raise RuntimeError('Another BehaveXRunner.run() or discover() is active in this process; '
                           'BehaveX keeps its run state in module globals, so runs cannot overlap')
    try:
        yield
    finally:
        _run_lock.release()


def _to_feature_results(feature_dicts: List[dict]) -> List[FeatureResult]:
    return [FeatureResult.model_validate(feature_dict) for feature_dict in feature_dicts]


def _validate_args(args: List[str]) -> None:
    stderr = io.StringIO()
    try:
        with contextlib.redirect_stderr(stderr):
            parse_arguments(args)
    except SystemExit:
        raise ValueError(stderr.getvalue().strip().splitlines()[-1]) from None


class BehaveXRunner:
    """Programmatic interface for running BehaveX without the CLI; docs/behavex-api.md shows its use."""

    def __init__(
        self,
        paths: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        output_folder: str = "",
        parallel_processes: Optional[int] = None,
        parallel_scheme: Optional[str] = None,
        parallel_delay: Optional[int] = None,
        include_paths: Optional[List[str]] = None,
        dry_run: bool = False,
        stop_on_failure: bool = False,
        show_progress_bar: bool = False,
        no_report: bool = False,
        config: Optional[str] = None,
        rerun_failures: Optional[str] = None,
        formatter: Optional[str] = None,
        formatter_outdir: Optional[str] = None,
        formatter_attach_logs: Optional[bool] = None,
        order_tests: bool = False,
        order_tests_strict: bool = False,
        order_tag_prefix: Optional[str] = None,
        logging_level: Optional[str] = None,
        no_snippets: bool = False,
        name: Optional[str] = None,
        include: Optional[str] = None,
        exclude: Optional[str] = None,
        define: Optional[List[str]] = None,
        on_progress: Optional[Callable[["ProgressEvent"], None]] = None,
    ) -> None:
        self.paths = paths or []
        self.tags = tags or []
        self.output_folder = output_folder
        self.parallel_processes = parallel_processes
        self.parallel_scheme = parallel_scheme
        self.parallel_delay = parallel_delay
        self.include_paths = include_paths or []
        self.dry_run = dry_run
        self.stop_on_failure = stop_on_failure
        self.show_progress_bar = show_progress_bar
        self.no_report = no_report
        self.config = config
        self.rerun_failures = rerun_failures
        self.formatter = formatter
        self.formatter_outdir = formatter_outdir
        self.formatter_attach_logs = formatter_attach_logs
        self.order_tests = order_tests
        self.order_tests_strict = order_tests_strict
        self.order_tag_prefix = order_tag_prefix
        self.logging_level = logging_level
        self.no_snippets = no_snippets
        self.name = name
        self.include = include
        self.exclude = exclude
        self.define = define or []
        self.on_progress = on_progress

    @_exclusive_run()
    def run(self) -> RunResult:
        args = self._build_args()
        _validate_args(args)
        runner._progress_callback = self.on_progress
        runner._completed_count = 0
        runner._progress_total = None
        runner._last_run_results = []
        runner._progress_reported = set()
        runner._stop_requested = False
        runner._stopped = False
        runner._run_active = True
        global _running_instance
        _running_instance = self
        try:
            exit_code = runner.run(args)
        except SystemExit as exit_signal:
            if isinstance(exit_signal.code, str):
                raise ValueError('BehaveX stopped before running the tests: {}'.format(exit_signal.code)) from None
            # BehaveX exits on duplicated or unnamed scenarios after printing why
            raise ValueError('BehaveX stopped before running the tests (exit code {}); '
                             'its output explains why'.format(exit_signal.code)) from None
        finally:
            runner._progress_callback = None
            runner._run_active = False
            _running_instance = None
        return RunResult(run_id=runner._run_id, exit_code=exit_code, output_folder=os.path.abspath(get_env('OUTPUT')),
                         features=_to_feature_results(runner._last_run_results), stopped=runner._stopped)

    @_exclusive_run()
    def discover(self, check_steps: bool = False) -> List[DiscoveredScenario]:
        """List the scenarios run() would execute, without executing anything or writing any file.

        check_steps imports the step definitions in a separate process to fill undefined_steps.
        """
        args = self._build_args()
        _validate_args(args)
        runner._run_active = True
        try:
            # an MCP stdio server owns sys.stdout
            with contextlib.redirect_stdout(io.StringIO()):
                scenarios = runner.discover(args, check_steps)
        except SystemExit as exit_signal:
            raise ValueError('BehaveX stopped before discovering the tests: {}'.format(exit_signal.code)) from None
        finally:
            runner._run_active = False
        if scenarios is None:
            raise ValueError('BehaveX stopped before discovering the tests: '
                             'the rerun_failures file is missing or empty')
        return [DiscoveredScenario(feature=scenario.feature.name, name=scenario.name,
                                   filename=text(scenario.filename), line=scenario.line,
                                   tags=list(scenario.effective_tags), undefined_steps=undefined_steps)
                for scenario, undefined_steps in scenarios]

    def stop(self) -> None:
        """Stop this runner's parallel run from submitting more scenarios and cancel the queued ones.

        Running ones finish, and on Python 3.8 so do queued ones. No effect on single-process runs.
        """
        if _running_instance is not self:
            return
        runner._stop_requested = True
        executor = runner._active_executor
        if executor is None or not runner._is_parallel_run:
            return
        # Python 3.8 has no cancel_futures, and shutdown(wait=False) there can strand queued futures
        if sys.version_info >= (3, 9):
            executor.shutdown(wait=False, cancel_futures=True)

    @staticmethod
    def load_results(output_folder: str) -> RunResult:
        """Return the RunResult that the run which last wrote output_folder returned."""
        status_filename = global_vars.report_filenames['report_overall']
        status_path = os.path.join(output_folder, status_filename)
        try:
            with open(status_path) as status_file:
                overall_status = json.load(status_file)
        except FileNotFoundError:
            raise ValueError('No BehaveX run results in {}: it has no {} (a no_report run '
                             'writes none)'.format(output_folder, status_filename)) from None
        if 'exit_code' not in overall_status:
            raise ValueError('{} was written by a BehaveX older than 4.7.0, which does not '
                             'record the exit code'.format(status_path))
        report_filename = global_vars.report_filenames['report_json']
        try:
            json_report = get_json_results(output_folder)
        except FileNotFoundError:
            # A run that fails before writing its report (a failing before_all_workers hook or an
            # interrupt) exits 1, and its run() returned no features either
            if overall_status['exit_code'] == 0:
                raise ValueError('{} has no {} for a run that exited 0'.format(
                    output_folder, report_filename)) from None
            json_report = {'features': []}
        if 'features' not in json_report:
            raise ValueError('{} in {} has no features'.format(report_filename, output_folder))
        feature_dicts = json_report['features']
        return RunResult(run_id=overall_status['run_id'], exit_code=overall_status['exit_code'],
                         output_folder=os.path.abspath(output_folder),
                         features=_to_feature_results(feature_dicts), stopped=overall_status['stopped'])

    def _build_args(self) -> List[str]:
        args: List[str] = []

        for tag in self.tags:
            args.append(f"--tags={tag}")

        if self.output_folder:
            args.append(f"--output-folder={self.output_folder}")

        if self.parallel_processes is not None:
            args.append(f"--parallel-processes={self.parallel_processes}")

        if self.parallel_scheme is not None:
            args.append(f"--parallel-scheme={self.parallel_scheme}")

        if self.parallel_delay is not None:
            args.append(f"--parallel-delay={self.parallel_delay}")

        if self.include_paths:
            args += ["--include-paths"] + [runner._as_non_option(path) for path in self.include_paths]

        if self.dry_run:
            args.append("--dry-run")

        if self.stop_on_failure:
            args.append("--stop")

        if self.show_progress_bar:
            args.append("--show-progress-bar")

        if self.no_report:
            args.append("--no-report")

        if self.config is not None:
            args.append(f"--config={self.config}")

        if self.rerun_failures is not None:
            args.append(f"--rerun-failures={self.rerun_failures}")

        if self.formatter is not None:
            args.append(f"--formatter={self.formatter}")

        if self.formatter_outdir is not None:
            args.append(f"--formatter-outdir={self.formatter_outdir}")

        # Only --no-formatter-attach-logs exists.
        if self.formatter_attach_logs is False:
            args.append("--no-formatter-attach-logs")

        if self.order_tests:
            args.append("--order-tests")

        if self.order_tests_strict:
            args.append("--order-tests-strict")

        if self.order_tag_prefix is not None:
            args.append(f"--order-tag-prefix={self.order_tag_prefix}")

        if self.logging_level is not None:
            args.append(f"--logging-level={self.logging_level}")

        if self.no_snippets:
            args.append("--no-snippets")

        if self.name is not None:
            args.append(f"--name={self.name}")

        if self.include is not None:
            args.append(f"--include={self.include}")

        if self.exclude is not None:
            args.append(f"--exclude={self.exclude}")

        for definition in self.define:
            args.append(f"--define={definition}")

        if self.paths:
            args += ["--"] + self.paths

        return args

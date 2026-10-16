# -*- coding: utf-8 -*-
"""BehaveX programmatic API."""
from __future__ import absolute_import

import os
import uuid
from typing import Callable, List, Optional

from behavex import runner
from behavex.conf_mgr import get_env

try:
    from behavex.models import FeatureResult, ProgressEvent, RunResult  # noqa: F401
except ImportError:
    raise ImportError(
        "BehaveXRunner requires pydantic. Install it with: pip install 'behavex[api]'"
    )


class BehaveXRunner:
    """Programmatic interface for running BehaveX without the CLI.

    Usage::

        from behavex import BehaveXRunner

        result = BehaveXRunner(
            paths=["tests/features"],
            tags=["@smoke"],
            parallel_processes=4,
            output_folder="output",
        ).run()

        assert result.passed
    """

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

    def run(self) -> RunResult:
        run_id = str(uuid.uuid4())
        args = self._build_args()
        runner._progress_callback = self.on_progress
        runner._completed_count = 0
        runner._last_run_results = []
        try:
            exit_code = runner.run(args)
        finally:
            runner._progress_callback = None
        features = self._load_features()
        return RunResult(run_id=run_id, exit_code=exit_code, output_folder=os.path.abspath(get_env('OUTPUT')), features=features)

    def stop(self) -> None:
        """Cancel the work a parallel run has not started; running scenarios finish.

        Safe from another thread or on_progress. No effect on Python 3.8 or single-process runs.
        """
        executor = runner._active_executor
        if executor is None:
            return
        try:
            executor.shutdown(wait=False, cancel_futures=True)
        except TypeError:  # Python 3.8: no cancel_futures
            executor.shutdown(wait=False)

    def _load_features(self) -> List[FeatureResult]:
        """Works with no_report."""
        return [FeatureResult.model_validate(f) for f in runner._last_run_results]

    def _build_args(self) -> List[str]:
        args: List[str] = []

        args.extend(self.paths)

        for tag in self.tags:
            args += ["--tags", tag]

        if self.output_folder:
            args += ["--output-folder", self.output_folder]

        if self.parallel_processes is not None:
            args += ["--parallel-processes", str(self.parallel_processes)]

        if self.parallel_scheme is not None:
            args += ["--parallel-scheme", self.parallel_scheme]

        if self.parallel_delay is not None:
            args += ["--parallel-delay", str(self.parallel_delay)]

        if self.include_paths:
            args += ["--include-paths"] + self.include_paths

        if self.dry_run:
            args.append("--dry-run")

        if self.stop_on_failure:
            args.append("--stop")

        if self.show_progress_bar:
            args.append("--show-progress-bar")

        if self.no_report:
            args.append("--no-report")

        if self.config is not None:
            args += ["--config", self.config]

        if self.rerun_failures is not None:
            args += ["--rerun-failures", self.rerun_failures]

        if self.formatter is not None:
            args += ["--formatter", self.formatter]

        if self.formatter_outdir is not None:
            args += ["--formatter-outdir", self.formatter_outdir]

        # Only --no-formatter-attach-logs exists.
        if self.formatter_attach_logs is False:
            args.append("--no-formatter-attach-logs")

        if self.order_tests:
            args.append("--order-tests")

        if self.order_tests_strict:
            args.append("--order-tests-strict")

        if self.order_tag_prefix is not None:
            args += ["--order-tag-prefix", self.order_tag_prefix]

        if self.logging_level is not None:
            args += ["--logging-level", self.logging_level]

        if self.no_snippets:
            args.append("--no-snippets")

        if self.name is not None:
            args += ["--name", self.name]

        if self.include is not None:
            args += ["--include", self.include]

        if self.exclude is not None:
            args += ["--exclude", self.exclude]

        for definition in self.define:
            args += ["-D", definition]

        return args

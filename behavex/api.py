# -*- coding: utf-8 -*-
"""BehaveX programmatic API."""
from __future__ import absolute_import

import json
import os
import uuid
from typing import List, Optional

from behavex import runner

try:
    from behavex.models import FeatureResult, RunResult
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
        stop: bool = False,
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
    ) -> None:
        self.paths = paths or []
        self.tags = tags or []
        self.output_folder = output_folder
        self.parallel_processes = parallel_processes
        self.parallel_scheme = parallel_scheme
        self.parallel_delay = parallel_delay
        self.include_paths = include_paths or []
        self.dry_run = dry_run
        self.stop = stop
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

    def run(self) -> RunResult:
        """Execute the test run and return a RunResult."""
        run_id = str(uuid.uuid4())
        args = self._build_args()
        exit_code = runner.run(args)
        features = self._load_features()
        return RunResult(run_id=run_id, exit_code=exit_code, output_folder=self.output_folder, features=features)

    def _load_features(self) -> List[FeatureResult]:
        """Read report.json after a run and return parsed feature results."""
        if self.no_report or not self.output_folder:
            return []
        report_path = os.path.join(self.output_folder, 'report.json')
        if not os.path.exists(report_path):
            return []
        with open(report_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return [FeatureResult.model_validate(feature) for feature in data.get('features', [])]

    def _build_args(self) -> List[str]:
        """Translate instance params into a CLI args list for runner.run()."""
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

        if self.stop:
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

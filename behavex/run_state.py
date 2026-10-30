# -*- coding: utf-8 -*-

from concurrent.futures import ProcessPoolExecutor
from typing import Callable, Optional


class RunState:

    def __init__(self):
        self.progress_callback: Optional[Callable] = None
        self.completed_count: int = 0
        self.progress_total: Optional[int] = None
        self.is_parallel_run: bool = False
        self.active_executor: Optional[ProcessPoolExecutor] = None
        # The executor's own process dict, which its shutdown() drops while the workers still run
        self.active_executor_processes_by_pid: dict = {}
        self.last_run_results: list = []
        self.progress_reported: set = set()
        self.run_active: bool = False
        self.stop_requested: bool = False
        self.stopped: bool = False
        self.run_id: Optional[str] = None
        self.host_queue = None

    def reset_for_run(self, progress_callback) -> None:
        self.__init__()
        self.progress_callback = progress_callback
        self.run_active = True

    def fire_progress(self, scenario_name: str, feature_name: str, status: str, duration: float) -> None:
        """Never raises."""
        if self.progress_callback is None:
            return
        try:
            from behavex.models import ProgressEvent
            self.completed_count += 1
            self.progress_callback(ProgressEvent(
                scenario_name=scenario_name,
                feature_name=feature_name,
                status=status,
                duration=duration,
                completed_count=self.completed_count,
                total=self.progress_total,
            ))
        except Exception:
            pass

    def fire_report_progress(self, json_report, already_reported=frozenset()) -> None:
        """Never raises. already_reported holds (feature filename, scenario line) keys to skip."""
        if self.progress_callback is None:
            return
        try:
            for feature in json_report.get('features', []):
                for scenario in feature.get('scenarios', []):
                    if (feature.get('filename'), scenario.get('line')) in already_reported:
                        continue
                    self.fire_progress(
                        scenario_name=scenario.get('name', ''),
                        feature_name=feature.get('name', ''),
                        status=scenario.get('status', ''),
                        duration=float(scenario.get('duration', 0.0)),
                    )
        except Exception:
            pass

    def report_scenario_progress(self, scenario_key, **progress_fields) -> None:
        """Fire on_progress for a finished scenario; a single-process worker hands it to the host process."""
        if self.host_queue is not None:
            self.host_queue.put(('progress', (scenario_key, progress_fields)))
            return
        self.progress_reported.add(scenario_key)
        self.fire_progress(**progress_fields)


state = RunState()

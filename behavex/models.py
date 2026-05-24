# -*- coding: utf-8 -*-
"""Pydantic models for BehaveXRunner structured output."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

# Behave statuses that indicate an unexpected exception rather than an assertion failure.
# hook_error: exception in a before/after hook
# cleanup_error: exception during teardown
_ERROR_STATUSES = frozenset({'error', 'hook_error', 'cleanup_error'})

# Statuses that mean the scenario never actually ran.
_UNTESTED_STATUSES = frozenset({'untested', 'untested_pending', 'untested_undefined', 'undefined'})


class ProgressEvent(BaseModel):
    model_config = ConfigDict(extra='ignore')

    scenario_name: str
    feature_name: str
    status: str
    duration: float
    completed: int


class StepResult(BaseModel):
    model_config = ConfigDict(extra='ignore')

    step_type: str
    name: str
    status: str
    duration: float
    line: int
    start: int = 0
    stop: int = 0
    text: Optional[str] = None
    error_msg: Optional[str] = None
    error_lines: List[str] = Field(default_factory=list)

    @model_validator(mode='before')
    @classmethod
    def _normalize_text(cls, data: dict) -> dict:
        if isinstance(data, dict) and data.get('text') == 'None':
            data['text'] = None
        return data


class BackgroundResult(BaseModel):
    model_config = ConfigDict(extra='ignore')

    duration: float = 0.0
    steps: List[StepResult] = Field(default_factory=list)


class ScenarioResult(BaseModel):
    model_config = ConfigDict(extra='ignore')

    name: str
    status: str
    duration: float
    line: int
    tags: List[str] = Field(default_factory=list)
    filename: str = ''
    feature: str = ''
    steps: List[StepResult] = Field(default_factory=list)
    background: BackgroundResult = Field(default_factory=BackgroundResult)
    error_msg: List[str] = Field(default_factory=list)
    error_lines: List[str] = Field(default_factory=list)
    error_step: Optional[StepResult] = None
    start: int = 0
    stop: int = 0
    worker_id: str = ''

    @property
    def is_manual(self) -> bool:
        return 'MANUAL' in self.tags

    @property
    def is_muted(self) -> bool:
        """Scenarios tagged @MUTE are silenced — failures don't affect the exit code."""
        return 'MUTE' in self.tags

    @property
    def passed(self) -> bool:
        return self.status == 'passed'

    @property
    def failed(self) -> bool:
        """Assertion failure, not silenced by @MUTE."""
        return self.status == 'failed' and not self.is_muted

    @property
    def errored(self) -> bool:
        """Unexpected exception (error/hook_error/cleanup_error), not silenced by @MUTE."""
        return self.status in _ERROR_STATUSES and not self.is_muted

    @property
    def muted(self) -> bool:
        """Failed or errored scenario whose failures are silenced by @MUTE."""
        return self.is_muted and (self.status == 'failed' or self.status in _ERROR_STATUSES)

    @property
    def skipped(self) -> bool:
        """Programmatically skipped via context.scenario.skip(), not a @MANUAL scenario."""
        return self.status == 'skipped' and not self.is_manual

    @property
    def untested(self) -> bool:
        """Never executed — stopped before reaching this scenario, or step undefined."""
        return self.status in _UNTESTED_STATUSES


class FeatureResult(BaseModel):
    model_config = ConfigDict(extra='ignore')

    name: str
    status: str
    duration: float
    filename: str = ''
    scenarios: List[ScenarioResult] = Field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.status == 'passed'

    @property
    def failed(self) -> bool:
        return self.status == 'failed'

    @property
    def failed_scenarios(self) -> List[ScenarioResult]:
        """Assertion failures only, excluding muted."""
        return [s for s in self.scenarios if s.failed]

    @property
    def errored_scenarios(self) -> List[ScenarioResult]:
        """Unexpected exceptions only, excluding muted."""
        return [s for s in self.scenarios if s.errored]

    @property
    def muted_scenarios(self) -> List[ScenarioResult]:
        return [s for s in self.scenarios if s.muted]


class RunSummary(BaseModel):
    model_config = ConfigDict(extra='ignore')

    total: int
    passed: int
    failed: int
    errored: int = 0
    skipped: int
    manual: int = 0
    muted: int = 0
    untested: int = 0


class RunResult(BaseModel):
    model_config = ConfigDict(extra='ignore')

    run_id: str
    exit_code: int
    output_folder: str
    features: List[FeatureResult] = Field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.exit_code == 0

    @property
    def summary(self) -> RunSummary:
        scenarios = [s for f in self.features for s in f.scenarios]
        return RunSummary(
            total=len(scenarios),
            passed=sum(1 for s in scenarios if s.passed),
            failed=sum(1 for s in scenarios if s.failed),
            errored=sum(1 for s in scenarios if s.errored),
            skipped=sum(1 for s in scenarios if s.skipped),
            manual=sum(1 for s in scenarios if s.is_manual),
            muted=sum(1 for s in scenarios if s.muted),
            untested=sum(1 for s in scenarios if s.untested),
        )

    @property
    def failed_scenarios(self) -> List[ScenarioResult]:
        """Assertion failures only, excluding muted."""
        return [s for f in self.features for s in f.failed_scenarios]

    @property
    def errored_scenarios(self) -> List[ScenarioResult]:
        """Unexpected exceptions only, excluding muted."""
        return [s for f in self.features for s in f.errored_scenarios]

    @property
    def muted_scenarios(self) -> List[ScenarioResult]:
        """Failed or errored scenarios silenced by @MUTE."""
        return [s for f in self.features for s in f.muted_scenarios]

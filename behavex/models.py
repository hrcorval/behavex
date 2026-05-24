# -*- coding: utf-8 -*-
"""Pydantic models for BehaveXRunner structured output."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

# Statuses BehaveX treats as execution failures (maps to HTML report "Failed" column).
_FAILED_STATUSES = frozenset({'failed', 'error'})


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
    def is_not_automated(self) -> bool:
        """@MANUAL or @WIP tag: scenario is not automated and never executes."""
        return 'MANUAL' in self.tags or 'WIP' in self.tags

    @property
    def passed(self) -> bool:
        return self.status == 'passed'

    @property
    def failed(self) -> bool:
        return self.status in _FAILED_STATUSES

    @property
    def skipped(self) -> bool:
        """Not executed for a runtime reason (conditional skip, --stop, undefined step).
        Excludes @MANUAL/@WIP scenarios which are counted separately as not_automated."""
        return self.status not in _FAILED_STATUSES and self.status != 'passed' and not self.is_not_automated

    @property
    def not_automated(self) -> bool:
        """@MANUAL or @WIP: appears in the report but is never executed."""
        return self.is_not_automated


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
        """All scenarios that broke (failed or error), including muted ones."""
        return [s for s in self.scenarios if s.status in _FAILED_STATUSES]


class RunSummary(BaseModel):
    model_config = ConfigDict(extra='ignore')

    total: int
    passed: int
    failed: int
    skipped: int
    not_automated: int = 0


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
        """Non-overlapping counts that always sum to total.

        passed + failed + skipped + not_automated == total
        """
        scenarios = [s for f in self.features for s in f.scenarios]
        return RunSummary(
            total=len(scenarios),
            passed=sum(1 for s in scenarios if s.passed),
            failed=sum(1 for s in scenarios if s.failed),
            skipped=sum(1 for s in scenarios if s.skipped),
            not_automated=sum(1 for s in scenarios if s.not_automated),
        )

    @property
    def failed_scenarios(self) -> List[ScenarioResult]:
        """All scenarios that broke (failed or error), including muted ones."""
        return [s for f in self.features for s in f.failed_scenarios]

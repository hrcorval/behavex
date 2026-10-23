# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator, model_validator

from behavex.outputs.report_utils import FAILED_STATUSES


class ProgressEvent(BaseModel):
    model_config = ConfigDict(extra='ignore')

    scenario_name: str
    feature_name: str
    status: str
    duration: float
    completed_count: int
    total: Optional[int] = None


class DiscoveredScenario(BaseModel):
    """A scenario run() would execute; fields match its ScenarioResult."""
    model_config = ConfigDict(extra='ignore')

    feature: str
    name: str
    filename: str
    line: int
    tags: List[str] = Field(default_factory=list)


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

    @field_validator('error_msg', mode='before')
    @classmethod
    def _error_msg_as_list(cls, value):
        # A crashed worker's skeleton reports a plain string, which the HTML and JUnit reports render as is
        return [value] if isinstance(value, str) else value

    @property
    def is_manual(self) -> bool:
        """@MANUAL or @WIP tag: scenario is not automated."""
        return 'MANUAL' in self.tags or 'WIP' in self.tags

    @property
    def passed(self) -> bool:
        return self.status == 'passed' and not self.is_manual

    @property
    def failed(self) -> bool:
        return self.status == 'failed' and not self.is_manual

    @property
    def errored(self) -> bool:
        return self.status == 'error' and not self.is_manual

    @property
    def skipped(self) -> bool:
        return self.status == 'skipped' and not self.is_manual

    @property
    def untested(self) -> bool:
        return self.status == 'untested' and not self.is_manual

    @property
    def manual(self) -> bool:
        return self.is_manual


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
        return [s for s in self.scenarios if s.status in FAILED_STATUSES]


class RunSummary(BaseModel):
    model_config = ConfigDict(extra='ignore')

    total: int
    passed: int
    failed: int
    error: int = 0
    skipped: int = 0
    untested: int = 0
    manual: int = 0


class RunResult(BaseModel):
    model_config = ConfigDict(extra='ignore')

    run_id: str
    exit_code: int
    output_folder: str
    features: List[FeatureResult] = Field(default_factory=list)
    stopped: bool = False

    @computed_field
    @property
    def passed(self) -> bool:
        return self.exit_code == 0 and not self.stopped

    @computed_field
    @property
    def summary(self) -> RunSummary:
        """Non-overlapping counts: passed + failed + error + skipped + untested + manual == total."""
        scenarios = [s for f in self.features for s in f.scenarios]
        return RunSummary(
            total=len(scenarios),
            passed=sum(1 for s in scenarios if s.passed),
            failed=sum(1 for s in scenarios if s.failed),
            error=sum(1 for s in scenarios if s.errored),
            skipped=sum(1 for s in scenarios if s.skipped),
            untested=sum(1 for s in scenarios if s.untested),
            manual=sum(1 for s in scenarios if s.manual),
        )

    @computed_field
    @property
    def failed_scenarios(self) -> List[ScenarioResult]:
        """All scenarios that broke (failed or error), including muted ones."""
        return [s for f in self.features for s in f.failed_scenarios]

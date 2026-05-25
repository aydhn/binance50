from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class WalkForwardMode(StrEnum):
    rolling_window = "rolling_window"
    expanding_window = "expanding_window"
    anchored_expanding = "anchored_expanding"


class WalkForwardWindowStatus(StrEnum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    skipped = "skipped"
    invalid = "invalid"


class WalkForwardSelectionSource(StrEnum):
    validation_only = "validation_only"
    validation_robust_score = "validation_robust_score"
    fixed_params = "fixed_params"
    invalid = "invalid"


class WalkForwardIntent(StrEnum):
    research_only = "research_only"
    no_order = "no_order"
    no_live = "no_live"
    no_paper = "no_paper"


class WalkForwardWindow(BaseModel):
    window_id: str
    index: int
    mode: WalkForwardMode
    train_start: int
    train_end: int
    validation_start: int
    validation_end: int
    test_start: int
    test_end: int
    train_rows: int
    validation_rows: int
    test_rows: int
    embargo_bars: int
    gaps: dict[str, int] = Field(default_factory=dict)
    status: WalkForwardWindowStatus = WalkForwardWindowStatus.pending
    metadata: dict[str, Any] = Field(default_factory=dict)


class WalkForwardWindowResult(BaseModel):
    window_id: str
    status: WalkForwardWindowStatus
    optimizer_result: Any | None = None
    selected_trial: Any | None = None
    selected_parameter_set: Any | None = None
    train_report: dict[str, Any] | None = None
    validation_report: dict[str, Any] | None = None
    oos_report: dict[str, Any] | None = None
    oos_backtest_result: Any | None = None
    overfit_report: dict[str, Any] | None = None
    robustness_report: dict[str, Any] | None = None
    degradation_report: dict[str, Any] | None = None
    parameter_drift_report: dict[str, Any] | None = None
    regime_report: dict[str, Any] | None = None
    started_at_utc: str | None = None
    finished_at_utc: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class WalkForwardRunRequest(BaseModel):
    symbol: str
    market_scope: str
    interval: str
    input_ohlcv_dataset_name: str
    mode: WalkForwardMode
    optimizer_method: str
    start_time_ms: int | None = None
    end_time_ms: int | None = None
    request_id: str
    correlation_id: str


class WalkForwardRunResult(BaseModel):
    request: WalkForwardRunRequest
    run_id: str
    mode: WalkForwardMode
    windows: list[WalkForwardWindow]
    window_results: dict[str, WalkForwardWindowResult]
    stitched_oos_equity: Any | None = None
    aggregate_oos_metrics: dict[str, Any] | None = None
    stability_report: dict[str, Any] | None = None
    degradation_summary: dict[str, Any] | None = None
    parameter_drift_summary: dict[str, Any] | None = None
    regime_summary: dict[str, Any] | None = None
    robustness_report: dict[str, Any] | None = None
    quality_report: dict[str, Any] | None = None
    report: dict[str, Any] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    success: bool
    error: str | None = None


class WalkForwardRunMetadata(BaseModel):
    run_id: str
    symbol: str
    market_scope: str
    interval: str
    mode: WalkForwardMode
    window_count: int
    completed_window_count: int
    failed_window_count: int
    skipped_window_count: int
    input_hash: str
    config_hash: str
    window_plan_hash: str
    output_hash: str
    generated_at_utc: str
    warnings: list[str] = Field(default_factory=list)

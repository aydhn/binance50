from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class OptimizationMethod(StrEnum):
    GRID = "grid"
    RANDOM = "random"
    OPTUNA_OPTIONAL = "optuna_optional"


class TrialStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED_BY_GUARD = "rejected_by_guard"
    INVALID = "invalid"


class OptimizationSplit(StrEnum):
    TRAIN = "train"
    VALIDATION = "validation"
    TEST = "test"
    FULL_REPORT_ONLY = "full_report_only"


class OptimizationIntent(StrEnum):
    RESEARCH_ONLY = "research_only"
    NO_ORDER = "no_order"
    NO_LIVE = "no_live"
    NO_PAPER = "no_paper"


class ParameterSpec(BaseModel):
    name: str
    path: str
    value_type: str
    values: list[Any] = Field(default_factory=list)
    min_value: float | int | None = None
    max_value: float | int | None = None
    step: float | int | None = None
    distribution: str | None = None
    description: str
    enabled: bool = True


class ParameterSet(BaseModel):
    parameter_set_id: str
    values: dict[str, Any]
    config_patch: dict[str, Any]
    complexity_score: float = 0.0
    hash: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class OptimizationTrial(BaseModel):
    trial_id: str
    run_id: str
    method: OptimizationMethod
    parameter_set: ParameterSet
    status: TrialStatus
    train_result: dict[str, Any] | None = None
    validation_result: dict[str, Any] | None = None
    test_result: dict[str, Any] | None = None
    objective_score: float | None = None
    robust_score: float | None = None
    overfit_report: dict[str, Any] | None = None
    robustness_report: dict[str, Any] | None = None
    started_at_utc: int
    finished_at_utc: int | None = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class OptimizationRunRequest(BaseModel):
    symbol: str
    market_scope: str
    interval: str
    input_ohlcv_dataset_name: str | None = None
    method: OptimizationMethod
    search_space_name: str | None = None
    start_time_ms: int | None = None
    end_time_ms: int | None = None
    max_trials: int | None = None
    request_id: str
    correlation_id: str | None = None


class OptimizationRunResult(BaseModel):
    request: OptimizationRunRequest
    run_id: str
    method: OptimizationMethod
    trials: list[OptimizationTrial]
    best_trial: OptimizationTrial | None = None
    ranked_trials: list[OptimizationTrial] = Field(default_factory=list)
    split_metadata: dict[str, Any] | None = None
    quality_report: dict[str, Any] | None = None
    report: dict[str, Any] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    success: bool
    error: str | None = None


class OptimizationRunMetadata(BaseModel):
    run_id: str
    symbol: str
    market_scope: str
    interval: str
    method: OptimizationMethod
    trial_count: int
    completed_trial_count: int
    failed_trial_count: int
    rejected_trial_count: int
    input_hash: str
    search_space_hash: str
    config_hash: str
    output_hash: str
    generated_at_utc: int
    warnings: list[str] = Field(default_factory=list)

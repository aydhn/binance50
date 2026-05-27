from enum import StrEnum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class MLInferenceStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    INVALID = "invalid"
    BLOCKED_BY_GUARD = "blocked_by_guard"

class MLInferenceMode(StrEnum):
    OFFLINE_BATCH = "offline_batch"

class MLInferenceIntent(StrEnum):
    RESEARCH_ONLY = "research_only"
    VALIDATION_ONLY = "validation_only"
    NO_ORDER = "no_order"
    NO_LIVE = "no_live"
    NO_PAPER = "no_paper"

class MLPredictionOutputType(StrEnum):
    CLASS_LABEL = "class_label"
    PROBABILITY = "probability"
    DECISION_SCORE = "decision_score"
    REGRESSION_VALUE_SKELETON = "regression_value_skeleton"

class MLSandboxOutputStatus(StrEnum):
    SANDBOX_ONLY = "sandbox_only"
    BLOCKED_FROM_SIGNAL = "blocked_from_signal"
    BLOCKED_FROM_RISK = "blocked_from_risk"
    BLOCKED_FROM_EXECUTION = "blocked_from_execution"
    INVALID = "invalid"

class MLInferenceRunRequest(BaseModel):
    symbol: str
    market_scope: str
    interval: str
    model_id: str
    dataset_id: str
    split_name: str
    start_time_ms: int
    end_time_ms: int
    request_id: str
    correlation_id: str

class MLModelLoadReport(BaseModel):
    model_id: str
    artifact_id: str
    trusted_artifact: bool
    artifact_hash_expected: str
    artifact_hash_actual: str
    hash_verified: bool
    environment_match: bool
    model_card_present: bool
    dataset_manifest_link_present: bool
    feature_schema_hash: str
    loaded_at_utc: str
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MLPredictionRow(BaseModel):
    prediction_id: str
    model_id: str
    dataset_id: str
    symbol: str
    market_scope: str
    interval: str
    open_time: str
    close_time: Optional[str] = None
    predicted_label: str
    predicted_class_index: int
    probabilities: Optional[Dict[str, float]] = None
    max_probability: Optional[float] = None
    confidence: Optional[float] = None
    decision_score: Optional[float] = None
    calibrated: Optional[bool] = None
    calibration_method: Optional[str] = None
    prediction_intent: MLInferenceIntent = MLInferenceIntent.RESEARCH_ONLY
    feature_schema_hash: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MLInferenceManifest(BaseModel):
    inference_id: str
    run_id: str
    model_id: str
    artifact_id: str
    dataset_id: str
    split_name: str
    row_count: int
    prediction_count: int
    feature_schema_hash: str
    model_hash: str
    dataset_hash: str
    preprocessor_hash: str
    config_hash: str
    output_hash: str
    calibration_status: str
    created_at_utc: str
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MLInferenceRunResult(BaseModel):
    request: MLInferenceRunRequest
    run_id: str
    status: MLInferenceStatus
    model_load_report: Optional[MLModelLoadReport] = None
    predictions: List[MLPredictionRow] = Field(default_factory=list)
    probability_report: Optional[Any] = None
    calibration_check_report: Optional[Any] = None
    threshold_sweep_report: Optional[Any] = None
    distribution_report: Optional[Any] = None
    drift_report: Optional[Any] = None
    sandbox_outputs: Optional[Any] = None
    manifest: Optional[MLInferenceManifest] = None
    quality_report: Optional[Any] = None
    reproducibility_report: Optional[Any] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    success: bool
    error: Optional[str] = None

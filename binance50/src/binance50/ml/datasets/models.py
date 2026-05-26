from datetime import datetime
from enum import StrEnum
from typing import Any

import pandas as pd
from pydantic import BaseModel, Field

from binance50.core.enums import MarketScope


class MLDatasetStatus(StrEnum):
    PENDING = "pending"
    BUILDING = "building"
    COMPLETED = "completed"
    FAILED = "failed"
    INVALID = "invalid"


class MLFeatureSource(StrEnum):
    INDICATORS_V1 = "indicators_v1"
    INDICATORS_V2 = "indicators_v2"
    SCORED_SIGNALS = "scored_signals"
    REGIMES = "regimes"
    RISK_ASSESSMENTS = "risk_assessments"
    STRATEGY_CANDIDATES = "strategy_candidates"
    BACKTEST_METADATA = "backtest_metadata"
    WALKFORWARD_METADATA = "walkforward_metadata"


class MLLabelType(StrEnum):
    FORWARD_RETURN_REGRESSION = "forward_return_regression"
    FORWARD_RETURN_CLASSIFICATION = "forward_return_classification"
    VOLATILITY_ADJUSTED_RETURN_CLASSIFICATION = "volatility_adjusted_return_classification"
    TRIPLE_BARRIER_SKELETON = "triple_barrier_skeleton"
    RANKING_SKELETON = "ranking_skeleton"


class MLSplitName(StrEnum):
    TRAIN = "train"
    VALIDATION = "validation"
    TEST = "test"
    TIME_SERIES_CV = "time_series_cv"
    WALKFORWARD_OOS_REFERENCE = "walkforward_oos_reference"


class MLDatasetIntent(StrEnum):
    RESEARCH_ONLY = "research_only"
    TRAINING_INPUT_CANDIDATE = "training_input_candidate"
    NO_ORDER = "no_order"
    NO_LIVE = "no_live"
    NO_PAPER = "no_paper"


class MLFeatureColumnMetadata(BaseModel):
    column_name: str
    source: str
    dtype: str
    group: str
    lookback_bars: int = 0
    is_mtf: bool = False
    is_regime: bool = False
    is_signal: bool = False
    is_risk: bool = False
    nan_ratio: float = 0.0
    inf_count: int = 0
    constant: bool = False
    allowed_for_training: bool = True
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MLLabelSpec(BaseModel):
    label_type: MLLabelType
    horizon_bars: int
    return_source: str = "close"
    threshold_pct: float = 0.0
    neutral_zone_pct: float = 0.0
    include_neutral_class: bool = True
    label_column: str
    future_return_column: str
    description: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class MLSplitMetadata(BaseModel):
    split_id: str
    split_method: str
    train_start: datetime | str
    train_end: datetime | str
    validation_start: datetime | str | None = None
    validation_end: datetime | str | None = None
    test_start: datetime | str | None = None
    test_end: datetime | str | None = None
    train_rows: int = 0
    validation_rows: int = 0
    test_rows: int = 0
    embargo_bars: int = 0
    purge_overlapping_labels: bool = False
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MLPreprocessorMetadata(BaseModel):
    preprocessor_id: str
    scaler: str
    imputation_strategy: str
    clipping_method: str
    fit_split: str
    fitted_columns: list[str] = Field(default_factory=list)
    parameters: dict[str, Any] = Field(default_factory=dict)
    fitted_at_utc: datetime | str
    hash: str
    warnings: list[str] = Field(default_factory=list)


class MLDatasetManifest(BaseModel):
    dataset_id: str
    dataset_version: int
    symbol: str
    market_scope: str
    interval: str
    row_count: int
    feature_count: int
    label_count: int
    feature_columns: list[str] = Field(default_factory=list)
    label_columns: list[str] = Field(default_factory=list)
    feature_metadata: list[MLFeatureColumnMetadata] = Field(default_factory=list)
    label_specs: list[MLLabelSpec] = Field(default_factory=list)
    split_metadata: MLSplitMetadata | None = None
    preprocessor_metadata: MLPreprocessorMetadata | None = None
    input_hashes: dict[str, str] = Field(default_factory=dict)
    dataset_hash: str
    config_hash: str
    leakage_report_hash: str = ""
    quality_status: str = "pending"
    created_at_utc: datetime | str
    warnings: list[str] = Field(default_factory=list)


class MLDatasetBuildRequest(BaseModel):
    symbol: str
    market_scope: MarketScope
    interval: str
    input_feature_dataset_names: list[str] = Field(default_factory=list)
    label_specs: list[MLLabelSpec] = Field(default_factory=list)
    start_time_ms: int | None = None
    end_time_ms: int | None = None
    request_id: str
    correlation_id: str = ""


class MLDatasetBuildResult(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    request: MLDatasetBuildRequest
    status: MLDatasetStatus
    features_df: pd.DataFrame | None = None
    labels_df: pd.DataFrame | None = None
    dataset_df: pd.DataFrame | None = None
    manifest: MLDatasetManifest | None = None
    split_metadata: MLSplitMetadata | None = None
    quality_report: Any | None = None
    leakage_report: Any | None = None
    preprocessing_report: Any | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    success: bool = False
    error: str | None = None

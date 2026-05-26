import re

with open("binance50/src/binance50/config/models.py", "r") as f:
    content = f.read()

models_to_add = """
class MLDatasetSourceConfig(BaseModel):
    use_indicator_v1: bool = True
    use_indicator_v2: bool = True
    use_strategy_candidates: bool = False
    use_scored_signals: bool = True
    use_regimes: bool = True
    use_risk_assessments: bool = True
    use_backtest_metadata: bool = False
    use_walkforward_metadata: bool = False
    require_source_hashes: bool = True
    require_source_timestamps: bool = True

class MLFeatureSelectionConfig(BaseModel):
    enabled: bool = True
    include_prefixes: list[str] = Field(default_factory=list)
    exclude_prefixes: list[str] = Field(default_factory=list)
    required_base_columns: list[str] = Field(default_factory=list)
    max_feature_columns: int = 1500
    min_feature_columns: int = 10
    reject_all_nan_features: bool = True
    reject_constant_features: bool = False
    warn_constant_features: bool = True
    max_nan_ratio_per_feature: float = Field(default=0.40, ge=0.0, le=1.0)
    max_inf_count: int = 0
    allow_object_features: bool = False
    allow_boolean_features: bool = True
    allow_categorical_features: bool = True
    categorical_encoding_deferred: bool = True

    @model_validator(mode="after")
    def validate_feature_counts(self) -> "MLFeatureSelectionConfig":
        if self.max_feature_columns <= self.min_feature_columns:
            raise ValueError("max_feature_columns must be > min_feature_columns")
        return self

class MLLabelTripleBarrierConfig(BaseModel):
    enabled: bool = False
    profit_take_pct: float = 1.0
    stop_loss_pct: float = 0.5
    max_holding_bars: int = 20
    full_engine_deferred: bool = True

class MLLabelConfig(BaseModel):
    enabled: bool = True
    default_label_type: str = "forward_return_classification"
    allowed_label_types: list[str] = Field(default_factory=list)
    horizons_bars: list[int] = Field(default_factory=list)
    default_horizon_bars: int = 5
    return_source: str = "close"
    classification_threshold_pct: float = Field(default=0.20, ge=0.0)
    neutral_zone_pct: float = Field(default=0.05, ge=0.0)
    include_neutral_class: bool = True
    label_column_prefix: str = "label_"
    future_return_column_prefix: str = "label_future_return_"
    allow_label_columns_in_features: bool = False
    drop_rows_without_label: bool = True
    drop_last_horizon_rows: bool = True
    triple_barrier: MLLabelTripleBarrierConfig = Field(default_factory=MLLabelTripleBarrierConfig)

    @model_validator(mode="after")
    def validate_horizons(self) -> "MLLabelConfig":
        for h in self.horizons_bars:
            if h <= 0:
                raise ValueError("all horizons must be > 0")
        if self.default_horizon_bars not in self.horizons_bars:
            raise ValueError("default_horizon_bars must be in horizons_bars")
        if self.allow_label_columns_in_features:
            raise ValueError("allow_label_columns_in_features must be False")
        if not self.drop_last_horizon_rows:
            raise ValueError("drop_last_horizon_rows must be True")
        return self

class MLSplitConfig(BaseModel):
    enabled: bool = True
    split_method: str = "chronological"
    train_pct: float = Field(default=0.60, ge=0.0, le=1.0)
    validation_pct: float = Field(default=0.20, ge=0.0, le=1.0)
    test_pct: float = Field(default=0.20, ge=0.0, le=1.0)
    min_train_rows: int = 500
    min_validation_rows: int = 200
    min_test_rows: int = 200
    time_series_cv_enabled: bool = True
    time_series_cv_splits: int = 3
    embargo_bars: int = 0
    purge_overlapping_labels: bool = True
    test_set_for_final_report_only: bool = True
    reject_split_overlap: bool = True
    reject_test_selection: bool = True

    @model_validator(mode="after")
    def validate_split_pcts(self) -> "MLSplitConfig":
        if abs(self.train_pct + self.validation_pct + self.test_pct - 1.0) > 1e-6:
            raise ValueError("train_pct + validation_pct + test_pct must equal 1.0")
        return self

class MLPreprocessingImputationConfig(BaseModel):
    enabled: bool = True
    strategy: str = "median_train_only"
    allow_bfill: bool = False
    allow_ffill: bool = True
    fit_imputer_train_only: bool = True

    @model_validator(mode="after")
    def validate_imputation(self) -> "MLPreprocessingImputationConfig":
        if self.allow_bfill:
            raise ValueError("allow_bfill must be False")
        return self

class MLPreprocessingClippingConfig(BaseModel):
    enabled: bool = True
    method: str = "train_quantile"
    lower_quantile: float = Field(default=0.001, ge=0.0, le=0.5)
    upper_quantile: float = Field(default=0.999, ge=0.5, le=1.0)
    fit_clipper_train_only: bool = True

class MLPreprocessingCategoricalConfig(BaseModel):
    enabled: bool = False
    encoding_deferred: bool = True

class MLPreprocessingConfig(BaseModel):
    enabled: bool = True
    fit_transform_train_only: bool = True
    transform_validation_test_only: bool = True
    scaler: str = "standard"
    allowed_scalers: list[str] = Field(default_factory=list)
    imputation: MLPreprocessingImputationConfig = Field(default_factory=MLPreprocessingImputationConfig)
    clipping: MLPreprocessingClippingConfig = Field(default_factory=MLPreprocessingClippingConfig)
    categorical: MLPreprocessingCategoricalConfig = Field(default_factory=MLPreprocessingCategoricalConfig)
    persist_preprocessor: bool = True
    preprocessor_registry_enabled: bool = True

    @model_validator(mode="after")
    def validate_preprocessing(self) -> "MLPreprocessingConfig":
        if not self.fit_transform_train_only:
            raise ValueError("fit_transform_train_only must be True")
        if not self.transform_validation_test_only:
            raise ValueError("transform_validation_test_only must be True")
        return self

class MLAlignmentConfig(BaseModel):
    enabled: bool = True
    method: str = "backward_asof"
    reject_forward_alignment: bool = True
    reject_nearest_alignment: bool = True
    require_no_future_join: bool = True
    tolerance_bars: int = 1
    require_closed_candles: bool = True

    @model_validator(mode="after")
    def validate_alignment(self) -> "MLAlignmentConfig":
        if not self.reject_forward_alignment:
            raise ValueError("reject_forward_alignment must be True")
        if not self.reject_nearest_alignment:
            raise ValueError("reject_nearest_alignment must be True")
        return self

class MLLeakageConfig(BaseModel):
    prevent_lookahead_bias: bool = True
    reject_future_columns_in_features: bool = True
    reject_target_columns_in_features: bool = True
    reject_label_columns_in_features: bool = True
    reject_next_columns_in_features: bool = True
    reject_forward_columns_in_features: bool = True
    reject_negative_shift_features: bool = True
    allow_forward_shift_only_for_labels: bool = True
    reject_global_scaler_fit: bool = True
    reject_global_imputer_fit: bool = True
    reject_global_clipper_fit: bool = True
    reject_test_fit: bool = True
    reject_validation_fit: bool = True
    reject_same_bar_label_as_feature: bool = True

    @model_validator(mode="after")
    def validate_leakage(self) -> "MLLeakageConfig":
        if not self.reject_global_scaler_fit:
            raise ValueError("reject_global_scaler_fit must be True")
        if not self.reject_test_fit:
            raise ValueError("reject_test_fit must be True")
        if not self.reject_validation_fit:
            raise ValueError("reject_validation_fit must be True")
        return self


class MLQualityConfig(BaseModel):
    reject_empty_dataset: bool = True
    reject_missing_labels: bool = True
    reject_missing_features: bool = True
    reject_single_class_labels: bool = False
    warn_single_class_labels: bool = True
    warn_class_imbalance: bool = True
    max_majority_class_ratio: float = Field(default=0.85, ge=0.5, le=1.0)
    reject_nan_inf_features: bool = True
    reject_nan_inf_labels: bool = True
    reject_missing_split_metadata: bool = True
    reject_missing_hashes: bool = True
    reject_leakage_warnings: bool = True
    warn_low_row_count: bool = True
    min_total_rows_warning: int = 1000

class MLDatasetConfig(BaseModel):
    enabled: bool = True
    output_dataset_name: str = "ml_datasets"
    cache_enabled: bool = True
    cache_dir: str = "data/ml/datasets/cache"
    export_dir: str = "data/ml/datasets/exports"
    registry_dir: str = "data/ml/datasets/registry"

    real_exchange_forbidden: bool = True
    paper_trade_forbidden: bool = True
    live_trade_forbidden: bool = True
    order_creation_forbidden: bool = True
    api_key_forbidden: bool = True
    signed_request_forbidden: bool = True
    dashboard_forbidden: bool = True
    model_training_deferred: bool = True
    prediction_deferred: bool = True

    sources: MLDatasetSourceConfig = Field(default_factory=MLDatasetSourceConfig)
    feature_selection: MLFeatureSelectionConfig = Field(default_factory=MLFeatureSelectionConfig)
    labels: MLLabelConfig = Field(default_factory=MLLabelConfig)
    splits: MLSplitConfig = Field(default_factory=MLSplitConfig)
    preprocessing: MLPreprocessingConfig = Field(default_factory=MLPreprocessingConfig)
    alignment: MLAlignmentConfig = Field(default_factory=MLAlignmentConfig)
    leakage: MLLeakageConfig = Field(default_factory=MLLeakageConfig)
    quality: MLQualityConfig = Field(default_factory=MLQualityConfig)

    @model_validator(mode="after")
    def validate_safety_flags(self) -> "MLDatasetConfig":
        if not self.real_exchange_forbidden:
            raise ValueError("real_exchange_forbidden must be True")
        if not self.paper_trade_forbidden:
            raise ValueError("paper_trade_forbidden must be True")
        if not self.live_trade_forbidden:
            raise ValueError("live_trade_forbidden must be True")
        if not self.order_creation_forbidden:
            raise ValueError("order_creation_forbidden must be True")
        if not self.api_key_forbidden:
            raise ValueError("api_key_forbidden must be True")
        if not self.signed_request_forbidden:
            raise ValueError("signed_request_forbidden must be True")
        if not self.dashboard_forbidden:
            raise ValueError("dashboard_forbidden must be True")
        if not self.model_training_deferred:
            raise ValueError("model_training_deferred must be True")
        if not self.prediction_deferred:
            raise ValueError("prediction_deferred must be True")
        if not re.match(r"^[a-zA-Z0-9_-]+$", self.output_dataset_name):
            raise ValueError("output_dataset_name is not safe")
        return self

class AppConfig(BaseModel):
"""

content = content.replace("class AppConfig(BaseModel):", models_to_add)

content = content.replace("    walkforward: WalkforwardConfig = Field(default_factory=WalkforwardConfig)", "    walkforward: WalkforwardConfig = Field(default_factory=WalkforwardConfig)\n    ml_dataset: MLDatasetConfig = Field(default_factory=MLDatasetConfig)")

with open("binance50/src/binance50/config/models.py", "w") as f:
    f.write(content)

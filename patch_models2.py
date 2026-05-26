import re
with open("binance50/src/binance50/config/models.py", "r") as f:
    content = f.read()

models_to_add = """class MLTrainingDatasetConfig(BaseModel):
    require_ml_dataset_manifest: bool = True
    require_leakage_free_dataset: bool = True
    require_quality_passed_dataset: bool = True
    allowed_label_types: list[str] = Field(default_factory=list)
    default_label_column: str = "label_forward_return_classification_5"
    require_split_metadata: bool = True
    require_preprocessor_metadata: bool = True
    reject_if_feature_contains_label: bool = True
    reject_if_feature_contains_future: bool = True
    reject_if_feature_contains_target: bool = True
    reject_if_missing_train_validation_test: bool = True

class MLTrainingTaskConfig(BaseModel):
    default_task_type: str = "classification"
    allowed_task_types: list[str] = Field(default_factory=list)
    multiclass_enabled: bool = True
    binary_enabled: bool = True
    regression_default_enabled: bool = False
    ranking_deferred: bool = True

class MLLogisticRegressionConfig(BaseModel):
    enabled: bool = True
    max_iter: int = 1000
    class_weight: str = "balanced"
    solver: str = "lbfgs"
    C: float = 1.0

class MLRandomForestClassifierConfig(BaseModel):
    enabled: bool = True
    n_estimators: int = 200
    max_depth: int = 6
    min_samples_leaf: int = 20
    class_weight: str = "balanced_subsample"
    random_state: int = 42
    n_jobs: int = 1

class MLHistGradientBoostingConfig(BaseModel):
    enabled: bool = True
    max_iter: int = 200
    max_leaf_nodes: int = 31
    learning_rate: float = 0.05
    l2_regularization: float = 0.0
    random_state: int = 42

class MLDummyClassifierConfig(BaseModel):
    enabled: bool = True
    strategy: str = "most_frequent"

class MLTrainingModelsConfig(BaseModel):
    enabled_models: list[str] = Field(default_factory=list)
    default_model: str = "logistic_regression"
    allow_regression_skeletons: bool = True
    random_state: int = 42
    n_jobs: int = 1
    max_fit_seconds_per_model: int = 300
    max_models_per_run: int = Field(default=10, ge=1, le=50)
    allow_gpu: bool = False
    require_deterministic_models: bool = True

    logistic_regression: MLLogisticRegressionConfig = Field(default_factory=MLLogisticRegressionConfig)
    random_forest_classifier: MLRandomForestClassifierConfig = Field(default_factory=MLRandomForestClassifierConfig)
    hist_gradient_boosting_classifier: MLHistGradientBoostingConfig = Field(default_factory=MLHistGradientBoostingConfig)
    dummy_classifier: MLDummyClassifierConfig = Field(default_factory=MLDummyClassifierConfig)

class MLTrainingValidationConfig(BaseModel):
    enabled: bool = True
    method: str = "time_series_split"
    use_existing_ml_splits: bool = True
    train_split_name: str = "train"
    validation_split_name: str = "validation"
    test_split_name: str = "test"
    time_series_cv_enabled: bool = True
    time_series_cv_splits: int = 3
    test_set_final_report_only: bool = True
    reject_test_selection: bool = True
    reject_split_overlap: bool = True
    require_chronological_order: bool = True
    min_train_rows: int = 500
    min_validation_rows: int = 200
    min_test_rows: int = 200
    min_class_count_per_split: int = 2
    min_samples_per_class_warning: int = 25

class MLCalibrationConfig(BaseModel):
    enabled: bool = True
    calibrate_classifiers: bool = True
    method: str = "sigmoid"
    allowed_methods: list[str] = Field(default_factory=list)
    calibration_split: str = "validation"
    fit_calibrator_on_test_forbidden: bool = True
    require_calibration_report: bool = True
    reliability_bins: int = Field(default=10, ge=2, le=50)
    compute_brier_score: bool = True
    compute_expected_calibration_error: bool = True
    warn_uncalibrated_probabilities: bool = True
    isotonic_min_samples_warning: int = 1000

class MLClassificationMetricsConfig(BaseModel):
    compute_accuracy: bool = True
    compute_balanced_accuracy: bool = True
    compute_precision_recall_f1: bool = True
    compute_roc_auc: bool = True
    compute_pr_auc: bool = True
    compute_log_loss: bool = True
    compute_brier_score: bool = True
    compute_confusion_matrix: bool = True
    compute_classification_report: bool = True
    average: str = "weighted"
    zero_division: int = 0

class MLRegressionMetricsConfig(BaseModel):
    compute_mae: bool = True
    compute_rmse: bool = True
    compute_r2: bool = True
    compute_directional_accuracy: bool = True
    regression_deferred: bool = True

class MLTrainingMetricsConfig(BaseModel):
    classification: MLClassificationMetricsConfig = Field(default_factory=MLClassificationMetricsConfig)
    regression: MLRegressionMetricsConfig = Field(default_factory=MLRegressionMetricsConfig)

class MLFeatureImportanceConfig(BaseModel):
    enabled: bool = True
    native_model_importance: bool = True
    permutation_importance: bool = True
    permutation_n_repeats: int = 5
    permutation_random_state: int = 42
    permutation_split: str = "validation"
    max_features_reported: int = Field(default=100, ge=1, le=1000)
    warn_high_cardinality_importance_bias: bool = True

class MLTrainingOverfitConfig(BaseModel):
    enabled: bool = True
    compare_train_validation: bool = True
    max_train_validation_metric_gap: float = 0.25
    max_train_validation_auc_gap: float = 0.20
    warn_if_train_much_better: bool = True
    reject_if_validation_worse_than_dummy: bool = False
    warn_if_validation_worse_than_dummy: bool = True
    warn_if_test_much_worse_than_validation: bool = True
    test_degradation_warning_gap: float = 0.20

class MLModelRegistryConfig(BaseModel):
    enabled: bool = True
    active_model_serving_forbidden: bool = True
    auto_promote_forbidden: bool = True
    require_model_card: bool = True
    require_training_manifest: bool = True
    require_dataset_manifest_link: bool = True
    require_reproducibility_hashes: bool = True
    persist_model_artifacts: bool = True
    artifact_format: str = "joblib"
    persist_pickled_objects_warning: bool = True
    allow_loading_untrusted_artifacts: bool = False

class MLTrainingQualityConfig(BaseModel):
    reject_no_models_trained: bool = True
    reject_all_models_failed: bool = True
    reject_missing_metrics: bool = True
    reject_missing_calibration_report: bool = False
    reject_missing_model_card: bool = True
    reject_missing_dataset_manifest: bool = True
    reject_missing_hashes: bool = True
    reject_nan_inf_metrics: bool = True
    warn_low_sample_count: bool = True
    warn_class_imbalance: bool = True
    warn_single_class_split: bool = True
    reject_single_class_train: bool = True
    reject_single_class_validation: bool = False
    warn_uncalibrated_model: bool = True
    reject_live_or_paper_intent: bool = True

class MLTrainingConfig(BaseModel):
    enabled: bool = True
    output_dataset_name: str = "ml_training_runs"
    cache_enabled: bool = True
    cache_dir: str = "data/ml/training/cache"
    export_dir: str = "data/ml/training/exports"
    registry_dir: str = "data/ml/training/registry"
    artifacts_dir: str = "data/ml/training/artifacts"
    reports_dir: str = "data/ml/training/reports"

    real_exchange_forbidden: bool = True
    paper_trade_forbidden: bool = True
    live_trade_forbidden: bool = True
    order_creation_forbidden: bool = True
    api_key_forbidden: bool = True
    signed_request_forbidden: bool = True
    dashboard_forbidden: bool = True
    prediction_serving_deferred: bool = True
    execution_integration_forbidden: bool = True
    auto_strategy_update_forbidden: bool = True

    dataset: MLTrainingDatasetConfig = Field(default_factory=MLTrainingDatasetConfig)
    task: MLTrainingTaskConfig = Field(default_factory=MLTrainingTaskConfig)
    models: MLTrainingModelsConfig = Field(default_factory=MLTrainingModelsConfig)
    validation: MLTrainingValidationConfig = Field(default_factory=MLTrainingValidationConfig)
    calibration: MLCalibrationConfig = Field(default_factory=MLCalibrationConfig)
    metrics: MLTrainingMetricsConfig = Field(default_factory=MLTrainingMetricsConfig)
    feature_importance: MLFeatureImportanceConfig = Field(default_factory=MLFeatureImportanceConfig)
    overfit: MLTrainingOverfitConfig = Field(default_factory=MLTrainingOverfitConfig)
    registry: MLModelRegistryConfig = Field(default_factory=MLModelRegistryConfig)
    quality: MLTrainingQualityConfig = Field(default_factory=MLTrainingQualityConfig)

    @model_validator(mode="after")
    def validate_safety_flags(self) -> "MLTrainingConfig":
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
        if not self.prediction_serving_deferred:
            raise ValueError("prediction_serving_deferred must be True")
        if not self.execution_integration_forbidden:
            raise ValueError("execution_integration_forbidden must be True")
        if not self.auto_strategy_update_forbidden:
            raise ValueError("auto_strategy_update_forbidden must be True")

        if not self.dataset.require_ml_dataset_manifest:
            raise ValueError("require_ml_dataset_manifest must be True")
        if not self.dataset.require_leakage_free_dataset:
            raise ValueError("require_leakage_free_dataset must be True")
        if not self.dataset.require_quality_passed_dataset:
            raise ValueError("require_quality_passed_dataset must be True")

        if not self.validation.reject_test_selection:
            raise ValueError("reject_test_selection must be True")
        if not self.calibration.fit_calibrator_on_test_forbidden:
            raise ValueError("fit_calibrator_on_test_forbidden must be True")

        if not self.registry.active_model_serving_forbidden:
            raise ValueError("active_model_serving_forbidden must be True")
        if not self.registry.auto_promote_forbidden:
            raise ValueError("auto_promote_forbidden must be True")
        if self.registry.allow_loading_untrusted_artifacts:
            raise ValueError("allow_loading_untrusted_artifacts must be False")

        if not re.match(r"^[a-zA-Z0-9_-]+$", self.output_dataset_name):
            raise ValueError("output_dataset_name is not safe")

        return self

class AppConfig(BaseModel):
"""

content = content.replace("class AppConfig(BaseModel):", models_to_add)

content = content.replace("    ml_dataset: MLDatasetConfig = Field(default_factory=MLDatasetConfig)", "    ml_dataset: MLDatasetConfig = Field(default_factory=MLDatasetConfig)\n    ml_training: MLTrainingConfig = Field(default_factory=MLTrainingConfig)")

with open("binance50/src/binance50/config/models.py", "w") as f:
    f.write(content)

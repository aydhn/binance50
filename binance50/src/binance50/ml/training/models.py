from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List

class MLTaskType(str, Enum):
    classification = "classification"
    regression_skeleton = "regression_skeleton"

class MLModelType(str, Enum):
    dummy_classifier = "dummy_classifier"
    logistic_regression = "logistic_regression"
    random_forest_classifier = "random_forest_classifier"
    hist_gradient_boosting_classifier = "hist_gradient_boosting_classifier"
    dummy_regressor = "dummy_regressor"
    ridge_regressor_skeleton = "ridge_regressor_skeleton"
    random_forest_regressor_skeleton = "random_forest_regressor_skeleton"

class MLTrainingStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    invalid = "invalid"

class MLModelStatus(str, Enum):
    trained = "trained"
    failed = "failed"
    skipped = "skipped"
    invalid = "invalid"

class MLPredictionIntent(str, Enum):
    research_only = "research_only"
    validation_only = "validation_only"
    no_order = "no_order"
    no_live = "no_live"
    no_paper = "no_paper"

class MLTrainingRunRequest(BaseModel):
    symbol: str
    market_scope: str
    interval: str
    dataset_id: str
    label_column: str
    task_type: MLTaskType
    model_names: List[str]
    start_time_ms: int
    end_time_ms: int
    request_id: str
    correlation_id: str

class MLModelArtifactMetadata(BaseModel):
    artifact_id: str
    model_id: str
    run_id: str
    model_name: str
    artifact_format: str
    artifact_path: str
    artifact_hash: str
    estimator_class: str
    sklearn_version: str
    python_version: str
    feature_columns_hash: str
    dataset_id: str
    dataset_hash: str
    config_hash: str
    created_at_utc: str
    trusted_artifact: bool
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MLModelCard(BaseModel):
    model_id: str
    model_name: str
    task_type: str
    dataset_id: str
    label_column: str
    intended_use: str
    not_intended_use: str
    training_period: str
    validation_period: str
    test_period: str
    metrics_summary: Dict[str, Any]
    calibration_summary: Dict[str, Any]
    feature_importance_summary: Dict[str, Any]
    limitations: List[str]
    risks: List[str]
    leakage_checks: Dict[str, bool]
    reproducibility_hashes: Dict[str, str]
    created_at_utc: str
    warnings: List[str] = Field(default_factory=list)

class MLCalibrationReport(BaseModel):
    model_id: str
    method: str
    calibrated: bool
    calibration_split: str
    brier_score_before: Optional[float] = None
    brier_score_after: Optional[float] = None
    ece_before: Optional[float] = None
    ece_after: Optional[float] = None
    reliability_bins: List[Dict[str, float]] = Field(default_factory=list)
    calibration_curve_points: List[Dict[str, float]] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MLFeatureImportanceReport(BaseModel):
    model_id: str
    method: str
    split: str
    top_features: List[Dict[str, Any]]
    raw_importances: Dict[str, float]
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MLModelOverfitReport(BaseModel):
    model_id: str
    train_validation_metric_gap: Optional[float] = None
    train_validation_auc_gap: Optional[float] = None
    validation_test_gap: Optional[float] = None
    validation_vs_dummy_gap: Optional[float] = None
    overfit_risk_level: str
    worse_than_dummy_warning: bool
    train_much_better_warning: bool
    test_degradation_warning: bool
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MLClassificationMetrics(BaseModel):
    accuracy: float
    balanced_accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: Optional[float] = None
    pr_auc: Optional[float] = None
    log_loss: Optional[float] = None
    brier_score: Optional[float] = None
    confusion_matrix: List[List[int]]
    class_distribution: Dict[str, int]
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MLRegressionMetrics(BaseModel):
    mae: float
    rmse: float
    r2: float
    directional_accuracy: Optional[float] = None
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MLModelTrainingResult(BaseModel):
    model_id: str
    run_id: str
    model_name: str
    model_type: MLModelType
    status: MLModelStatus
    task_type: MLTaskType
    train_metrics: Optional[Dict[str, Any]] = None
    validation_metrics: Optional[Dict[str, Any]] = None
    test_metrics: Optional[Dict[str, Any]] = None
    calibration_report: Optional[MLCalibrationReport] = None
    feature_importance_report: Optional[MLFeatureImportanceReport] = None
    overfit_report: Optional[MLModelOverfitReport] = None
    artifact_metadata: Optional[MLModelArtifactMetadata] = None
    model_card: Optional[MLModelCard] = None
    started_at_utc: str
    finished_at_utc: str
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MLTrainingRunMetadata(BaseModel):
    run_id: str
    symbol: str
    market_scope: str
    interval: str
    dataset_id: str
    label_column: str
    task_type: MLTaskType
    model_count: int
    trained_model_count: int
    failed_model_count: int
    input_hash: str
    dataset_hash: str
    config_hash: str
    output_hash: str
    generated_at_utc: str
    warnings: List[str] = Field(default_factory=list)

class MLTrainingQualityIssue(BaseModel):
    issue_type: str
    severity: str
    model_id: Optional[str] = None
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MLTrainingQualityReport(BaseModel):
    status: str
    run_id: str
    model_count: int
    trained_model_count: int
    failed_model_count: int
    missing_metrics_count: int
    missing_calibration_count: int
    missing_model_card_count: int
    missing_dataset_manifest_count: int
    missing_hash_count: int
    nan_inf_metric_count: int
    single_class_train_count: int
    class_imbalance_warning_count: int
    uncalibrated_model_warning_count: int
    live_or_paper_intent_count: int
    issues: List[MLTrainingQualityIssue] = Field(default_factory=list)
    generated_at_utc: str

class MLTrainingRunResult(BaseModel):
    request: MLTrainingRunRequest
    run_id: str
    status: MLTrainingStatus
    dataset_manifest: Dict[str, Any]
    model_results: List[MLModelTrainingResult] = Field(default_factory=list)
    best_validation_model: Optional[str] = None
    quality_report: Optional[MLTrainingQualityReport] = None
    registry_report: Optional[Dict[str, Any]] = None
    reproducibility_report: Optional[Dict[str, Any]] = None
    metadata: MLTrainingRunMetadata
    success: bool
    error: Optional[str] = None

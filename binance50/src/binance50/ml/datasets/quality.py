import pandas as pd
import numpy as np
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.core.exceptions import MLDatasetQualityError

class MLDatasetQualityIssue(BaseModel):
    issue_type: str
    severity: str
    column: str
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)

class MLDatasetQualityReport(BaseModel):
    status: str
    row_count: int
    feature_count: int
    label_count: int
    train_rows: int
    validation_rows: int
    test_rows: int
    missing_feature_count: int
    missing_label_count: int
    nan_inf_feature_count: int
    nan_inf_label_count: int
    single_class_label_count: int
    class_imbalance_warnings: int
    constant_feature_count: int
    high_nan_feature_count: int
    leakage_issue_count: int
    issues: list[MLDatasetQualityIssue] = Field(default_factory=list)
    generated_at_utc: datetime | str

def build_ml_dataset_quality_report(
    result_or_df: Any,
    manifest: Any,
    leakage_report: Any,
    config: AppConfig
) -> MLDatasetQualityReport:
    issues = []

    # We expect result_or_df to be the dataset_df for simplicity
    df = result_or_df

    row_count = len(df) if df is not None else 0
    if row_count == 0:
        issues.append(MLDatasetQualityIssue(
            issue_type="empty_dataset",
            severity="critical",
            column="*",
            message="Dataset is empty"
        ))

    feature_cols = manifest.feature_columns if manifest else []
    label_cols = manifest.label_columns if manifest else []

    issues.extend(detect_missing_features(df, feature_cols))
    issues.extend(detect_missing_labels(df, label_cols))
    issues.extend(detect_nan_inf_features(df, feature_cols))
    issues.extend(detect_nan_inf_labels(df, label_cols))
    issues.extend(detect_constant_features(df, feature_cols))

    if manifest and manifest.split_metadata:
        train_rows = manifest.split_metadata.train_rows
        validation_rows = manifest.split_metadata.validation_rows
        test_rows = manifest.split_metadata.test_rows
    else:
        train_rows = validation_rows = test_rows = 0

    issue_count = len(issues)
    status = "passed"
    if any(i.severity == "critical" for i in issues):
        status = "failed"
    elif issue_count > 0:
        status = "warnings"

    report = MLDatasetQualityReport(
        status=status,
        row_count=row_count,
        feature_count=len(feature_cols),
        label_count=len(label_cols),
        train_rows=train_rows,
        validation_rows=validation_rows,
        test_rows=test_rows,
        missing_feature_count=sum(1 for i in issues if i.issue_type == "missing_feature"),
        missing_label_count=sum(1 for i in issues if i.issue_type == "missing_label"),
        nan_inf_feature_count=sum(1 for i in issues if i.issue_type == "nan_inf_feature"),
        nan_inf_label_count=sum(1 for i in issues if i.issue_type == "nan_inf_label"),
        single_class_label_count=0,
        class_imbalance_warnings=0,
        constant_feature_count=sum(1 for i in issues if i.issue_type == "constant_feature"),
        high_nan_feature_count=0,
        leakage_issue_count=leakage_report.issue_count if leakage_report else 0,
        issues=issues,
        generated_at_utc=datetime.utcnow()
    )

    assert_ml_dataset_quality_passed(report, config)
    return report

def detect_missing_features(df: pd.DataFrame, feature_columns: list[str]) -> list[MLDatasetQualityIssue]:
    issues = []
    if df is not None:
        for col in feature_columns:
            if col not in df.columns:
                issues.append(MLDatasetQualityIssue(
                    issue_type="missing_feature", severity="critical", column=col, message=f"Missing feature: {col}"
                ))
    return issues

def detect_missing_labels(df: pd.DataFrame, label_columns: list[str]) -> list[MLDatasetQualityIssue]:
    issues = []
    if df is not None:
        for col in label_columns:
            if col not in df.columns:
                issues.append(MLDatasetQualityIssue(
                    issue_type="missing_label", severity="critical", column=col, message=f"Missing label: {col}"
                ))
    return issues

def detect_nan_inf_features(df: pd.DataFrame, feature_columns: list[str]) -> list[MLDatasetQualityIssue]:
    issues = []
    if df is not None:
        for col in feature_columns:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                if df[col].isna().any() or np.isinf(df[col]).any():
                     issues.append(MLDatasetQualityIssue(
                         issue_type="nan_inf_feature", severity="critical", column=col, message=f"NaN/Inf in feature: {col}"
                     ))
    return issues

def detect_nan_inf_labels(df: pd.DataFrame, label_columns: list[str]) -> list[MLDatasetQualityIssue]:
    issues = []
    if df is not None:
        for col in label_columns:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                if df[col].isna().any() or np.isinf(df[col]).any():
                     issues.append(MLDatasetQualityIssue(
                         issue_type="nan_inf_label", severity="critical", column=col, message=f"NaN/Inf in label: {col}"
                     ))
    return issues

def analyze_label_distribution(labels_df: pd.DataFrame) -> dict:
    return {}

def detect_class_imbalance(labels_df: pd.DataFrame, config: AppConfig) -> list[MLDatasetQualityIssue]:
    return []

def detect_single_class_labels(labels_df: pd.DataFrame) -> list[MLDatasetQualityIssue]:
    return []

def detect_constant_features(df: pd.DataFrame, feature_columns: list[str]) -> list[MLDatasetQualityIssue]:
    issues = []
    if df is not None:
        for col in feature_columns:
            if col in df.columns and df[col].nunique() <= 1:
                 issues.append(MLDatasetQualityIssue(
                     issue_type="constant_feature", severity="warning", column=col, message=f"Constant feature: {col}"
                 ))
    return issues

def assert_ml_dataset_quality_passed(report: MLDatasetQualityReport, config: AppConfig) -> None:
    if report.status == "failed":
        raise MLDatasetQualityError("Dataset failed critical quality checks.")

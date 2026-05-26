import pandas as pd
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.core.exceptions import MLLeakageError

class MLLeakageIssue(BaseModel):
    issue_type: str
    severity: str
    column: str
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)

class MLLeakageReport(BaseModel):
    status: str
    issue_count: int
    future_column_count: int
    label_in_feature_count: int
    target_in_feature_count: int
    negative_shift_feature_count: int
    global_fit_issue_count: int
    split_overlap_issue_count: int
    alignment_issue_count: int
    issues: list[MLLeakageIssue] = Field(default_factory=list)
    generated_at_utc: datetime | str

def build_ml_leakage_report(
    dataset_df: pd.DataFrame,
    feature_columns: list[str],
    label_columns: list[str],
    split_metadata: Any,
    preprocessing_metadata: Any,
    config: AppConfig
) -> MLLeakageReport:
    issues = []

    issues.extend(detect_label_columns_in_features(feature_columns, label_columns))
    issues.extend(detect_future_target_columns_in_features(feature_columns))
    issues.extend(detect_global_preprocessing_fit(preprocessing_metadata))
    issues.extend(detect_split_overlap(split_metadata))

    issue_count = len(issues)

    status = "clean"
    if any(i.severity == "critical" for i in issues):
        status = "failed"
    elif issue_count > 0:
        status = "warnings"

    report = MLLeakageReport(
        status=status,
        issue_count=issue_count,
        future_column_count=sum(1 for i in issues if i.issue_type == "future_in_feature"),
        label_in_feature_count=sum(1 for i in issues if i.issue_type == "label_in_feature"),
        target_in_feature_count=sum(1 for i in issues if i.issue_type == "target_in_feature"),
        negative_shift_feature_count=0,
        global_fit_issue_count=sum(1 for i in issues if i.issue_type == "global_fit"),
        split_overlap_issue_count=sum(1 for i in issues if i.issue_type == "split_overlap"),
        alignment_issue_count=0,
        issues=issues,
        generated_at_utc=datetime.utcnow()
    )

    assert_ml_leakage_free(report, config)
    return report

def detect_label_columns_in_features(feature_columns: list[str], label_columns: list[str]) -> list[MLLeakageIssue]:
    issues = []
    for col in feature_columns:
        if col in label_columns or "label_" in col:
            issues.append(MLLeakageIssue(
                issue_type="label_in_feature",
                severity="critical",
                column=col,
                message=f"Label column {col} found in feature set",
            ))
    return issues

def detect_future_target_columns_in_features(feature_columns: list[str]) -> list[MLLeakageIssue]:
    issues = []
    forbidden = ["future", "target", "next", "forward"]
    for col in feature_columns:
        if any(f in col.lower() for f in forbidden):
            issues.append(MLLeakageIssue(
                issue_type="future_in_feature",
                severity="critical",
                column=col,
                message=f"Future/Target related keyword found in feature column {col}",
            ))
    return issues

def detect_negative_shift_feature_metadata(feature_metadata: Any) -> list[MLLeakageIssue]:
    return []

def detect_global_preprocessing_fit(preprocessing_metadata: Any) -> list[MLLeakageIssue]:
    issues = []
    if preprocessing_metadata and preprocessing_metadata.fit_split != "train":
        issues.append(MLLeakageIssue(
            issue_type="global_fit",
            severity="critical",
            column="*",
            message="Preprocessing was not fit exclusively on train split",
        ))
    return issues

def detect_split_overlap(split_metadata: Any) -> list[MLLeakageIssue]:
    # Placeholder for overlap logic
    return []

def detect_forward_alignment(alignment_metadata: Any) -> list[MLLeakageIssue]:
    return []

def assert_ml_leakage_free(report: MLLeakageReport, config: AppConfig) -> None:
    if report.status == "failed" and config.ml_dataset and config.ml_dataset.leakage.prevent_lookahead_bias:
         raise MLLeakageError("Critical leakage issue detected in ML dataset")

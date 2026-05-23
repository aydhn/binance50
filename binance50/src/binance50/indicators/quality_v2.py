import pandas as pd
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timezone
import numpy as np

from binance50.config.models import AppConfig
from binance50.core.exceptions import FeatureQualityError
from binance50.features.grouping import exclude_non_feature_columns
from .feature_groups import infer_feature_group

class FeatureQualityIssue(BaseModel):
    feature_name: str
    issue_type: str
    severity: str
    message: str
    metadata: Dict[str, Any] = {}

class FeatureQualityReport(BaseModel):
    status: str
    feature_count: int
    row_count: int
    issues: List[FeatureQualityIssue]
    nan_ratio_by_feature: Dict[str, float]
    inf_features: List[str]
    duplicate_features: List[str]
    ungrouped_features: List[str]
    lookahead_risk_features: List[str]
    generated_at_utc: datetime

def detect_duplicate_feature_names(columns: List[str]) -> List[str]:
    seen = set()
    dupes = []
    for col in columns:
        if col in seen:
            dupes.append(col)
        seen.add(col)
    return dupes

def detect_lookahead_risk_features(columns: List[str]) -> List[str]:
    from binance50.features.grouping import TARGET_KEYWORDS
    risks = []
    for col in columns:
        col_lower = col.lower()
        if any(k in col_lower for k in TARGET_KEYWORDS):
            risks.append(col)
    return risks

def detect_high_nan_features(df: pd.DataFrame, config: AppConfig) -> Dict[str, float]:
    features = exclude_non_feature_columns(df.columns.tolist())
    max_ratio = config.indicator_v2.quality.max_nan_ratio

    nan_counts = df[features].isna().sum()
    total_rows = len(df)

    high_nans = {}
    if total_rows > 0:
        for col in features:
            ratio = float(nan_counts[col] / total_rows)
            if ratio > max_ratio:
                high_nans[col] = ratio

    return high_nans

def detect_inf_features(df: pd.DataFrame) -> List[str]:
    features = exclude_non_feature_columns(df.columns.tolist())
    infs = []

    # Select only numeric types
    numeric_df = df[features].select_dtypes(include=[np.number])

    for col in numeric_df.columns:
        if np.isinf(numeric_df[col]).any():
            infs.append(col)

    return infs

def detect_unregistered_features(df: pd.DataFrame, registry, config: AppConfig) -> List[str]:
    features = exclude_non_feature_columns(df.columns.tolist())
    unreg = []
    for f in features:
        if not registry.get_feature(f):
            unreg.append(f)
    return unreg

def build_feature_quality_report(df: pd.DataFrame, feature_columns: List[str], config: AppConfig, registry=None) -> FeatureQualityReport:
    cfg = config.indicator_v2.quality

    issues = []
    status = "pass"

    dupes = detect_duplicate_feature_names(df.columns.tolist())
    if dupes and cfg.reject_duplicate_feature_names:
        status = "fail"
        for d in dupes:
            issues.append(FeatureQualityIssue(feature_name=d, issue_type="duplicate", severity="error", message="Duplicate feature name"))

    lookahead = detect_lookahead_risk_features(feature_columns)
    if lookahead and cfg.reject_lookahead_columns:
        status = "fail"
        for l in lookahead:
            issues.append(FeatureQualityIssue(feature_name=l, issue_type="lookahead", severity="error", message="Lookahead/target keyword detected"))

    infs = detect_inf_features(df)
    if infs and cfg.reject_inf:
        status = "fail"
        for i in infs:
            issues.append(FeatureQualityIssue(feature_name=i, issue_type="inf_values", severity="error", message="Infinite values detected"))

    high_nans = detect_high_nan_features(df, config)
    all_nan = [f for f, r in high_nans.items() if r >= 0.999]
    if all_nan and cfg.reject_all_nan_feature:
        status = "fail"
        for a in all_nan:
            issues.append(FeatureQualityIssue(feature_name=a, issue_type="all_nan", severity="error", message="Feature is entirely NaN"))

    if cfg.warn_high_nan_ratio:
        for f, r in high_nans.items():
            if f not in all_nan:
                issues.append(FeatureQualityIssue(feature_name=f, issue_type="high_nan", severity="warning", message=f"NaN ratio is {r:.2f} > max_nan_ratio"))

    unreg = []
    if registry and cfg.reject_unregistered_feature:
        unreg = detect_unregistered_features(df, registry, config)
        if unreg:
            status = "fail"
            for u in unreg:
                issues.append(FeatureQualityIssue(feature_name=u, issue_type="unregistered", severity="error", message="Feature not in registry"))

    ungrouped = []
    if not config.indicator_v2.feature_groups.allow_ungrouped_features:
        for f in feature_columns:
            if not infer_feature_group(f, config):
                ungrouped.append(f)
                status = "fail"
                issues.append(FeatureQualityIssue(feature_name=f, issue_type="ungrouped", severity="error", message="Feature doesn't belong to any group"))

    nan_ratios = {}
    total_rows = len(df)
    if total_rows > 0:
        nan_counts = df[feature_columns].isna().sum()
        for c in feature_columns:
            nan_ratios[c] = float(nan_counts[c] / total_rows)

    return FeatureQualityReport(
        status=status,
        feature_count=len(feature_columns),
        row_count=total_rows,
        issues=issues,
        nan_ratio_by_feature=nan_ratios,
        inf_features=infs,
        duplicate_features=dupes,
        ungrouped_features=ungrouped,
        lookahead_risk_features=lookahead,
        generated_at_utc=datetime.now(timezone.utc)
    )

def assert_feature_quality_passed(report: FeatureQualityReport, config: AppConfig) -> None:
    if report.status == "fail":
        errors = [i.message for i in report.issues if i.severity == "error"]
        raise FeatureQualityError(f"Feature quality checks failed. Errors: {errors[:3]}")

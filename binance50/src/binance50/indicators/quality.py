from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import numpy as np
import pandas as pd

from binance50.config.models import AppConfig
from binance50.core.exceptions import IndicatorQualityError


@dataclass
class IndicatorQualityIssue:
    column: str
    issue_type: str
    severity: str
    message: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self, redacted: bool = True) -> dict[str, Any]:
        return {
            "column": self.column,
            "issue_type": self.issue_type,
            "severity": self.severity,
            "message": self.message,
            "metadata": self.metadata,
        }


@dataclass
class IndicatorQualityReport:
    status: str
    row_count: int
    indicator_column_count: int
    issues: list[IndicatorQualityIssue]
    nan_ratio_by_column: dict[str, float]
    inf_columns: list[str]
    constant_columns: list[str]
    extreme_value_columns: list[str]
    generated_at_utc: str

    def to_dict(self, redacted: bool = True) -> dict[str, Any]:
        return {
            "status": self.status,
            "row_count": self.row_count,
            "indicator_column_count": self.indicator_column_count,
            "issues": [i.to_dict() for i in self.issues],
            "nan_ratio_by_column": self.nan_ratio_by_column,
            "inf_columns": self.inf_columns,
            "constant_columns": self.constant_columns,
            "extreme_value_columns": self.extreme_value_columns,
            "generated_at_utc": self.generated_at_utc,
        }


def build_indicator_quality_report(
    df: pd.DataFrame, indicator_columns: list[str], config: AppConfig
) -> IndicatorQualityReport:
    issues = []
    nan_ratio_by_column = {}
    inf_columns = []
    constant_columns = []
    extreme_value_columns = []

    if len(df) == 0:
        return IndicatorQualityReport(
            "fail",
            0,
            len(indicator_columns),
            [IndicatorQualityIssue("all", "empty_dataframe", "error", "Dataframe is empty")],
            {},
            [],
            [],
            [],
            datetime.now(UTC).isoformat(),
        )

    for col in indicator_columns:
        if col not in df.columns:
            continue

        s = df[col]

        # NaN ratio
        nan_count = s.isna().sum()
        nan_ratio = nan_count / len(df)
        nan_ratio_by_column[col] = float(nan_ratio)

        if nan_ratio == 1.0:
            if config.indicators.quality.reject_all_nan_indicator:
                issues.append(
                    IndicatorQualityIssue(col, "all_nan", "error", "Indicator is all NaN")
                )
        elif (
            config.indicators.quality.warn_high_nan_ratio
            and nan_ratio > config.indicators.quality.max_nan_ratio
        ):
            issues.append(
                IndicatorQualityIssue(
                    col, "high_nan_ratio", "warning", f"High NaN ratio: {nan_ratio:.2%}"
                )
            )

        # Inf check
        if config.indicators.quality.detect_inf and np.isinf(s).any():
            inf_columns.append(col)
            issues.append(
                IndicatorQualityIssue(col, "infinity_detected", "error", "Infinity values detected")
            )

        # Constant check (ignore nan)
        s_valid = s.dropna()
        if len(s_valid) > 1 and s_valid.nunique() == 1:
            constant_columns.append(col)
            sev = "error" if config.indicators.quality.reject_constant_indicator else "warning"
            issues.append(
                IndicatorQualityIssue(col, "constant_values", sev, "Indicator has constant values")
            )

        # Extreme values check
        if config.indicators.quality.detect_extreme_values and len(s_valid) > 1:
            mean = s_valid.mean()
            std = s_valid.std()
            if std > 0:
                z = (s_valid - mean).abs() / std
                if (z > config.indicators.quality.extreme_zscore_threshold).any():
                    extreme_value_columns.append(col)
                    issues.append(
                        IndicatorQualityIssue(
                            col,
                            "extreme_values",
                            "warning",
                            f"Extreme values detected (z > {config.indicators.quality.extreme_zscore_threshold})",
                        )
                    )

    status = "pass"
    if any(i.severity == "error" for i in issues):
        status = "fail"

    return IndicatorQualityReport(
        status=status,
        row_count=len(df),
        indicator_column_count=len(indicator_columns),
        issues=issues,
        nan_ratio_by_column=nan_ratio_by_column,
        inf_columns=inf_columns,
        constant_columns=constant_columns,
        extreme_value_columns=extreme_value_columns,
        generated_at_utc=datetime.now(UTC).isoformat(),
    )


def assert_indicator_quality_passed(report: IndicatorQualityReport, config: AppConfig) -> None:
    if report.status == "fail":
        errors = [i.message for i in report.issues if i.severity == "error"]
        raise IndicatorQualityError(f"Indicator quality check failed: {', '.join(errors)}")

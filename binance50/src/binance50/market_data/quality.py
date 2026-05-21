from datetime import UTC, datetime
from typing import Any

import pandas as pd
from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.core.enums import MarketScope
from binance50.core.exceptions import OHLCVQualityError
from binance50.market_data.incremental import compute_missing_ranges
from binance50.market_data.intervals import is_candle_closed
from binance50.market_data.ohlcv_models import OHLCVValidationStatus


class OHLCVQualityIssue(BaseModel):
    issue_type: str
    severity: OHLCVValidationStatus
    symbol: str | None = None
    interval: str | None = None
    open_time: int | None = None
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class OHLCVQualityReport(BaseModel):
    symbol: str
    market_scope: MarketScope
    interval: str
    row_count: int
    status: OHLCVValidationStatus
    issues: list[OHLCVQualityIssue] = Field(default_factory=list)
    duplicate_count: int = 0
    gap_count: int = 0
    out_of_order_count: int = 0
    incomplete_last_candle: bool = False
    start_open_time: int | None = None
    end_open_time: int | None = None
    generated_at_utc: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


def validate_ohlcv_dataframe(
    df: pd.DataFrame, config: AppConfig, now_ms: int | None = None
) -> OHLCVQualityReport:
    if df.empty:
        return OHLCVQualityReport(
            symbol="UNKNOWN",
            market_scope=MarketScope.SPOT,
            interval="UNKNOWN",
            row_count=0,
            status=OHLCVValidationStatus.INVALID,
            issues=[
                OHLCVQualityIssue(
                    issue_type="empty_dataframe",
                    severity=OHLCVValidationStatus.INVALID,
                    message="DataFrame is empty.",
                )
            ],
        )

    symbol = df["symbol"].iloc[0]
    market_scope = MarketScope(df["market_scope"].iloc[0])
    interval = df["interval"].iloc[0]

    report = OHLCVQualityReport(
        symbol=symbol,
        market_scope=market_scope,
        interval=interval,
        row_count=len(df),
        status=OHLCVValidationStatus.VALID,
        start_open_time=int(df["open_time"].min()),
        end_open_time=int(df["open_time"].max()),
    )

    issues = []

    # 1. Duplicates
    dup_issues = detect_duplicate_open_times(df)
    issues.extend(dup_issues)
    report.duplicate_count = len(dup_issues)

    # 2. Out of order
    ooo_issues = detect_out_of_order(df)
    issues.extend(ooo_issues)
    report.out_of_order_count = len(ooo_issues)

    # 3. Gaps
    if config.market_data.quality.detect_gaps:
        gap_issues = detect_gaps(df, interval)
        issues.extend(gap_issues)
        report.gap_count = len(gap_issues)

        if len(df) > 0 and report.gap_count > 0:
            gap_ratio = (report.gap_count / len(df)) * 100
            if gap_ratio > config.market_data.quality.max_gap_ratio_pct:
                issues.append(
                    OHLCVQualityIssue(
                        issue_type="excessive_gaps",
                        severity=OHLCVValidationStatus.INVALID,
                        symbol=symbol,
                        interval=interval,
                        message=f"Gap ratio ({gap_ratio:.2f}%) exceeds max ({config.market_data.quality.max_gap_ratio_pct}%)",
                    )
                )

    # 4. Incomplete last candle
    inc_issue = detect_incomplete_last_candle(df, interval, now_ms, config)
    if inc_issue:
        issues.append(inc_issue)
        report.incomplete_last_candle = True

    # 5. Price inconsistencies
    price_issues = detect_price_inconsistencies(df)
    issues.extend(price_issues)

    # 6. Volume inconsistencies
    vol_issues = detect_volume_inconsistencies(df)
    issues.extend(vol_issues)

    # 7. Min rows check
    if len(df) < config.market_data.min_rows_required:
        issues.append(
            OHLCVQualityIssue(
                issue_type="insufficient_data",
                severity=OHLCVValidationStatus.WARNING,
                symbol=symbol,
                interval=interval,
                message=f"Row count {len(df)} is below minimum required {config.market_data.min_rows_required}",
            )
        )

    # Resolve overall status
    has_invalid = any(i.severity == OHLCVValidationStatus.INVALID for i in issues)
    has_warning = any(i.severity == OHLCVValidationStatus.WARNING for i in issues)

    if has_invalid:
        report.status = OHLCVValidationStatus.INVALID
    elif has_warning:
        report.status = OHLCVValidationStatus.WARNING

    report.issues = issues
    return report


def detect_duplicate_open_times(df: pd.DataFrame) -> list[OHLCVQualityIssue]:
    duplicates = df[df.duplicated(subset=["open_time"], keep=False)]
    if duplicates.empty:
        return []

    issues = []
    # Just record one issue per unique duplicate timestamp to avoid spam
    unique_dups = duplicates["open_time"].unique()
    for ot in unique_dups:
        issues.append(
            OHLCVQualityIssue(
                issue_type="duplicate_open_time",
                severity=OHLCVValidationStatus.INVALID,
                open_time=int(ot),
                message=f"Duplicate open_time detected: {ot}",
            )
        )
    return issues


def detect_out_of_order(df: pd.DataFrame) -> list[OHLCVQualityIssue]:
    issues = []
    # Check if open_time strictly increases
    diffs = df["open_time"].diff()
    out_of_order_idx = diffs[diffs < 0].index

    for idx in out_of_order_idx:
        ot = int(df.loc[idx, "open_time"])
        issues.append(
            OHLCVQualityIssue(
                issue_type="out_of_order",
                severity=OHLCVValidationStatus.INVALID,
                open_time=ot,
                message=f"Candle at index {idx} is out of chronological order (open_time {ot})",
            )
        )
    return issues


def detect_gaps(df: pd.DataFrame, interval: str) -> list[OHLCVQualityIssue]:
    missing_ranges = compute_missing_ranges(df, interval)
    issues = []
    for start, end in missing_ranges:
        issues.append(
            OHLCVQualityIssue(
                issue_type="data_gap",
                severity=OHLCVValidationStatus.WARNING,  # Gaps are usually warnings, maybe invalid if ratio is too high
                open_time=start,
                message=f"Data gap detected from {start} to {end}",
                metadata={"gap_start": start, "gap_end": end},
            )
        )
    return issues


def detect_incomplete_last_candle(
    df: pd.DataFrame, interval: str, now_ms: int | None, config: AppConfig
) -> OHLCVQualityIssue | None:
    if df.empty:
        return None

    sorted_df = df.sort_values(by="open_time").reset_index(drop=True)
    last_row = sorted_df.iloc[-1]

    if not is_candle_closed(
        int(last_row["open_time"]), int(last_row["close_time"]), interval, now_ms
    ):
        severity = (
            OHLCVValidationStatus.INVALID
            if config.market_data.require_closed_candles
            else OHLCVValidationStatus.WARNING
        )
        return OHLCVQualityIssue(
            issue_type="incomplete_last_candle",
            severity=severity,
            open_time=int(last_row["open_time"]),
            message=f"Last candle is incomplete (open_time {int(last_row['open_time'])})",
        )
    return None


def detect_price_inconsistencies(df: pd.DataFrame) -> list[OHLCVQualityIssue]:
    issues = []

    # Negative prices
    neg_mask = (df["open"] < 0) | (df["high"] < 0) | (df["low"] < 0) | (df["close"] < 0)
    for _idx, row in df[neg_mask].iterrows():
        issues.append(
            OHLCVQualityIssue(
                issue_type="negative_price",
                severity=OHLCVValidationStatus.INVALID,
                open_time=int(row["open_time"]),
                message=f"Negative price detected at {row['open_time']}",
            )
        )

    # Zero or negative close
    zn_mask = df["close"] <= 0
    for _idx, row in df[zn_mask].iterrows():
        issues.append(
            OHLCVQualityIssue(
                issue_type="zero_or_negative_close",
                severity=OHLCVValidationStatus.INVALID,
                open_time=int(row["open_time"]),
                message=f"Zero or negative close detected at {row['open_time']}",
            )
        )

    # High/Low inconsistencies
    hl_mask = (
        (df["high"] < df["low"])
        | (df["high"] < df["open"])
        | (df["high"] < df["close"])
        | (df["low"] > df["open"])
        | (df["low"] > df["close"])
    )
    for _idx, row in df[hl_mask].iterrows():
        issues.append(
            OHLCVQualityIssue(
                issue_type="high_low_inconsistency",
                severity=OHLCVValidationStatus.INVALID,
                open_time=int(row["open_time"]),
                message=f"High/Low inconsistency at {row['open_time']}",
            )
        )

    return issues


def detect_volume_inconsistencies(df: pd.DataFrame) -> list[OHLCVQualityIssue]:
    issues = []

    # Negative volume
    neg_vol_mask = (
        (df["volume"] < 0) | (df["quote_asset_volume"] < 0) | (df["number_of_trades"] < 0)
    )
    for _idx, row in df[neg_vol_mask].iterrows():
        issues.append(
            OHLCVQualityIssue(
                issue_type="negative_volume",
                severity=OHLCVValidationStatus.INVALID,
                open_time=int(row["open_time"]),
                message=f"Negative volume or trades detected at {row['open_time']}",
            )
        )

    # Zero volume
    zero_vol_mask = df["volume"] == 0
    for _idx, row in df[zero_vol_mask].iterrows():
        issues.append(
            OHLCVQualityIssue(
                issue_type="zero_volume",
                severity=OHLCVValidationStatus.WARNING,
                open_time=int(row["open_time"]),
                message=f"Zero volume detected at {row['open_time']}",
            )
        )

    return issues


def assert_quality_passed(report: OHLCVQualityReport, config: AppConfig) -> None:
    if report.status == OHLCVValidationStatus.INVALID:
        invalid_issues = [
            i.message for i in report.issues if i.severity == OHLCVValidationStatus.INVALID
        ]
        raise OHLCVQualityError(f"Data quality validation failed: {invalid_issues}")

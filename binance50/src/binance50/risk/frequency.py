from datetime import datetime, timedelta

import pandas as pd

from binance50.config.models import AppConfig
from binance50.risk.models import RiskComponent, RiskDimension, RiskSeverity


def check_candidate_frequency(
    symbol: str, open_time: datetime, history_df: pd.DataFrame | None, config: AppConfig
) -> RiskComponent:
    limit = config.risk.frequency.max_risk_reviews_per_symbol_per_hour
    if history_df is None or history_df.empty:
        return RiskComponent(
            dimension=RiskDimension.frequency,
            raw_value=0,
            passed=True,
            severity=RiskSeverity.info,
            reason="No history available, frequency limit passes",
            metadata={"limit": limit},
        )
    cutoff_time = open_time - timedelta(hours=1)
    if "symbol" in history_df.columns and "open_time" in history_df.columns:
        recent = history_df[
            (history_df["symbol"] == symbol) & (history_df["open_time"] >= cutoff_time)
        ]
        count = len(recent)
    else:
        count = 0
    passed = count <= limit
    return RiskComponent(
        dimension=RiskDimension.frequency,
        raw_value=count,
        passed=passed,
        severity=RiskSeverity.info if passed else RiskSeverity.blocked,
        reason="Symbol frequency within limits" if passed else "Symbol review frequency exceeded",
        metadata={"limit": limit, "symbol": symbol},
    )


def check_same_direction_frequency(
    symbol: str, direction: str, history_df: pd.DataFrame | None, config: AppConfig
) -> RiskComponent:
    limit = config.risk.frequency.max_same_direction_candidates_per_symbol_per_hour
    if history_df is None or history_df.empty:
        return RiskComponent(
            dimension=RiskDimension.frequency,
            raw_value=0,
            passed=True,
            severity=RiskSeverity.info,
            reason="No history available, direction frequency limit passes",
            metadata={"limit": limit},
        )
    count = 0
    if "symbol" in history_df.columns and "direction" in history_df.columns:
        count = len(
            history_df[(history_df["symbol"] == symbol) & (history_df["direction"] == direction)]
        )
    passed = count <= limit
    return RiskComponent(
        dimension=RiskDimension.frequency,
        raw_value=count,
        passed=passed,
        severity=RiskSeverity.info if passed else RiskSeverity.blocked,
        reason=(
            "Direction frequency within limits" if passed else "Direction review frequency exceeded"
        ),
        metadata={"limit": limit, "symbol": symbol, "direction": direction},
    )


def check_total_review_frequency(
    history_df: pd.DataFrame | None, config: AppConfig
) -> RiskComponent:
    limit = config.risk.frequency.max_risk_reviews_total_per_hour
    count = len(history_df) if history_df is not None else 0
    passed = count <= limit
    return RiskComponent(
        dimension=RiskDimension.frequency,
        raw_value=count,
        passed=passed,
        severity=RiskSeverity.info if passed else RiskSeverity.blocked,
        reason="Total frequency within limits" if passed else "Total review frequency exceeded",
        metadata={"limit": limit},
    )


def build_frequency_report(history_df: pd.DataFrame | None, config: AppConfig) -> dict:
    return {"total_history_count": len(history_df) if history_df is not None else 0}

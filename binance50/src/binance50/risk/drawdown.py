from typing import Any

from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.risk.models import RiskComponent, RiskDimension, RiskSeverity


class DrawdownSnapshot(BaseModel):
    source: str = "simulated_placeholder"
    daily_loss_pct: float = 0.0
    weekly_loss_pct: float = 0.0
    monthly_loss_pct: float = 0.0
    max_drawdown_pct: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


def build_empty_drawdown_snapshot(config: AppConfig) -> DrawdownSnapshot:
    return DrawdownSnapshot()


def check_daily_loss_limit(snapshot: DrawdownSnapshot, config: AppConfig) -> RiskComponent:
    loss = snapshot.daily_loss_pct
    limit = config.risk.global_limits.max_daily_loss_pct
    passed = loss <= limit
    return RiskComponent(
        dimension=RiskDimension.drawdown,
        raw_value=loss,
        passed=passed,
        severity=RiskSeverity.info if passed else RiskSeverity.blocked,
        reason="Daily loss within limits" if passed else "Daily loss limit exceeded",
        metadata={"limit": limit},
    )


def check_weekly_loss_limit(snapshot: DrawdownSnapshot, config: AppConfig) -> RiskComponent:
    loss = snapshot.weekly_loss_pct
    limit = config.risk.global_limits.max_weekly_loss_pct
    passed = loss <= limit
    return RiskComponent(
        dimension=RiskDimension.drawdown,
        raw_value=loss,
        passed=passed,
        severity=RiskSeverity.info if passed else RiskSeverity.blocked,
        reason="Weekly loss within limits" if passed else "Weekly loss limit exceeded",
        metadata={"limit": limit},
    )


def check_monthly_loss_limit(snapshot: DrawdownSnapshot, config: AppConfig) -> RiskComponent:
    loss = snapshot.monthly_loss_pct
    limit = config.risk.global_limits.max_monthly_loss_pct
    passed = loss <= limit
    return RiskComponent(
        dimension=RiskDimension.drawdown,
        raw_value=loss,
        passed=passed,
        severity=RiskSeverity.info if passed else RiskSeverity.blocked,
        reason="Monthly loss within limits" if passed else "Monthly loss limit exceeded",
        metadata={"limit": limit},
    )


def build_drawdown_report(snapshot: DrawdownSnapshot) -> dict:
    return snapshot.model_dump()

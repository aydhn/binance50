from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.risk.models import RiskAssessment, RiskComponent, RiskDimension, RiskSeverity


class ExposureSnapshot(BaseModel):
    source: str = "simulated_placeholder"
    total_exposure_pct: float = 0.0
    symbol_exposure_pct: dict[str, float] = Field(default_factory=dict)
    open_risk_candidates: int = 0
    correlated_candidates: int = 0
    generated_at_utc: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


def build_simulated_exposure_snapshot(
    assessments: list[RiskAssessment], config: AppConfig
) -> ExposureSnapshot:
    total = 0.0
    symbol_exp = {}
    for a in assessments:
        if a.hypothetical_risk_pct:
            total += a.hypothetical_risk_pct
            symbol_exp[a.symbol] = symbol_exp.get(a.symbol, 0.0) + a.hypothetical_risk_pct
    return ExposureSnapshot(
        total_exposure_pct=total,
        symbol_exposure_pct=symbol_exp,
        open_risk_candidates=len(assessments),
        correlated_candidates=0,
    )


def check_symbol_exposure(
    snapshot: ExposureSnapshot, symbol: str, config: AppConfig
) -> RiskComponent:
    exposure = snapshot.symbol_exposure_pct.get(symbol, 0.0)
    limit = config.risk.position_risk.max_symbol_exposure_pct
    passed = exposure <= limit
    return RiskComponent(
        dimension=RiskDimension.exposure,
        raw_value=exposure,
        passed=passed,
        severity=RiskSeverity.info if passed else RiskSeverity.blocked,
        reason="Symbol exposure within limits" if passed else "Symbol exposure exceeds maximum",
        metadata={"symbol": symbol, "limit": limit},
    )


def check_total_exposure(snapshot: ExposureSnapshot, config: AppConfig) -> RiskComponent:
    exposure = snapshot.total_exposure_pct
    limit = config.risk.position_risk.max_total_exposure_pct
    passed = exposure <= limit
    return RiskComponent(
        dimension=RiskDimension.exposure,
        raw_value=exposure,
        passed=passed,
        severity=RiskSeverity.info if passed else RiskSeverity.blocked,
        reason="Total exposure within limits" if passed else "Total exposure exceeds maximum",
        metadata={"limit": limit},
    )


def check_correlated_candidates_placeholder(
    snapshot: ExposureSnapshot, config: AppConfig
) -> RiskComponent:
    limit = config.risk.global_limits.max_correlated_candidates
    count = snapshot.correlated_candidates
    passed = count <= limit
    return RiskComponent(
        dimension=RiskDimension.exposure,
        raw_value=count,
        passed=passed,
        severity=RiskSeverity.info if passed else RiskSeverity.warning,
        reason="Correlation within limits" if passed else "Correlation warning",
        metadata={"limit": limit},
    )


def build_exposure_report(snapshot: ExposureSnapshot) -> dict:
    return snapshot.model_dump()

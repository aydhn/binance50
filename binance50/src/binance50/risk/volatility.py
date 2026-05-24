from typing import Any

from binance50.config.models import AppConfig
from binance50.risk.models import RiskComponent, RiskDimension, RiskSeverity


def check_atr_pct(feature_row: dict[str, Any], config: AppConfig) -> RiskComponent:
    atr_pct = feature_row.get("vol_atr_14_pct", 0.0)
    max_atr = config.risk.volatility.max_atr_pct_for_candidate
    passed = atr_pct <= max_atr or not config.risk.volatility.reject_extreme_volatility
    severity = RiskSeverity.info if passed else RiskSeverity.blocked
    return RiskComponent(
        dimension=RiskDimension.volatility,
        raw_value=atr_pct,
        passed=passed,
        severity=severity,
        reason="ATR within limits" if passed else "Extreme ATR detected",
        metadata={"max_atr": max_atr},
    )


def check_realized_vol_z(feature_row: dict[str, Any], config: AppConfig) -> RiskComponent:
    vol_z = feature_row.get("vol_realized_vol_20_z", 0.0)
    max_z = config.risk.volatility.max_realized_vol_z
    passed = vol_z <= max_z or not config.risk.volatility.reject_extreme_volatility
    severity = RiskSeverity.info if passed else RiskSeverity.blocked
    return RiskComponent(
        dimension=RiskDimension.volatility,
        raw_value=vol_z,
        passed=passed,
        severity=severity,
        reason="Realized vol within limits" if passed else "Extreme realized volatility detected",
        metadata={"max_z": max_z},
    )


def check_volatile_regime(
    regime_context: dict[str, Any] | None, config: AppConfig
) -> RiskComponent:
    if not regime_context:
        return RiskComponent(
            dimension=RiskDimension.volatility, passed=True, reason="No regime context", metadata={}
        )
    regime = regime_context.get("regime", "unknown")
    penalty = 0.0
    bonus = 0.0
    reason = "Normal volatility regime"
    if regime == "volatile":
        penalty = config.risk.volatility.volatile_regime_penalty
        reason = "Volatile regime penalty applied"
    elif regime == "calm":
        bonus = config.risk.volatility.calm_regime_bonus
        reason = "Calm regime bonus applied"
    return RiskComponent(
        dimension=RiskDimension.volatility,
        raw_value=0.0,
        penalty=penalty,
        bonus=bonus,
        passed=True,
        severity=RiskSeverity.warning if penalty > 0 else RiskSeverity.info,
        reason=reason,
        metadata={"regime": regime},
    )


def compute_volatility_risk(
    scored_signal: Any,
    regime_context: dict[str, Any] | None,
    feature_row: dict[str, Any],
    config: AppConfig,
) -> list[RiskComponent]:
    if not config.risk.volatility.enabled:
        return []
    return [
        check_atr_pct(feature_row, config),
        check_realized_vol_z(feature_row, config),
        check_volatile_regime(regime_context, config),
    ]


def build_volatility_risk_report(components: list[RiskComponent]) -> dict:
    return {"components": [c.model_dump() for c in components]}

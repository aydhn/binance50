from typing import Any

from binance50.config.models import AppConfig
from binance50.risk.models import RiskComponent, RiskDimension, RiskSeverity


def check_futures_context_allowed(market_scope: str, config: AppConfig) -> RiskComponent:
    if market_scope == "futures" and not config.risk.futures.allow_usdm_futures_context:
        return RiskComponent(
            dimension=RiskDimension.leverage,
            passed=False,
            severity=RiskSeverity.blocked,
            reason="USDM futures context not allowed",
            metadata={},
        )
    return RiskComponent(
        dimension=RiskDimension.leverage, passed=True, reason="Market scope allowed", metadata={}
    )


def estimate_leverage_context(scored_signal: Any, config: AppConfig) -> dict:
    return {"estimated_leverage": config.risk.futures.default_leverage_for_estimate}


def check_leverage_policy(leverage: int, config: AppConfig) -> RiskComponent:
    if leverage > config.risk.futures.hard_max_leverage_allowed:
        return RiskComponent(
            dimension=RiskDimension.leverage,
            passed=False,
            severity=RiskSeverity.blocked,
            reason="Estimated leverage exceeds hard maximum",
            metadata={
                "leverage": leverage,
                "hard_max": config.risk.futures.hard_max_leverage_allowed,
            },
        )
    if (
        config.risk.futures.reject_if_leverage_above_policy
        and leverage > config.risk.futures.max_leverage_for_estimate
    ):
        return RiskComponent(
            dimension=RiskDimension.leverage,
            passed=False,
            severity=RiskSeverity.blocked,
            reason="Estimated leverage exceeds policy maximum",
            metadata={
                "leverage": leverage,
                "policy_max": config.risk.futures.max_leverage_for_estimate,
            },
        )
    return RiskComponent(
        dimension=RiskDimension.leverage,
        raw_value=leverage,
        passed=True,
        severity=RiskSeverity.info,
        reason="Leverage within limits",
        metadata={"leverage": leverage},
    )


def check_margin_model_deferred(config: AppConfig) -> RiskComponent:
    return RiskComponent(
        dimension=RiskDimension.leverage,
        passed=True,
        severity=RiskSeverity.info,
        reason="Margin and liquidation models are deferred as per config",
        metadata={
            "liquidation_deferred": config.risk.futures.liquidation_model_deferred,
            "maintenance_deferred": config.risk.futures.maintenance_margin_model_deferred,
        },
    )


def build_futures_risk_placeholder_report(config: AppConfig) -> dict:
    return {"status": "placeholder", "config": config.risk.futures.model_dump()}

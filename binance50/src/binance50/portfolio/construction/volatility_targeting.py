from typing import Any

import pandas as pd
from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.portfolio.construction.volatility import (
    compute_portfolio_volatility,
    compute_volatility_scale_factor,
)


class VolatilityTargetingReport(BaseModel):
    enabled: bool
    skeleton_only: bool
    target_volatility_pct: float
    current_portfolio_volatility_pct: float
    scale_factor: float
    leverage_used: bool
    leverage_forbidden: bool
    cash_buffer_weight: float
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

def compute_volatility_target_scale(weights: dict[str, float], cov_matrix: pd.DataFrame, config: AppConfig) -> float:
    current_vol = compute_portfolio_volatility(weights, cov_matrix)
    target_vol = config.portfolio_construction.volatility_targeting.target_volatility_pct
    return compute_volatility_scale_factor(current_vol, target_vol, config)

def apply_volatility_targeting_skeleton(weights: dict[str, float], cov_matrix: pd.DataFrame, config: AppConfig) -> tuple[dict[str, float], VolatilityTargetingReport]:
    if not config.portfolio_construction.volatility_targeting.enabled:
        return weights, VolatilityTargetingReport(
            enabled=False, skeleton_only=True, target_volatility_pct=0.0, current_portfolio_volatility_pct=0.0, scale_factor=1.0, leverage_used=False, leverage_forbidden=True, cash_buffer_weight=0.0
        )
    current_vol = compute_portfolio_volatility(weights, cov_matrix)
    target_vol = config.portfolio_construction.volatility_targeting.target_volatility_pct
    scale_factor = compute_volatility_target_scale(weights, cov_matrix, config)
    warnings = []
    if current_vol < target_vol and not config.portfolio_construction.volatility_targeting.allow_leverage:
        scale_factor = min(scale_factor, 1.0)
        warnings.append("Target volatility is higher than current, but leverage is forbidden. Scaling limited to 1.0.")
    if config.portfolio_construction.volatility_targeting.production_scaling_forbidden:
        warnings.append("Production scaling is forbidden. This is a skeleton/sandbox projection only.")
    scaled_weights = {k: v * scale_factor for k, v in weights.items()}
    total_weight = sum(scaled_weights.values())
    leverage_used = total_weight > 1.0
    cash_buffer = max(0.0, 1.0 - total_weight)
    report = VolatilityTargetingReport(
        enabled=True,
        skeleton_only=config.portfolio_construction.volatility_targeting.skeleton_only,
        target_volatility_pct=target_vol,
        current_portfolio_volatility_pct=current_vol,
        scale_factor=scale_factor,
        leverage_used=leverage_used,
        leverage_forbidden=not config.portfolio_construction.volatility_targeting.allow_leverage,
        cash_buffer_weight=cash_buffer,
        warnings=warnings
    )
    return scaled_weights, report

def validate_volatility_targeting_output(report: VolatilityTargetingReport, config: AppConfig) -> None:
    if report.leverage_used and not config.portfolio_construction.volatility_targeting.allow_leverage:
        raise ValueError("Volatility targeting resulted in leverage, but leverage is forbidden.")

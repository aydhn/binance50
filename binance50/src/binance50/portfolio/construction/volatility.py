from typing import Any

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.core.exceptions import PortfolioVolatilityError


class PortfolioVolatilityReport(BaseModel):
    run_id: str
    symbol_volatilities: dict[str, float]
    portfolio_volatility_by_method: dict[str, float] = Field(default_factory=dict)
    volatility_floor_applied: bool = False
    volatility_cap_applied: bool = False
    target_volatility_pct: float | None = None
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

def compute_symbol_realized_volatility(returns_df: pd.DataFrame, config: AppConfig) -> dict[str, float]:
    if returns_df.empty: return {}
    vols = returns_df.std()
    if config.portfolio_construction.volatility.annualize:
        annualization_factor = np.sqrt(config.portfolio_construction.covariance.annualization_periods)
        vols = vols * annualization_factor
    vols_pct = (vols * 100).to_dict()
    return {k: v for k, v in vols_pct.items() if pd.notna(v)}

def apply_volatility_floor_cap(vols: dict[str, float], config: AppConfig) -> dict[str, float]:
    floor = config.portfolio_construction.volatility.min_volatility_floor_pct
    cap = config.portfolio_construction.volatility.max_volatility_cap_pct
    adjusted_vols = {}
    for symbol, vol in vols.items():
        if pd.isna(vol): continue
        adj_vol = max(floor, min(cap, vol))
        adjusted_vols[symbol] = float(adj_vol)
    return adjusted_vols

def compute_portfolio_volatility(weights: dict[str, float], cov_matrix: pd.DataFrame) -> float:
    if not weights or cov_matrix.empty: return 0.0
    symbols = list(cov_matrix.columns)
    w = np.array([weights.get(s, 0.0) for s in symbols])
    port_var = w.T @ cov_matrix.values @ w
    if port_var < 0: return 0.0
    port_vol = np.sqrt(port_var)
    return float(port_vol * 100)

def compute_volatility_scale_factor(current_vol: float, target_vol: float, config: AppConfig) -> float:
    if current_vol <= 0: return 1.0
    scale = target_vol / current_vol
    max_scale = config.portfolio_construction.volatility_targeting.max_scale_factor
    if config.portfolio_construction.volatility_targeting.allow_leverage is False:
        max_scale = min(max_scale, 1.0)
    return min(scale, max_scale)

def validate_volatility_estimates(vols: dict[str, float], config: AppConfig) -> None:
    if not vols: return
    if config.portfolio_construction.volatility.reject_zero_volatility:
        for symbol, vol in vols.items():
            if vol <= 0: raise PortfolioVolatilityError(f"Volatility for {symbol} is zero or negative ({vol}).")
    if config.portfolio_construction.quality.reject_non_finite_volatility:
        for symbol, vol in vols.items():
            if not np.isfinite(vol): raise PortfolioVolatilityError(f"Volatility for {symbol} is not finite ({vol}).")

def build_volatility_report(vols: dict[str, float], config: AppConfig, run_id: str = "unknown") -> PortfolioVolatilityReport:
    return PortfolioVolatilityReport(
        run_id=run_id,
        symbol_volatilities=vols,
        target_volatility_pct=config.portfolio_construction.volatility.target_portfolio_volatility_pct if config.portfolio_construction.volatility.volatility_targeting_enabled else None
    )

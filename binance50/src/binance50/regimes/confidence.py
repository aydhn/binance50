import pandas as pd

from binance50.config.models import AppConfig
from binance50.regimes.models import MarketRegime
from binance50.regimes.rules import RegimeRuleDecision


def clamp_confidence(value: float, config: AppConfig) -> float:
    return max(
        config.regimes.thresholds.min_regime_confidence,
        min(config.regimes.thresholds.max_regime_confidence, value),
    )


def confidence_to_label(confidence: float) -> str:
    if confidence >= 80:
        return "high"
    if confidence >= 50:
        return "medium"
    return "low"


def compute_trend_confidence(row: pd.Series, config: AppConfig) -> float:
    adx_col = f"reg_adx_{config.regimes.features.adx_period}"
    adx = row.get(adx_col, 0.0)
    if pd.isna(adx):
        return 0.0
    min_a = config.regimes.thresholds.trend_adx_min
    strong = config.regimes.thresholds.strong_trend_adx_min
    if adx <= min_a:
        return 0.0
    if adx >= strong:
        return 100.0
    return ((adx - min_a) / (strong - min_a)) * 100.0


def compute_range_confidence(row: pd.Series, config: AppConfig) -> float:
    adx_col = f"reg_adx_{config.regimes.features.adx_period}"
    adx = row.get(adx_col, 0.0)
    if pd.isna(adx):
        return 0.0
    max_a = config.regimes.thresholds.range_adx_max
    if adx >= max_a:
        return 0.0
    return ((max_a - adx) / max_a) * 100.0


def compute_volatility_confidence(row: pd.Series, config: AppConfig) -> float:
    w = config.regimes.features.realized_vol_period
    vol_col = f"reg_realized_vol_z_{w}"
    vol = row.get(vol_col, 0.0)
    if pd.isna(vol):
        return 0.0
    v_min = config.regimes.thresholds.volatile_realized_vol_z_min
    if vol <= v_min:
        return 0.0
    if vol >= v_min + 2.0:
        return 100.0
    return ((vol - v_min) / 2.0) * 100.0


def compute_calm_confidence(row: pd.Series, config: AppConfig) -> float:
    w = config.regimes.features.realized_vol_period
    vol_col = f"reg_realized_vol_z_{w}"
    vol = row.get(vol_col, 0.0)
    if pd.isna(vol):
        return 0.0
    v_max = config.regimes.thresholds.calm_realized_vol_z_max
    if vol >= v_max:
        return 0.0
    if vol <= v_max - 1.0:
        return 100.0
    return ((v_max - vol) / 1.0) * 100.0


def compute_rule_confidence(
    decision: RegimeRuleDecision, row: pd.Series, config: AppConfig
) -> float:
    conf = 0.0
    if decision.regime in [MarketRegime.trend_up, MarketRegime.trend_down]:
        conf = compute_trend_confidence(row, config)
    elif decision.regime == MarketRegime.range_bound:
        conf = compute_range_confidence(row, config)
    elif decision.regime == MarketRegime.volatile:
        conf = compute_volatility_confidence(row, config)
    elif decision.regime == MarketRegime.calm:
        conf = compute_calm_confidence(row, config)
    return clamp_confidence(conf, config)

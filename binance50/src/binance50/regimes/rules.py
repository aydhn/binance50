import pandas as pd
from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.regimes.models import MarketRegime, RegimeFamily, RegimeRiskContext


class RegimeRuleDecision(BaseModel):
    regime: MarketRegime
    family: RegimeFamily
    confidence: float
    risk_context: RegimeRiskContext
    reasons: list[str] = Field(default_factory=list)
    feature_evidence: dict[str, float] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


def build_rule_evidence(row: pd.Series, rule_name: str, passed: bool, values: dict) -> dict:
    return {"rule_name": rule_name, "passed": passed, "values": values}


def detect_trend_up_rule(row: pd.Series, config: AppConfig) -> RegimeRuleDecision | None:
    adx_col = f"reg_adx_{config.regimes.features.adx_period}"
    slope_col = f"reg_trend_slope_{config.regimes.features.slope_window}"
    adx = row.get(adx_col, 0.0)
    slope = row.get(slope_col, 0.0)
    if pd.isna(adx) or pd.isna(slope):
        return None
    if (
        adx >= config.regimes.thresholds.trend_adx_min
        and slope > config.regimes.thresholds.trend_slope_min_abs
    ):
        return RegimeRuleDecision(
            regime=MarketRegime.trend_up,
            family=RegimeFamily.trend,
            confidence=0.0,
            risk_context=RegimeRiskContext.risk_on_candidate,
            reasons=["ADX indicates trend", "Positive slope"],
            feature_evidence={"adx": float(adx), "slope": float(slope)},
        )
    return None


def detect_trend_down_rule(row: pd.Series, config: AppConfig) -> RegimeRuleDecision | None:
    adx_col = f"reg_adx_{config.regimes.features.adx_period}"
    slope_col = f"reg_trend_slope_{config.regimes.features.slope_window}"
    adx = row.get(adx_col, 0.0)
    slope = row.get(slope_col, 0.0)
    if pd.isna(adx) or pd.isna(slope):
        return None
    if (
        adx >= config.regimes.thresholds.trend_adx_min
        and slope < -config.regimes.thresholds.trend_slope_min_abs
    ):
        return RegimeRuleDecision(
            regime=MarketRegime.trend_down,
            family=RegimeFamily.trend,
            confidence=0.0,
            risk_context=RegimeRiskContext.risk_off_candidate,
            reasons=["ADX indicates trend", "Negative slope"],
            feature_evidence={"adx": float(adx), "slope": float(slope)},
        )
    return None


def detect_range_rule(row: pd.Series, config: AppConfig) -> RegimeRuleDecision | None:
    adx_col = f"reg_adx_{config.regimes.features.adx_period}"
    adx = row.get(adx_col, 0.0)
    if pd.isna(adx):
        return None
    if adx <= config.regimes.thresholds.range_adx_max:
        return RegimeRuleDecision(
            regime=MarketRegime.range_bound,
            family=RegimeFamily.range,
            confidence=0.0,
            risk_context=RegimeRiskContext.chop_candidate,
            reasons=["ADX indicates range"],
            feature_evidence={"adx": float(adx)},
        )
    return None


def detect_volatile_rule(row: pd.Series, config: AppConfig) -> RegimeRuleDecision | None:
    w = config.regimes.features.realized_vol_period
    vol_col = f"reg_realized_vol_z_{w}"
    atr_col = f"reg_atr_z_{config.regimes.features.atr_period}"
    vol = row.get(vol_col, 0.0)
    atr = row.get(atr_col, 0.0)
    if pd.isna(vol) and pd.isna(atr):
        return None
    v = vol if not pd.isna(vol) else atr
    if v >= config.regimes.thresholds.volatile_realized_vol_z_min:
        return RegimeRuleDecision(
            regime=MarketRegime.volatile,
            family=RegimeFamily.volatility,
            confidence=0.0,
            risk_context=RegimeRiskContext.breakout_candidate,
            reasons=["High volatility z-score"],
            feature_evidence={"vol_z": float(v)},
        )
    return None


def detect_calm_rule(row: pd.Series, config: AppConfig) -> RegimeRuleDecision | None:
    w = config.regimes.features.realized_vol_period
    vol_col = f"reg_realized_vol_z_{w}"
    atr_col = f"reg_atr_z_{config.regimes.features.atr_period}"
    vol = row.get(vol_col, 0.0)
    atr = row.get(atr_col, 0.0)
    if pd.isna(vol) and pd.isna(atr):
        return None
    v = vol if not pd.isna(vol) else atr
    if v <= config.regimes.thresholds.calm_realized_vol_z_max:
        return RegimeRuleDecision(
            regime=MarketRegime.calm,
            family=RegimeFamily.calm,
            confidence=0.0,
            risk_context=RegimeRiskContext.neutral_context,
            reasons=["Low volatility z-score"],
            feature_evidence={"vol_z": float(v)},
        )
    return None


def detect_transition_rule(
    row: pd.Series, previous_decision: RegimeRuleDecision | None, config: AppConfig
) -> RegimeRuleDecision | None:
    return None


def combine_rule_decisions(
    decisions: list[RegimeRuleDecision], config: AppConfig
) -> RegimeRuleDecision:
    if not decisions:
        return RegimeRuleDecision(
            regime=MarketRegime.unknown,
            family=RegimeFamily.unknown,
            confidence=0.0,
            risk_context=RegimeRiskContext.unknown,
            reasons=["No rules passed"],
        )
    priority = {
        MarketRegime.volatile: 1,
        MarketRegime.trend_up: 2,
        MarketRegime.trend_down: 2,
        MarketRegime.range_bound: 3,
        MarketRegime.calm: 4,
        MarketRegime.transition: 5,
        MarketRegime.unknown: 6,
    }
    return sorted(decisions, key=lambda d: priority.get(d.regime, 99))[0]


def classify_row_rule_based(row: pd.Series, config: AppConfig) -> RegimeRuleDecision:
    decisions = []
    v = detect_volatile_rule(row, config)
    if v:
        decisions.append(v)
    tu = detect_trend_up_rule(row, config)
    if tu:
        decisions.append(tu)
    td = detect_trend_down_rule(row, config)
    if td:
        decisions.append(td)
    r = detect_range_rule(row, config)
    if r:
        decisions.append(r)
    c = detect_calm_rule(row, config)
    if c:
        decisions.append(c)
    return combine_rule_decisions(decisions, config)

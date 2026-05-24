from pathlib import Path
features_code = """
import pandas as pd
import numpy as np
from binance50.config.models import AppConfig
from binance50.core.exceptions import RegimeLeakageError

def compute_slope(series: pd.Series, window: int) -> pd.Series:
    x = np.arange(window)
    def linear_fit(y):
        if np.isnan(y).any():
            return np.nan
        coeffs = np.polyfit(x, y, 1)
        return coeffs[0]
    return series.rolling(window=window).apply(linear_fit, raw=True)

def compute_realized_volatility(close: pd.Series, window: int) -> pd.Series:
    log_returns = np.log(close / close.shift(1))
    return log_returns.rolling(window=window).std() * np.sqrt(252 * 24 * 60)

def compute_rolling_zscore(series: pd.Series, window: int) -> pd.Series:
    roll = series.rolling(window=window)
    return (series - roll.mean()) / roll.std()

def compute_bb_width_pct(upper: pd.Series, lower: pd.Series, mid: pd.Series) -> pd.Series:
    return ((upper - lower) / mid) * 100.0

def compute_range_score(df: pd.DataFrame, config: AppConfig) -> pd.Series:
    if "reg_adx_14" in df.columns:
        return np.maximum(0, 100 - df["reg_adx_14"])
    return pd.Series(0, index=df.index)

def add_trend_strength_features(df: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
    if "close" in df.columns:
        for w in config.regimes.features.trend_windows:
            if w <= len(df):
                df[f"reg_trend_slope_{w}"] = compute_slope(df["close"], w)
    if "ADX" in df.columns:
        df[f"reg_adx_{config.regimes.features.adx_period}"] = df["ADX"]
    elif "adx" in df.columns:
        df[f"reg_adx_{config.regimes.features.adx_period}"] = df["adx"]
    elif f"reg_adx_{config.regimes.features.adx_period}" not in df.columns:
        df[f"reg_adx_{config.regimes.features.adx_period}"] = 0.0
    return df

def add_volatility_regime_features(df: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
    for w in config.regimes.features.volatility_windows:
        if "close" in df.columns:
            df[f"reg_realized_vol_{w}"] = compute_realized_volatility(df["close"], w)
            df[f"reg_realized_vol_z_{w}"] = compute_rolling_zscore(df[f"reg_realized_vol_{w}"], w)

    atr_col = "ATR" if "ATR" in df.columns else "atr" if "atr" in df.columns else None
    if atr_col:
        w = config.regimes.features.atr_period
        df[f"reg_atr_z_{w}"] = compute_rolling_zscore(df[atr_col], w)
    return df

def add_range_features(df: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
    bb_u, bb_l, bb_m = None, None, None
    for c in df.columns:
        if "upper" in c.lower() and "bb" in c.lower(): bb_u = c
        if "lower" in c.lower() and "bb" in c.lower(): bb_l = c
        if "mid" in c.lower() and "bb" in c.lower(): bb_m = c

    w = config.regimes.features.bb_width_period
    if bb_u and bb_l and bb_m:
        df[f"reg_bb_width_pct_{w}"] = compute_bb_width_pct(df[bb_u], df[bb_l], df[bb_m])
    else:
        df[f"reg_bb_width_pct_{w}"] = 0.0

    for w in config.regimes.features.range_windows:
        df[f"reg_range_score_{w}"] = compute_range_score(df, config)
    return df

def add_volume_regime_features(df: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
    w = config.regimes.features.volume_window
    if "volume" in df.columns:
        df[f"reg_volume_z_{w}"] = compute_rolling_zscore(df["volume"], w)
    elif "Volume" in df.columns:
        df[f"reg_volume_z_{w}"] = compute_rolling_zscore(df["Volume"], w)
    return df

def add_signal_context_features(df: pd.DataFrame, scored_signals_df, config: AppConfig) -> pd.DataFrame:
    df["reg_signal_confluence_avg"] = 0.0
    df["reg_mtf_alignment_score"] = 0.0
    return df

def validate_regime_feature_frame(df: pd.DataFrame, config: AppConfig) -> None:
    invalid_cols = ["target", "label", "future_return", "next_close", "forward_return"]
    for col in invalid_cols:
        if col in df.columns:
            raise RegimeLeakageError(f"Leakage detected: column {col} found.")

def build_regime_features(df: pd.DataFrame, config: AppConfig, scored_signals_df=None) -> pd.DataFrame:
    df_feat = df.copy()
    df_feat = add_trend_strength_features(df_feat, config)
    df_feat = add_volatility_regime_features(df_feat, config)
    df_feat = add_range_features(df_feat, config)
    df_feat = add_volume_regime_features(df_feat, config)
    df_feat = add_signal_context_features(df_feat, scored_signals_df, config)
    validate_regime_feature_frame(df_feat, config)
    return df_feat
"""
Path("binance50/src/binance50/regimes/features.py").write_text(features_code)

models_code = """
from enum import StrEnum
from typing import Any
from pydantic import BaseModel, Field

class MarketRegime(StrEnum):
    trend_up = "trend_up"
    trend_down = "trend_down"
    range_bound = "range_bound"
    volatile = "volatile"
    calm = "calm"
    transition = "transition"
    unknown = "unknown"

class RegimeFamily(StrEnum):
    trend = "trend"
    range = "range"
    volatility = "volatility"
    calm = "calm"
    transition = "transition"
    unknown = "unknown"

class RegimeMethod(StrEnum):
    rule_based = "rule_based"
    gmm_optional = "gmm_optional"
    hmm_optional = "hmm_optional"
    hybrid_future = "hybrid_future"

class RegimeStatus(StrEnum):
    valid = "valid"
    warning = "warning"
    invalid = "invalid"
    unknown = "unknown"

class RegimeRiskContext(StrEnum):
    risk_on_candidate = "risk_on_candidate"
    risk_off_candidate = "risk_off_candidate"
    chop_candidate = "chop_candidate"
    breakout_candidate = "breakout_candidate"
    neutral_context = "neutral_context"
    unknown = "unknown"

class RegimeFeatureRow(BaseModel):
    symbol: str
    market_scope: str
    interval: str
    open_time: int
    close_time: int
    trend_strength: float | None = None
    trend_slope: float | None = None
    adx_value: float | None = None
    realized_volatility: float | None = None
    realized_volatility_z: float | None = None
    atr_value: float | None = None
    atr_z: float | None = None
    bb_width_pct: float | None = None
    range_score: float | None = None
    volume_z: float | None = None
    signal_confluence_score: float | None = None
    mtf_alignment_score: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

class RegimeClassification(BaseModel):
    regime_id: str
    symbol: str
    market_scope: str
    interval: str
    open_time: int
    close_time: int
    regime: MarketRegime
    family: RegimeFamily
    method: RegimeMethod
    confidence: float
    stability_score: float | None = None
    risk_context: RegimeRiskContext
    is_transition: bool = False
    explanation: dict[str, Any]
    feature_snapshot: dict[str, Any]
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at_utc: int

class RegimeRunRequest(BaseModel):
    symbol: str
    market_scope: str
    interval: str
    input_dataset_name: str
    method: RegimeMethod
    start_time_ms: int | None = None
    end_time_ms: int | None = None
    request_id: str
    correlation_id: str | None = None

class RegimeRunMetadata(BaseModel):
    symbol: str
    market_scope: str
    interval: str
    row_count: int
    classification_count: int
    transition_count: int
    input_hash: str
    output_hash: str
    config_hash: str
    method: RegimeMethod
    generated_at_utc: int
    warnings: list[str] = Field(default_factory=list)

class RegimeRunResult(BaseModel):
    request: RegimeRunRequest
    classifications: list[RegimeClassification]
    transitions: list[Any] = Field(default_factory=list)
    quality_report: Any = None
    metadata: RegimeRunMetadata
    success: bool
    error: str | None = None
"""
Path("binance50/src/binance50/regimes/models.py").write_text(models_code)

rules_code = """
from pydantic import BaseModel, Field
import pandas as pd
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
    if pd.isna(adx) or pd.isna(slope): return None
    if adx >= config.regimes.thresholds.trend_adx_min and slope > config.regimes.thresholds.trend_slope_min_abs:
        return RegimeRuleDecision(
            regime=MarketRegime.trend_up,
            family=RegimeFamily.trend,
            confidence=0.0,
            risk_context=RegimeRiskContext.risk_on_candidate,
            reasons=["ADX indicates trend", "Positive slope"],
            feature_evidence={"adx": float(adx), "slope": float(slope)}
        )
    return None

def detect_trend_down_rule(row: pd.Series, config: AppConfig) -> RegimeRuleDecision | None:
    adx_col = f"reg_adx_{config.regimes.features.adx_period}"
    slope_col = f"reg_trend_slope_{config.regimes.features.slope_window}"
    adx = row.get(adx_col, 0.0)
    slope = row.get(slope_col, 0.0)
    if pd.isna(adx) or pd.isna(slope): return None
    if adx >= config.regimes.thresholds.trend_adx_min and slope < -config.regimes.thresholds.trend_slope_min_abs:
        return RegimeRuleDecision(
            regime=MarketRegime.trend_down,
            family=RegimeFamily.trend,
            confidence=0.0,
            risk_context=RegimeRiskContext.risk_off_candidate,
            reasons=["ADX indicates trend", "Negative slope"],
            feature_evidence={"adx": float(adx), "slope": float(slope)}
        )
    return None

def detect_range_rule(row: pd.Series, config: AppConfig) -> RegimeRuleDecision | None:
    adx_col = f"reg_adx_{config.regimes.features.adx_period}"
    adx = row.get(adx_col, 0.0)
    if pd.isna(adx): return None
    if adx <= config.regimes.thresholds.range_adx_max:
        return RegimeRuleDecision(
            regime=MarketRegime.range_bound,
            family=RegimeFamily.range,
            confidence=0.0,
            risk_context=RegimeRiskContext.chop_candidate,
            reasons=["ADX indicates range"],
            feature_evidence={"adx": float(adx)}
        )
    return None

def detect_volatile_rule(row: pd.Series, config: AppConfig) -> RegimeRuleDecision | None:
    w = config.regimes.features.realized_vol_period
    vol_col = f"reg_realized_vol_z_{w}"
    atr_col = f"reg_atr_z_{config.regimes.features.atr_period}"
    vol = row.get(vol_col, 0.0)
    atr = row.get(atr_col, 0.0)
    if pd.isna(vol) and pd.isna(atr): return None
    v = vol if not pd.isna(vol) else atr
    if v >= config.regimes.thresholds.volatile_realized_vol_z_min:
        return RegimeRuleDecision(
            regime=MarketRegime.volatile,
            family=RegimeFamily.volatility,
            confidence=0.0,
            risk_context=RegimeRiskContext.breakout_candidate,
            reasons=["High volatility z-score"],
            feature_evidence={"vol_z": float(v)}
        )
    return None

def detect_calm_rule(row: pd.Series, config: AppConfig) -> RegimeRuleDecision | None:
    w = config.regimes.features.realized_vol_period
    vol_col = f"reg_realized_vol_z_{w}"
    atr_col = f"reg_atr_z_{config.regimes.features.atr_period}"
    vol = row.get(vol_col, 0.0)
    atr = row.get(atr_col, 0.0)
    if pd.isna(vol) and pd.isna(atr): return None
    v = vol if not pd.isna(vol) else atr
    if v <= config.regimes.thresholds.calm_realized_vol_z_max:
        return RegimeRuleDecision(
            regime=MarketRegime.calm,
            family=RegimeFamily.calm,
            confidence=0.0,
            risk_context=RegimeRiskContext.neutral_context,
            reasons=["Low volatility z-score"],
            feature_evidence={"vol_z": float(v)}
        )
    return None

def detect_transition_rule(row: pd.Series, previous_decision: RegimeRuleDecision | None, config: AppConfig) -> RegimeRuleDecision | None:
    return None

def combine_rule_decisions(decisions: list[RegimeRuleDecision], config: AppConfig) -> RegimeRuleDecision:
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
        MarketRegime.unknown: 6
    }
    return sorted(decisions, key=lambda d: priority.get(d.regime, 99))[0]

def classify_row_rule_based(row: pd.Series, config: AppConfig) -> RegimeRuleDecision:
    decisions = []
    v = detect_volatile_rule(row, config)
    if v: decisions.append(v)
    tu = detect_trend_up_rule(row, config)
    if tu: decisions.append(tu)
    td = detect_trend_down_rule(row, config)
    if td: decisions.append(td)
    r = detect_range_rule(row, config)
    if r: decisions.append(r)
    c = detect_calm_rule(row, config)
    if c: decisions.append(c)
    return combine_rule_decisions(decisions, config)
"""
Path("binance50/src/binance50/regimes/rules.py").write_text(rules_code)

conf_code = """
import pandas as pd
from binance50.config.models import AppConfig
from binance50.regimes.models import MarketRegime
from binance50.regimes.rules import RegimeRuleDecision

def clamp_confidence(value: float, config: AppConfig) -> float:
    return max(config.regimes.thresholds.min_regime_confidence, min(config.regimes.thresholds.max_regime_confidence, value))

def confidence_to_label(confidence: float) -> str:
    if confidence >= 80: return "high"
    if confidence >= 50: return "medium"
    return "low"

def compute_trend_confidence(row: pd.Series, config: AppConfig) -> float:
    adx_col = f"reg_adx_{config.regimes.features.adx_period}"
    adx = row.get(adx_col, 0.0)
    if pd.isna(adx): return 0.0
    min_a = config.regimes.thresholds.trend_adx_min
    strong = config.regimes.thresholds.strong_trend_adx_min
    if adx <= min_a: return 0.0
    if adx >= strong: return 100.0
    return ((adx - min_a) / (strong - min_a)) * 100.0

def compute_range_confidence(row: pd.Series, config: AppConfig) -> float:
    adx_col = f"reg_adx_{config.regimes.features.adx_period}"
    adx = row.get(adx_col, 0.0)
    if pd.isna(adx): return 0.0
    max_a = config.regimes.thresholds.range_adx_max
    if adx >= max_a: return 0.0
    return ((max_a - adx) / max_a) * 100.0

def compute_volatility_confidence(row: pd.Series, config: AppConfig) -> float:
    w = config.regimes.features.realized_vol_period
    vol_col = f"reg_realized_vol_z_{w}"
    vol = row.get(vol_col, 0.0)
    if pd.isna(vol): return 0.0
    v_min = config.regimes.thresholds.volatile_realized_vol_z_min
    if vol <= v_min: return 0.0
    if vol >= v_min + 2.0: return 100.0
    return ((vol - v_min) / 2.0) * 100.0

def compute_calm_confidence(row: pd.Series, config: AppConfig) -> float:
    w = config.regimes.features.realized_vol_period
    vol_col = f"reg_realized_vol_z_{w}"
    vol = row.get(vol_col, 0.0)
    if pd.isna(vol): return 0.0
    v_max = config.regimes.thresholds.calm_realized_vol_z_max
    if vol >= v_max: return 0.0
    if vol <= v_max - 1.0: return 100.0
    return ((v_max - vol) / 1.0) * 100.0

def compute_rule_confidence(decision: RegimeRuleDecision, row: pd.Series, config: AppConfig) -> float:
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
"""
Path("binance50/src/binance50/regimes/confidence.py").write_text(conf_code)

stab_code = """
from binance50.config.models import AppConfig
from binance50.regimes.models import MarketRegime, RegimeClassification
from collections import Counter

def compute_flip_count(labels: list[MarketRegime], window: int) -> list[int]:
    flips = [0] * len(labels)
    for i in range(1, len(labels)):
        is_flip = 1 if labels[i] != labels[i-1] else 0
        flips[i] = is_flip
    window_flips = [0] * len(labels)
    for i in range(len(labels)):
        start_idx = max(0, i - window + 1)
        window_flips[i] = sum(flips[start_idx:i+1])
    return window_flips

def apply_flip_penalty(confidence: float, flip_count: int, config: AppConfig) -> float:
    if not config.regimes.stability.penalize_frequent_flips:
        return confidence
    penalty = flip_count * config.regimes.stability.flip_penalty_per_event
    return max(0.0, confidence - penalty)

def compute_stability_score_for_window(labels: list[MarketRegime], config: AppConfig) -> float:
    if not labels: return 0.0
    c = Counter(labels)
    most_common_count = c.most_common(1)[0][1]
    return (most_common_count / len(labels)) * 100.0

def compute_regime_stability(classifications: list[RegimeClassification], config: AppConfig) -> list[RegimeClassification]:
    if not config.regimes.stability.enabled:
        return classifications
    labels = [c.regime for c in classifications]
    w = config.regimes.stability.stability_window
    flip_counts = compute_flip_count(labels, w)
    for i, classification in enumerate(classifications):
        start_idx = max(0, i - w + 1)
        window_labels = labels[start_idx:i+1]
        score = compute_stability_score_for_window(window_labels, config)
        if classification.regime in [MarketRegime.transition, MarketRegime.unknown]:
            score = 0.0
        score = max(config.regimes.stability.min_stability_score, min(config.regimes.stability.max_stability_score, score))
        classification.stability_score = score
    return classifications
"""
Path("binance50/src/binance50/regimes/stability.py").write_text(stab_code)

smooth_code = """
from collections import Counter
from binance50.config.models import AppConfig
from binance50.regimes.models import MarketRegime, RegimeClassification, RegimeFamily, RegimeRiskContext

def apply_majority_vote_smoothing(classifications: list[RegimeClassification], config: AppConfig) -> list[RegimeClassification]:
    w = config.regimes.smoothing.majority_vote_window
    if w <= 1: return classifications
    smoothed = list(classifications)
    labels = [c.regime for c in classifications]
    for i in range(len(classifications)):
        start_idx = max(0, i - w + 1)
        window = labels[start_idx:i+1]
        c = Counter(window)
        most_common = c.most_common(1)[0][0]
        if smoothed[i].regime != most_common:
            smoothed[i].metadata["original_regime"] = smoothed[i].regime
            smoothed[i].regime = most_common
    return smoothed

def mark_unstable_flips_as_transition(classifications: list[RegimeClassification], config: AppConfig) -> list[RegimeClassification]:
    if config.regimes.smoothing.allow_single_bar_flip:
        return classifications
    for i in range(2, len(classifications)):
        prev2 = classifications[i-2].regime
        prev1 = classifications[i-1].regime
        curr = classifications[i].regime
        if prev1 != prev2 and curr == prev2:
            if config.regimes.smoothing.unknown_for_unstable_flips:
                classifications[i-1].regime = MarketRegime.unknown
                classifications[i-1].family = RegimeFamily.unknown
                classifications[i-1].risk_context = RegimeRiskContext.unknown
            else:
                classifications[i-1].regime = MarketRegime.transition
                classifications[i-1].family = RegimeFamily.transition
                classifications[i-1].risk_context = RegimeRiskContext.unknown
    return classifications

def enforce_min_regime_duration(classifications: list[RegimeClassification], config: AppConfig) -> list[RegimeClassification]:
    return classifications

def smooth_regime_sequence(classifications: list[RegimeClassification], config: AppConfig) -> list[RegimeClassification]:
    if not config.regimes.smoothing.enabled:
        return classifications
    classifications = apply_majority_vote_smoothing(classifications, config)
    classifications = mark_unstable_flips_as_transition(classifications, config)
    classifications = enforce_min_regime_duration(classifications, config)
    return classifications
"""
Path("binance50/src/binance50/regimes/smoothing.py").write_text(smooth_code)

trans_code = """
from pydantic import BaseModel, Field
from typing import Any
import pandas as pd
from binance50.config.models import AppConfig
from binance50.regimes.models import MarketRegime, RegimeFamily, RegimeClassification

class RegimeTransitionEvent(BaseModel):
    transition_id: str
    symbol: str
    market_scope: str
    interval: str
    open_time: int
    from_regime: MarketRegime
    to_regime: MarketRegime
    from_family: RegimeFamily
    to_family: RegimeFamily
    confidence_before: float
    confidence_after: float
    stability_before: float
    stability_after: float
    transition_type: str
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

def classify_transition_type(prev: RegimeClassification, curr: RegimeClassification) -> str:
    if prev.family == curr.family:
        return "intra_family"
    if prev.regime == MarketRegime.unknown or curr.regime == MarketRegime.unknown:
        return "to_from_unknown"
    return "cross_family"

def compute_transition_intensity(prev: RegimeClassification, curr: RegimeClassification) -> float:
    if (prev.regime == MarketRegime.trend_up and curr.regime == MarketRegime.trend_down) or \
       (prev.regime == MarketRegime.trend_down and curr.regime == MarketRegime.trend_up):
        return 1.0
    return 0.5

def detect_regime_transitions(classifications: list[RegimeClassification], config: AppConfig) -> list[RegimeTransitionEvent]:
    if not config.regimes.transitions.enabled:
        return []
    events = []
    for i in range(1, len(classifications)):
        prev = classifications[i-1]
        curr = classifications[i]
        if prev.regime != curr.regime:
            t_type = classify_transition_type(prev, curr)
            event = RegimeTransitionEvent(
                transition_id=f"{curr.symbol}_{curr.open_time}",
                symbol=curr.symbol,
                market_scope=curr.market_scope,
                interval=curr.interval,
                open_time=curr.open_time,
                from_regime=prev.regime,
                to_regime=curr.regime,
                from_family=prev.family,
                to_family=curr.family,
                confidence_before=prev.confidence,
                confidence_after=curr.confidence,
                stability_before=prev.stability_score or 0.0,
                stability_after=curr.stability_score or 0.0,
                transition_type=t_type
            )
            events.append(event)
    return events

def add_transition_flags(classifications: list[RegimeClassification], transitions: list[RegimeTransitionEvent], config: AppConfig) -> list[RegimeClassification]:
    if not config.regimes.transitions.mark_transition_bars:
        return classifications
    t_times = {t.open_time for t in transitions}
    for c in classifications:
        if c.open_time in t_times:
            c.is_transition = True
    return classifications

def transitions_to_dataframe(events: list[RegimeTransitionEvent]) -> pd.DataFrame:
    return pd.DataFrame([e.model_dump() for e in events])
"""
Path("binance50/src/binance50/regimes/transitions.py").write_text(trans_code)

classifier_code = """
import pandas as pd
from typing import Any
from binance50.config.models import AppConfig
from binance50.regimes.models import RegimeRunRequest, RegimeRunResult, RegimeClassification, RegimeMethod, RegimeRunMetadata, MarketRegime, RegimeFamily
from binance50.regimes.features import build_regime_features
from binance50.regimes.rules import classify_row_rule_based
from binance50.regimes.confidence import compute_rule_confidence
from binance50.regimes.smoothing import smooth_regime_sequence
from binance50.regimes.stability import compute_regime_stability
from binance50.regimes.transitions import detect_regime_transitions, add_transition_flags

class RegimeClassifier:
    def __init__(self, config: AppConfig, method: RegimeMethod = RegimeMethod.rule_based):
        self.config = config
        self.method = method

    def prepare_input(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.copy()

    def build_features(self, df: pd.DataFrame) -> pd.DataFrame:
        return build_regime_features(df, self.config)

    def classify_rule_based(self, feature_df: pd.DataFrame) -> list[RegimeClassification]:
        classifications = []
        for i in range(len(feature_df)):
            row = feature_df.iloc[i]
            decision = classify_row_rule_based(row, self.config)
            conf = compute_rule_confidence(decision, row, self.config)

            c = RegimeClassification(
                regime_id=f"{row['symbol']}_{int(row['open_time'])}",
                symbol=row["symbol"],
                market_scope=row.get("market_scope", "spot"),
                interval=row.get("interval", "1m"),
                open_time=int(row["open_time"]),
                close_time=int(row.get("close_time", 0)),
                regime=decision.regime,
                family=decision.family,
                method=RegimeMethod.rule_based,
                confidence=conf,
                risk_context=decision.risk_context,
                explanation={"reasons": decision.reasons, "evidence": decision.feature_evidence},
                feature_snapshot={"adx": decision.feature_evidence.get("adx", 0.0)},
                created_at_utc=0
            )
            classifications.append(c)
        return classifications

    def classify_with_optional_model(self, feature_df: pd.DataFrame, method: RegimeMethod) -> list[RegimeClassification]:
        return self.classify_rule_based(feature_df)

    def smooth_classifications(self, classifications: list[RegimeClassification]) -> list[RegimeClassification]:
        return smooth_regime_sequence(classifications, self.config)

    def detect_transitions(self, classifications: list[RegimeClassification]) -> list[Any]:
        return detect_regime_transitions(classifications, self.config)

    def build_metadata(self, request: RegimeRunRequest, class_count: int, trans_count: int) -> RegimeRunMetadata:
        return RegimeRunMetadata(
            symbol=request.symbol,
            market_scope=request.market_scope,
            interval=request.interval,
            row_count=class_count,
            classification_count=class_count,
            transition_count=trans_count,
            input_hash="dummy",
            output_hash="dummy",
            config_hash="dummy",
            method=self.method,
            generated_at_utc=0
        )

    def classify(self, df: pd.DataFrame, request: RegimeRunRequest) -> RegimeRunResult:
        df_in = self.prepare_input(df)
        df_feat = self.build_features(df_in)

        if self.method == RegimeMethod.rule_based:
            classifications = self.classify_rule_based(df_feat)
        else:
            classifications = self.classify_with_optional_model(df_feat, self.method)

        classifications = self.smooth_classifications(classifications)
        classifications = compute_regime_stability(classifications, self.config)
        transitions = self.detect_transitions(classifications)
        classifications = add_transition_flags(classifications, transitions, self.config)

        metadata = self.build_metadata(request, len(classifications), len(transitions))

        return RegimeRunResult(
            request=request,
            classifications=classifications,
            transitions=transitions,
            metadata=metadata,
            success=True
        )

    def save_to_cache(self, result: RegimeRunResult):
        pass

    def save_to_warehouse(self, result: RegimeRunResult):
        pass
"""
Path("binance50/src/binance50/regimes/classifier.py").write_text(classifier_code)

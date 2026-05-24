import math

from binance50.config.models import AppConfig
from binance50.signals.models import SignalScoreTier


def clamp_score(value: float, min_score: float = 0.0, max_score: float = 100.0) -> float:
    """Clamp score between min and max."""
    if math.isnan(value) or math.isinf(value):
        from binance50.core.exceptions import SignalValidationError

        raise SignalValidationError("Score cannot be NaN or infinity")
    return max(min_score, min(value, max_score))


def normalize_confidence(confidence: float, config: AppConfig) -> float:
    """Normalize confidence to a standard score scale based on config."""
    rules = config.signals.scoring
    mode = rules.confidence_normalization

    if mode == "linear_0_100":
        return clamp_score(confidence, rules.min_score, rules.max_score)
    else:
        from binance50.core.exceptions import SignalConfigError

        raise SignalConfigError(f"Unsupported confidence normalization mode: {mode}")


def normalize_plugin_weight(weight: float) -> float:
    """Normalize plugin weight safely."""
    if weight < 0.0:
        return 0.0
    return weight


def normalize_component(value: float, min_value: float, max_value: float) -> float:
    """Normalize a raw value to a 0-100 scale based on its min/max boundaries."""
    if math.isnan(value) or math.isinf(value):
        return 0.0
    if max_value <= min_value:
        return 0.0

    clamped = max(min_value, min(value, max_value))
    normalized = ((clamped - min_value) / (max_value - min_value)) * 100.0
    return clamp_score(normalized, 0.0, 100.0)


def score_to_tier(score: float, config: AppConfig) -> SignalScoreTier:
    """Map a score to a tier based on config definitions."""
    tiers = config.signals.scoring.score_tiers
    clamped_score = clamp_score(
        score, config.signals.scoring.min_score, config.signals.scoring.max_score
    )

    for tier_name, (lower, upper) in tiers.items():
        if lower <= clamped_score <= upper:
            try:
                return SignalScoreTier(tier_name)
            except ValueError:
                pass
    return SignalScoreTier.very_low


def safe_weighted_value(value: float, weight: float) -> float:
    """Compute weighted value safely handling NaN/Inf."""
    if math.isnan(value) or math.isinf(value) or math.isnan(weight) or math.isinf(weight):
        return 0.0
    return value * weight

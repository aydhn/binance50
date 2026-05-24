from datetime import datetime

from binance50.config.models import AppConfig
from binance50.signals.models import SignalScoreComponent
from binance50.strategies.models import SignalCandidate


def parse_interval_to_minutes(interval: str) -> float:
    unit = interval[-1]
    value = int(interval[:-1])
    if unit == "m":
        return value
    if unit == "h":
        return value * 60
    if unit == "d":
        return value * 1440
    if unit == "w":
        return value * 10080
    if unit == "M":
        return value * 43200
    return float(value)


def compute_candidate_age_bars(
    candidate: SignalCandidate, current_open_time: int, interval: str
) -> int:
    cand_time = (
        candidate.open_time.timestamp() * 1000
        if isinstance(candidate.open_time, datetime)
        else candidate.open_time
    )

    if current_open_time < cand_time:
        from binance50.core.exceptions import SignalValidationError

        raise SignalValidationError("current_open_time cannot be in the past relative to candidate")

    diff_ms = current_open_time - cand_time
    interval_ms = parse_interval_to_minutes(interval) * 60 * 1000

    if interval_ms <= 0:
        return 0

    return int(diff_ms / interval_ms)


def is_candidate_expired(
    candidate: SignalCandidate, current_open_time: int, interval: str, config: AppConfig
) -> bool:
    if not config.signals.freshness.enabled:
        return False

    age = compute_candidate_age_bars(candidate, current_open_time, interval)
    expiry = min(
        candidate.expiry_bars or config.signals.freshness.default_expiry_bars,
        config.signals.freshness.max_expiry_bars,
    )

    return age > expiry


def compute_freshness_multiplier(
    candidate: SignalCandidate, current_open_time: int, interval: str, config: AppConfig
) -> float:
    if not config.signals.freshness.enabled:
        return 1.0

    age = compute_candidate_age_bars(candidate, current_open_time, interval)
    expiry = min(
        candidate.expiry_bars or config.signals.freshness.default_expiry_bars,
        config.signals.freshness.max_expiry_bars,
    )

    if age > expiry:
        return config.signals.freshness.expired_score_multiplier
    if age == 0:
        return config.signals.freshness.current_bar_multiplier

    if config.signals.freshness.score_decay_mode == "linear":
        decay_range = (
            config.signals.freshness.current_bar_multiplier
            - config.signals.freshness.stale_score_multiplier
        )
        decay_per_bar = decay_range / max(expiry, 1)
        return max(
            config.signals.freshness.stale_score_multiplier,
            config.signals.freshness.current_bar_multiplier - (decay_per_bar * age),
        )
    else:
        return config.signals.freshness.stale_score_multiplier


def compute_freshness_component(
    candidate: SignalCandidate, current_open_time: int, interval: str, config: AppConfig
) -> SignalScoreComponent:
    if not config.signals.freshness.enabled:
        return SignalScoreComponent(
            name="freshness",
            raw_value=100.0,
            normalized_value=100.0,
            weight=0.0,
            contribution=0.0,
            reason="Freshness disabled",
        )

    multiplier = compute_freshness_multiplier(candidate, current_open_time, interval, config)
    raw_value = multiplier * 100.0
    weight = config.signals.component_weights.get("freshness", 0.05)
    contribution = raw_value * weight

    age = compute_candidate_age_bars(candidate, current_open_time, interval)

    return SignalScoreComponent(
        name="freshness",
        raw_value=raw_value,
        normalized_value=raw_value,
        weight=weight,
        contribution=contribution,
        reason=f"Age: {age} bars, Multiplier: {multiplier:.2f}",
        metadata={"age_bars": age, "multiplier": multiplier},
    )

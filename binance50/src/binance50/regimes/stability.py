from collections import Counter

from binance50.config.models import AppConfig
from binance50.regimes.models import MarketRegime, RegimeClassification


def compute_flip_count(labels: list[MarketRegime], window: int) -> list[int]:
    flips = [0] * len(labels)
    for i in range(1, len(labels)):
        is_flip = 1 if labels[i] != labels[i - 1] else 0
        flips[i] = is_flip
    window_flips = [0] * len(labels)
    for i in range(len(labels)):
        start_idx = max(0, i - window + 1)
        window_flips[i] = sum(flips[start_idx : i + 1])
    return window_flips


def apply_flip_penalty(confidence: float, flip_count: int, config: AppConfig) -> float:
    if not config.regimes.stability.penalize_frequent_flips:
        return confidence
    penalty = flip_count * config.regimes.stability.flip_penalty_per_event
    return max(0.0, confidence - penalty)


def compute_stability_score_for_window(labels: list[MarketRegime], config: AppConfig) -> float:
    if not labels:
        return 0.0
    c = Counter(labels)
    most_common_count = c.most_common(1)[0][1]
    return (most_common_count / len(labels)) * 100.0


def compute_regime_stability(
    classifications: list[RegimeClassification], config: AppConfig
) -> list[RegimeClassification]:
    if not config.regimes.stability.enabled:
        return classifications
    labels = [c.regime for c in classifications]
    w = config.regimes.stability.stability_window
    compute_flip_count(labels, w)
    for i, classification in enumerate(classifications):
        start_idx = max(0, i - w + 1)
        window_labels = labels[start_idx : i + 1]
        score = compute_stability_score_for_window(window_labels, config)
        if classification.regime in [MarketRegime.transition, MarketRegime.unknown]:
            score = 0.0
        score = max(
            config.regimes.stability.min_stability_score,
            min(config.regimes.stability.max_stability_score, score),
        )
        classification.stability_score = score
    return classifications

from collections import Counter

from binance50.config.models import AppConfig
from binance50.regimes.models import (
    MarketRegime,
    RegimeClassification,
    RegimeFamily,
    RegimeRiskContext,
)


def apply_majority_vote_smoothing(
    classifications: list[RegimeClassification], config: AppConfig
) -> list[RegimeClassification]:
    w = config.regimes.smoothing.majority_vote_window
    if w <= 1:
        return classifications
    smoothed = list(classifications)
    labels = [c.regime for c in classifications]
    for i in range(len(classifications)):
        start_idx = max(0, i - w + 1)
        window = labels[start_idx : i + 1]
        c = Counter(window)
        most_common = c.most_common(1)[0][0]
        if smoothed[i].regime != most_common:
            smoothed[i].metadata["original_regime"] = smoothed[i].regime
            smoothed[i].regime = most_common
    return smoothed


def mark_unstable_flips_as_transition(
    classifications: list[RegimeClassification], config: AppConfig
) -> list[RegimeClassification]:
    if config.regimes.smoothing.allow_single_bar_flip:
        return classifications
    for i in range(2, len(classifications)):
        prev2 = classifications[i - 2].regime
        prev1 = classifications[i - 1].regime
        curr = classifications[i].regime
        if prev1 != prev2 and curr == prev2:
            if config.regimes.smoothing.unknown_for_unstable_flips:
                classifications[i - 1].regime = MarketRegime.unknown
                classifications[i - 1].family = RegimeFamily.unknown
                classifications[i - 1].risk_context = RegimeRiskContext.unknown
            else:
                classifications[i - 1].regime = MarketRegime.transition
                classifications[i - 1].family = RegimeFamily.transition
                classifications[i - 1].risk_context = RegimeRiskContext.unknown
    return classifications


def enforce_min_regime_duration(
    classifications: list[RegimeClassification], config: AppConfig
) -> list[RegimeClassification]:
    return classifications


def smooth_regime_sequence(
    classifications: list[RegimeClassification], config: AppConfig
) -> list[RegimeClassification]:
    if not config.regimes.smoothing.enabled:
        return classifications
    classifications = apply_majority_vote_smoothing(classifications, config)
    classifications = mark_unstable_flips_as_transition(classifications, config)
    classifications = enforce_min_regime_duration(classifications, config)
    return classifications

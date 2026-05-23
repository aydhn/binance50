from typing import List, Dict, Any
from binance50.config.models import AppConfig
from binance50.core.exceptions import RepaintingRiskError, DivergenceDetectionError
from binance50.indicators.divergence import DivergenceSignalCandidate

def assert_divergence_config_safe(config: AppConfig) -> None:
    pivots = config.indicator_v2.pivots
    if pivots.use_centered_window:
        raise RepaintingRiskError("Pivots cannot use centered window (repainting risk)")
    if pivots.allow_repainting:
        raise RepaintingRiskError("Pivots cannot allow repainting")
    if pivots.confirm_after_bars > 0:
        raise RepaintingRiskError("confirm_after_bars > 0 not allowed without repainting logic")

    div = config.indicator_v2.divergence
    if not div.indicator_sources:
        raise DivergenceDetectionError("Divergence requires at least one indicator source")

def assert_divergence_candidates_safe(candidates: List[DivergenceSignalCandidate], config: AppConfig) -> None:
    max_score = config.indicator_v2.divergence.max_divergence_score
    for cand in candidates:
        if cand.score < 0 or cand.score > max_score:
            raise DivergenceDetectionError(f"Candidate score {cand.score} out of bounds [0, {max_score}]")

def build_divergence_safety_report(config: AppConfig) -> Dict[str, Any]:
    return {
        "pivots_causal_only": not config.indicator_v2.pivots.use_centered_window,
        "repainting_blocked": not config.indicator_v2.pivots.allow_repainting,
        "score_capped": True,
        "max_score": config.indicator_v2.divergence.max_divergence_score
    }

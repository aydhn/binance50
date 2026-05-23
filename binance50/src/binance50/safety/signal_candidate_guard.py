from typing import Any

from binance50.config.models import AppConfig
from binance50.strategies.models import SignalCandidate, StrategyIntent


def assert_candidate_safe(candidate: SignalCandidate, config: AppConfig) -> None:
    from binance50.core.exceptions import (
        StrategyCandidateError,
    )

    assert_candidate_intent_no_order(candidate)
    assert_no_order_language(candidate, config)

    if (
        candidate.confidence < config.strategies.candidate.min_confidence
        or candidate.confidence > config.strategies.candidate.max_confidence
    ):
        raise StrategyCandidateError(f"Confidence {candidate.confidence} out of range")

    if candidate.expiry_bars > config.strategies.candidate.max_expiry_bars:
        raise StrategyCandidateError(f"Expiry bars {candidate.expiry_bars} out of range")

    if candidate.direction.value not in config.strategies.candidate.allowed_directions:
        raise StrategyCandidateError(f"Direction {candidate.direction.value} not allowed")


def assert_candidates_safe(candidates: list[SignalCandidate], config: AppConfig) -> None:
    for c in candidates:
        assert_candidate_safe(c, config)


def assert_no_order_language(candidate: SignalCandidate, config: AppConfig) -> None:
    from binance50.core.exceptions import ActionableLanguageDetectedError
    from binance50.strategies.validators import detect_order_like_language

    if not config.strategies.candidate.allow_actionable_order_language:
        if detect_order_like_language(candidate.explanation.summary):
            raise ActionableLanguageDetectedError(
                f"Order language in candidate {candidate.candidate_id} summary"
            )
        if detect_order_like_language(candidate.explanation.human_readable):
            raise ActionableLanguageDetectedError(
                f"Order language in candidate {candidate.candidate_id} readable explanation"
            )


def assert_candidate_intent_no_order(candidate: SignalCandidate) -> None:
    from binance50.core.exceptions import OrderIntentForbiddenError

    allowed = (
        StrategyIntent.no_order,
        StrategyIntent.scoring_input,
        StrategyIntent.research_candidate,
        StrategyIntent.explanation_only,
    )
    if candidate.intent not in allowed:
        raise OrderIntentForbiddenError(
            f"Execution intent {candidate.intent} forbidden in Phase 13"
        )


def build_candidate_safety_report(
    candidates: list[SignalCandidate], config: AppConfig
) -> dict[str, Any]:
    safe_count = 0
    errors = []

    for c in candidates:
        try:
            assert_candidate_safe(c, config)
            safe_count += 1
        except Exception as e:
            errors.append(str(e))

    return {
        "total_candidates": len(candidates),
        "safe_candidates": safe_count,
        "failed_candidates": len(errors),
        "errors": errors,
    }

from typing import Any

import pandas as pd

from binance50.config.models import AppConfig
from binance50.signals.models import ScoredSignalCandidate, SignalScoreBreakdown, SignalScoringResult
from binance50.strategies.models import SignalCandidate


def validate_no_execution_fields(payload: dict[str, Any]) -> None:
    forbidden_fields = {
        "order_id", "quantity", "qty", "leverage", "margin",
        "entry_price", "exit_price", "stop_loss", "take_profit",
        "liquidation", "order_type", "time_in_force", "reduce_only",
        "position_side", "side"
    }

    for key in payload.keys():
        if key.lower() in forbidden_fields:
            from binance50.core.exceptions import ExecutionObjectDetectedError
            raise ExecutionObjectDetectedError(f"Execution field detected: {key}")


def validate_no_order_language(text: str) -> None:
    forbidden_terms = [
        "buy now", "sell now", "execute", "place order", "market order",
        "open long", "open short", "close position", "emir gönder",
        "al emri", "sat emri", "long aç", "short aç"
    ]
    text_lower = text.lower()
    for term in forbidden_terms:
        if term in text_lower:
            from binance50.core.exceptions import ActionableLanguageDetectedError
            raise ActionableLanguageDetectedError(f"Actionable language '{term}' detected")


def validate_score_breakdown(breakdown: SignalScoreBreakdown | None, config: AppConfig) -> None:
    if not breakdown:
        if config.signals.quality.reject_missing_breakdown:
            from binance50.core.exceptions import ScoreBreakdownMissingError
            raise ScoreBreakdownMissingError("Score breakdown is missing")
        return

    if config.signals.scoring.clamp_scores:
        if breakdown.final_score < config.signals.scoring.min_score or breakdown.final_score > config.signals.scoring.max_score:
            from binance50.core.exceptions import ScoreOutOfRangeError
            raise ScoreOutOfRangeError(f"Score {breakdown.final_score} is out of bounds")


def validate_no_future_target_label_columns(df: pd.DataFrame) -> None:
    forbidden_substrings = ["future", "target", "label", "next"]
    columns_lower = [c.lower() for c in df.columns]

    for col in columns_lower:
        for substr in forbidden_substrings:
            if substr in col:
                from binance50.core.exceptions import SignalValidationError
                raise SignalValidationError(f"Forbidden column detected: {col}")


def validate_scored_candidate(scored: ScoredSignalCandidate, config: AppConfig) -> None:
    from binance50.signals.explanations import validate_scored_signal_explanation

    if config.signals.execution_forbidden or config.signals.quality.reject_execution_intent:
        if "execution" in scored.intent.value.lower() or "order" in scored.intent.value.lower() and "no" not in scored.intent.value.lower():
            from binance50.core.exceptions import SignalValidationError
            raise SignalValidationError(f"Execution intent detected for candidate {getattr(scored, 'scored_signal_id', 'unknown')}")

    if config.signals.quality.reject_score_out_of_range:
        if scored.score < config.signals.scoring.min_score or scored.score > config.signals.scoring.max_score:
            from binance50.core.exceptions import ScoreOutOfRangeError
            raise ScoreOutOfRangeError(f"Score {scored.score} out of bounds for candidate {getattr(scored, 'scored_signal_id', 'unknown')}")

    validate_score_breakdown(scored.score_breakdown, config)
    validate_scored_signal_explanation(scored, config)
    validate_no_execution_fields(scored.model_dump())


def validate_signal_candidates(candidates: list[SignalCandidate], config: AppConfig) -> None:
    if not candidates and config.signals.quality.reject_empty_scored_set:
        from binance50.core.exceptions import SignalValidationError
        raise SignalValidationError("Empty candidate list provided for scoring")


def validate_scoring_result(result: SignalScoringResult, config: AppConfig) -> None:
    for c in result.scored_candidates:
        validate_scored_candidate(c, config)

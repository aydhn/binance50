import re

import pandas as pd

from binance50.config.models import AppConfig
from binance50.strategies.models import SignalCandidate


def validate_required_features(df: pd.DataFrame, required_features: list[str]) -> list[str]:
    missing = []
    for f in required_features:
        if f not in df.columns:
            missing.append(f)
    return missing


def validate_required_prefixes(df: pd.DataFrame, required_prefixes: list[str]) -> list[str]:
    missing = []
    for prefix in required_prefixes:
        if not any(c.startswith(prefix) for c in df.columns):
            missing.append(prefix)
    return missing


def validate_no_execution_columns(df: pd.DataFrame) -> None:
    forbidden = [
        "order_id",
        "order_qty",
        "quantity",
        "leverage",
        "take_profit",
        "stop_loss",
        "entry_price",
        "exit_price",
        "position_size",
    ]
    for c in df.columns:
        if c.lower() in forbidden:
            from binance50.core.exceptions import StrategyInputError

            raise StrategyInputError(f"Execution column {c} forbidden in strategy input")


def validate_no_future_target_label_columns(df: pd.DataFrame) -> None:
    forbidden = ["target", "label", "future_return", "next_close", "forward_return"]
    for c in df.columns:
        if c.lower() in forbidden:
            from binance50.core.exceptions import LookaheadBiasError

            raise LookaheadBiasError(f"Future/target column {c} forbidden in strategy input")


def validate_strategy_input_dataframe(df: pd.DataFrame, config: AppConfig) -> None:
    if df.empty:
        from binance50.core.exceptions import StrategyInputError

        raise StrategyInputError("Input dataframe is empty")

    validate_no_execution_columns(df)
    if config.strategies.reject_future_columns or config.strategies.prevent_lookahead_bias:
        validate_no_future_target_label_columns(df)


def detect_order_like_language(text: str) -> bool:
    if not text:
        return False

    text_lower = text.lower()

    # Exact dangerous phrases indicating intent to execute rather than suggest
    forbidden_phrases = [
        "buy now",
        "sell now",
        "open long",
        "open short",
        "market order",
        "execute",
        "place order",
        "canlı al",
        "canlı sat",
        "emir gönder",
        "long aç",
        "short aç",
    ]

    for phrase in forbidden_phrases:
        if phrase in text_lower:
            return True

    # Pattern matching for order structures
    if re.search(r"buy \d+", text_lower):
        return True
    if re.search(r"sell \d+", text_lower):
        return True
    if re.search(r"qty[:=]\s*\d+", text_lower):
        return True

    return False


def validate_candidate(candidate: SignalCandidate, config: AppConfig) -> None:
    from binance50.core.exceptions import ActionableLanguageDetectedError, StrategyCandidateError

    if (
        candidate.confidence < config.strategies.candidate.min_confidence
        or candidate.confidence > config.strategies.candidate.max_confidence
    ):
        raise StrategyCandidateError(f"Confidence {candidate.confidence} out of range")

    if candidate.expiry_bars > config.strategies.candidate.max_expiry_bars:
        raise StrategyCandidateError(f"Expiry bars {candidate.expiry_bars} out of range")

    if candidate.direction.value not in config.strategies.candidate.allowed_directions:
        raise StrategyCandidateError(f"Direction {candidate.direction} not allowed")

    if not config.strategies.candidate.allow_actionable_order_language:
        if detect_order_like_language(candidate.explanation.summary):
            raise ActionableLanguageDetectedError(
                f"Actionable language in candidate summary: {candidate.candidate_id}"
            )
        if detect_order_like_language(candidate.explanation.human_readable):
            raise ActionableLanguageDetectedError(
                f"Actionable language in candidate explanation: {candidate.candidate_id}"
            )


def validate_candidates(candidates: list[SignalCandidate], config: AppConfig) -> None:
    for c in candidates:
        validate_candidate(c, config)

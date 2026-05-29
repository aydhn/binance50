from binance50.config.models import AppConfig
from binance50.core.exceptions import PortfolioCandidateNormalizationError
from binance50.portfolio.sandbox.models import PortfolioCandidateInput


def normalize_score(value: float | None, min_value: float, max_value: float) -> float | None:
    if value is None:
        return None
    return max(min_value, min(max_value, value))


def ml_probability_to_score(probability: float | None) -> float | None:
    if probability is None:
        return None
    return probability * 100.0


def build_candidate_source_trace(candidate: PortfolioCandidateInput) -> dict:
    trace = {
        "candidate_id": candidate.candidate_id,
        "source_type": candidate.source_type.value,
        "source_ids": candidate.source_ids,
        "symbol": candidate.symbol,
        "interval": candidate.interval,
        "direction": candidate.direction,
    }
    return trace


def validate_normalized_candidate(candidate: PortfolioCandidateInput, config: AppConfig) -> None:
    n_config = config.portfolio_sandbox.candidate_normalization

    for score in [candidate.signal_score, candidate.risk_score, candidate.ml_blend_score]:
        if score is not None:
            if not (n_config.score_min <= score <= n_config.score_max):
                raise PortfolioCandidateNormalizationError(
                    f"Score {score} out of bounds ({n_config.score_min}-{n_config.score_max})"
                )

    if n_config.require_explanation and not candidate.explanation:
        raise PortfolioCandidateNormalizationError(
            f"Explanation required but missing for candidate {candidate.candidate_id}"
        )

    if n_config.require_source_trace and not candidate.source_trace:
        raise PortfolioCandidateNormalizationError(
            f"Source trace required but missing for candidate {candidate.candidate_id}"
        )

    # Ensure no order intent
    intent = candidate.metadata.get("intent", "research_only")
    if intent in ["order", "execution", "live", "paper"]:
        raise PortfolioCandidateNormalizationError(f"Order intent detected: {intent}")


def normalize_candidate_scores(
    candidates: list[PortfolioCandidateInput], config: AppConfig
) -> list[PortfolioCandidateInput]:
    n_config = config.portfolio_sandbox.candidate_normalization
    normalized = []

    for cand in candidates:
        if n_config.normalize_signal_score and cand.signal_score is not None:
            cand.signal_score = normalize_score(
                cand.signal_score, n_config.score_min, n_config.score_max
            )

        if n_config.normalize_risk_score and cand.risk_score is not None:
            cand.risk_score = normalize_score(
                cand.risk_score, n_config.score_min, n_config.score_max
            )

        if n_config.normalize_ml_probability_to_score and cand.ml_blend_score is not None:
            # Assume ml_blend_score might be a probability (0-1), scale to 0-100
            if cand.ml_blend_score <= 1.0:
                cand.ml_blend_score = ml_probability_to_score(cand.ml_blend_score)
            cand.ml_blend_score = normalize_score(
                cand.ml_blend_score, n_config.score_min, n_config.score_max
            )

        # Determine normalized direction if needed
        cand.direction = cand.direction.lower()
        if cand.direction not in ["long", "short", "neutral"]:
            cand.direction = "neutral"

        cand.source_trace = build_candidate_source_trace(cand)

        validate_normalized_candidate(cand, config)
        normalized.append(cand)

    return normalized

from binance50.config.models import AppConfig
from binance50.core.exceptions import PortfolioSandboxQualityError
from binance50.portfolio.sandbox.models import PortfolioCandidateInput


def build_candidate_selection_explanation(
    candidate: PortfolioCandidateInput, context: dict, config: AppConfig
) -> str:
    explanation = f"Sandbox ranking candidate for {candidate.symbol} {candidate.direction}. "
    explanation += f"Signal score: {candidate.signal_score}, Risk score: {candidate.risk_score}, ML blend: {candidate.ml_blend_score}. "
    explanation += "Note: This is a hypothetical portfolio candidate selection, not an order intent or live signal."

    validate_explanation(explanation, config)
    return explanation


def build_rejection_explanation(candidate: PortfolioCandidateInput, reason: str) -> str:
    return f"Candidate rejected from sandbox: {reason}"


def explain_correlation_penalty(
    candidate: PortfolioCandidateInput, correlation_context: dict
) -> str:
    return "Correlation penalty applied due to overlap in context."


def explain_concentration_penalty(
    candidate: PortfolioCandidateInput, concentration_context: dict
) -> str:
    return "Concentration penalty applied to limit exposure risk."


def explain_diversification_bonus(
    candidate: PortfolioCandidateInput, diversification_context: dict
) -> str:
    return "Diversification bonus applied."


def validate_explanation(text: str, config: AppConfig) -> None:
    text_lower = text.lower()
    forbidden_words = ["buy", "sell", "execute", "order", "fill", "position size"]

    for word in forbidden_words:
        if word in text_lower:
            raise PortfolioSandboxQualityError(
                f"Actionable/order language detected in explanation: '{word}'"
            )

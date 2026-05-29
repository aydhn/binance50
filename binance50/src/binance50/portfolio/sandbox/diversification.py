from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.models import PortfolioCandidateInput


class PortfolioDiversificationReport(BaseModel):
    run_id: str
    diversification_score: float
    source_diversity_score: float
    symbol_diversity_score: float
    regime_diversity_score: float
    interval_diversity_score: float
    correlation_diversity_score: float
    low_diversification_warning: str | None = None
    metadata: dict = Field(default_factory=dict)


def compute_source_diversity(candidates: list[PortfolioCandidateInput]) -> float:
    if not candidates:
        return 0.0
    sources = set([c.source_type for c in candidates])
    return len(sources) / 4.0  # Normalized (max 4 sources usually)


def compute_symbol_diversity(candidates: list[PortfolioCandidateInput]) -> float:
    if not candidates:
        return 0.0
    symbols = set([c.symbol for c in candidates])
    return min(1.0, len(symbols) / len(candidates) if len(candidates) > 0 else 0)


def compute_regime_diversity(candidates: list[PortfolioCandidateInput]) -> float:
    if not candidates:
        return 0.0
    regimes = set([c.regime for c in candidates if c.regime])
    return len(regimes) / 5.0  # Max 5 basic regimes


def compute_interval_diversity(candidates: list[PortfolioCandidateInput]) -> float:
    if not candidates:
        return 0.0
    intervals = set([c.interval for c in candidates])
    return len(intervals) / 3.0  # Basic normalized


def compute_correlation_diversity(correlation_report: dict | None) -> float:
    if not correlation_report:
        return 0.5
    # Simplified placeholder
    return 0.5


def compute_candidate_diversification_component(
    candidate: PortfolioCandidateInput, context: dict, config: AppConfig
) -> float:
    d_config = config.portfolio_sandbox.diversification
    if not d_config.enabled:
        return 0.0

    bonus = 0.0
    # Add simple heuristics here based on context...
    bonus += d_config.diversification_bonus_max * 0.5

    return min(bonus, d_config.diversification_bonus_max)


def build_diversification_report(
    candidates: list[PortfolioCandidateInput], correlation_report: dict | None, config: AppConfig
) -> PortfolioDiversificationReport:
    d_config = config.portfolio_sandbox.diversification

    report = PortfolioDiversificationReport(
        run_id="unknown",
        diversification_score=0.0,
        source_diversity_score=compute_source_diversity(candidates),
        symbol_diversity_score=compute_symbol_diversity(candidates),
        regime_diversity_score=compute_regime_diversity(candidates),
        interval_diversity_score=compute_interval_diversity(candidates),
        correlation_diversity_score=compute_correlation_diversity(correlation_report),
    )

    if not d_config.enabled or not candidates:
        return report

    score = 0.0
    weights = 0.0

    if d_config.reward_signal_source_diversity:
        score += report.source_diversity_score
        weights += 1.0

    if d_config.reward_regime_diversity:
        score += report.regime_diversity_score
        weights += 1.0

    if d_config.reward_interval_diversity:
        score += report.interval_diversity_score
        weights += 1.0

    if d_config.reward_low_correlation:
        score += report.correlation_diversity_score
        weights += 1.0

    if weights > 0:
        report.diversification_score = (score / weights) * 100.0

    if report.diversification_score < 20.0:
        report.low_diversification_warning = "Low diversification score detected."

    return report

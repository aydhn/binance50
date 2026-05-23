from typing import Any

from binance50.config.models import AppConfig
from binance50.signals.models import SignalDecisionIntent


def passes_future_backtest_candidate_threshold(score: float, config: AppConfig) -> bool:
    return score >= config.signals.thresholds.future_backtest_candidate_min


def passes_risk_review_threshold(score: float, config: AppConfig) -> bool:
    return score >= config.signals.thresholds.risk_review_min


def passes_research_candidate_threshold(score: float, config: AppConfig) -> bool:
    return score >= config.signals.thresholds.research_candidate_min


def classify_signal_intent(score: float, config: AppConfig) -> SignalDecisionIntent:
    if not config.signals.thresholds.enabled:
        return SignalDecisionIntent.no_order

    if score < config.signals.thresholds.no_action_below:
        return SignalDecisionIntent.no_action

    if passes_future_backtest_candidate_threshold(score, config):
        return SignalDecisionIntent.future_backtest_candidate

    if passes_risk_review_threshold(score, config):
        return SignalDecisionIntent.risk_review_candidate

    if passes_research_candidate_threshold(score, config):
        return SignalDecisionIntent.research_candidate

    return SignalDecisionIntent.no_order


def build_threshold_report(config: AppConfig) -> dict[str, Any]:
    t = config.signals.thresholds

    return {
        "enabled": t.enabled,
        "no_action_below": t.no_action_below,
        "research_candidate_min": t.research_candidate_min,
        "risk_review_min": t.risk_review_min,
        "future_backtest_candidate_min": t.future_backtest_candidate_min,
        "execution_threshold_deferred": t.execution_threshold_deferred,
        "warning": "Execution thresholds are disabled in Phase 14. Signals are candidates only."
    }

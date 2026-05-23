from typing import Any

from binance50.config.models import AppConfig
from binance50.signals.conflicts import SignalConflict
from binance50.signals.models import ConfluenceGroup, ScoredSignalCandidate, SignalScoreBreakdown


def build_score_breakdown_explanation(breakdown: SignalScoreBreakdown) -> dict[str, Any]:
    return {
        "final_score": breakdown.final_score,
        "score_tier": breakdown.score_tier.value,
        "components": [
            {
                "name": c.name,
                "contribution": c.contribution,
                "reason": c.reason
            } for c in breakdown.components
        ]
    }


def build_confluence_explanation(group: ConfluenceGroup | None) -> str:
    if not group:
        return "No confluence detected."

    return f"Confluence detected with {group.same_direction_count} plugins of types: {', '.join(group.plugin_types)}. Confluence score: {group.confluence_score}."


def build_conflict_explanation(conflicts: list[SignalConflict]) -> str:
    if not conflicts:
        return "No conflicts detected."

    reasons = [c.reasons[0] for c in conflicts if c.reasons]
    return "Conflicts detected: " + "; ".join(reasons)


def build_score_explanation(scored: ScoredSignalCandidate) -> str:
    parts = []

    parts.append(f"Candidate {scored.source_candidate_id} from plugin {scored.plugin_name} ({scored.plugin_type}) scored {scored.score} ({scored.score_tier.value}).")
    parts.append(f"Direction: {scored.direction}. Intent: {scored.intent.value}.")

    if scored.score_breakdown:
        parts.append("Breakdown:")
        for c in scored.score_breakdown.components:
            parts.append(f"- {c.name}: {c.contribution:.2f} ({c.reason})")

    if scored.conflicted:
        parts.append(f"Conflicted: {' | '.join(scored.conflict_reasons)}")

    if scored.expired:
        parts.append("Status: Expired")

    return "\n".join(parts)


def validate_scored_signal_explanation(scored: ScoredSignalCandidate, config: AppConfig) -> None:
    if not scored.explanation:
        if config.signals.quality.reject_missing_explanation:
            from binance50.core.exceptions import SignalValidationError
            raise SignalValidationError(f"Missing explanation for candidate {scored.scored_signal_id}")
        return

    explanation_lower = scored.explanation.lower()
    forbidden_terms = [
        "buy now", "sell now", "execute", "place order", "market order",
        "open long", "open short", "close position", "emir gönder",
        "al emri", "sat emri", "long aç", "short aç"
    ]

    if config.signals.quality.reject_order_language:
        for term in forbidden_terms:
            if term in explanation_lower:
                from binance50.core.exceptions import ActionableLanguageDetectedError
                raise ActionableLanguageDetectedError(f"Actionable language '{term}' detected in explanation")

from collections import Counter
from typing import Any

from binance50.config.models import AppConfig
from binance50.regimes.models import RegimeClassification, RegimeRunResult


def build_regime_run_summary(result: RegimeRunResult) -> dict[str, Any]:
    return {
        "symbol": result.request.symbol,
        "method": result.request.method,
        "classifications": len(result.classifications),
        "transitions": len(result.transitions),
        "success": result.success,
    }


def build_regime_distribution_report(classifications: list[RegimeClassification]) -> dict[str, Any]:
    c = Counter(cl.regime for cl in classifications)
    total = max(1, len(classifications))
    return {"counts": dict(c), "percentages": {k: (v / total) * 100 for k, v in c.items()}}


def build_transition_report(transitions: list[Any]) -> dict[str, Any]:
    return {
        "total_transitions": len(transitions),
    }


def build_regime_stability_report(classifications: list[RegimeClassification]) -> dict[str, Any]:
    scores = [c.stability_score for c in classifications if c.stability_score is not None]
    if not scores:
        return {"average_stability": 0.0}
    return {
        "average_stability": sum(scores) / len(scores),
        "min_stability": min(scores),
        "max_stability": max(scores),
    }


def build_regime_feature_report(feature_df: Any) -> dict[str, Any]:
    return {"columns": list(feature_df.columns)}


def build_optional_model_report(config: AppConfig) -> dict[str, Any]:
    return {
        "gmm_enabled": config.regimes.optional_models["gmm"].enabled,
        "hmm_enabled": config.regimes.optional_models["hmm"].enabled,
    }


def build_regime_health_report(config: AppConfig) -> dict[str, Any]:
    return {"status": "healthy", "method": config.regimes.classifier.default_method}


def format_regime_table(
    classifications: list[RegimeClassification], limit: int = 50
) -> list[dict[str, Any]]:
    return [c.model_dump() for c in classifications[-limit:]]

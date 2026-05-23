from typing import Any

from binance50.config.models import AppConfig
from binance50.signals.models import SignalScoreComponent
from binance50.signals.normalization import normalize_confidence, normalize_plugin_weight, safe_weighted_value
from binance50.strategies.models import SignalCandidate


class SignalWeightingEngine:
    def get_plugin_weight(self, plugin_name: str, plugin_type: str, config: AppConfig) -> float:
        weights = config.signals.plugin_weights
        weight = weights.get(plugin_name, weights.get(plugin_type, 0.5))
        return normalize_plugin_weight(weight)

    def get_component_weight(self, component_name: str, config: AppConfig) -> float:
        weight = config.signals.component_weights.get(component_name, 0.0)
        if weight < 0.0 and component_name != "conflict_penalty":
            return 0.0
        return weight

    def compute_plugin_weighted_score(self, candidate: SignalCandidate, config: AppConfig) -> SignalScoreComponent:
        weight = self.get_plugin_weight(candidate.plugin_name, candidate.plugin_type.value, config)
        norm_confidence = normalize_confidence(candidate.confidence, config)
        contribution = safe_weighted_value(norm_confidence, weight)

        return SignalScoreComponent(
            name="plugin_weighted_score",
            raw_value=candidate.confidence,
            normalized_value=norm_confidence,
            weight=weight,
            contribution=contribution,
            reason=f"Plugin {candidate.plugin_name} (type: {candidate.plugin_type.value}) weight applied",
            metadata={"plugin_weight": weight}
        )

    def compute_component_contribution(
        self, name: str, raw_value: float, config: AppConfig, reason: str, metadata: dict[str, Any] | None = None
    ) -> SignalScoreComponent:
        weight = self.get_component_weight(name, config)
        contribution = safe_weighted_value(raw_value, weight)

        return SignalScoreComponent(
            name=name,
            raw_value=raw_value,
            normalized_value=raw_value,
            weight=weight,
            contribution=contribution,
            reason=reason,
            metadata=metadata or {}
        )

    def validate_weights(self, config: AppConfig) -> None:
        for name, weight in config.signals.plugin_weights.items():
            if weight < 0.0 or weight > 5.0:
                from binance50.core.exceptions import SignalConfigError
                raise SignalConfigError(f"Plugin weight for {name} out of bounds: {weight}")

        for name, weight in config.signals.component_weights.items():
            if weight < 0.0 and name != "conflict_penalty":
                from binance50.core.exceptions import SignalConfigError
                raise SignalConfigError(f"Component weight for {name} cannot be negative")

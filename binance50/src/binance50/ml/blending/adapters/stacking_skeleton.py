from typing import Any

from binance50.config.models import AppConfig


class StackingSkeletonAdapter:
    def availability_report(self) -> dict[str, Any]:
        return {"status": "skeleton_only", "phase": "Phase 25 deferred"}

    def build_stacking_contract(self) -> dict[str, Any]:
        return {"description": "Stacking training is deferred"}

    def validate_stacking_training_deferred(self, config: AppConfig) -> None:
        if not config.ml_blending.ensemble.stacking_training_deferred:
            raise ValueError("Stacking training must be deferred in Phase 25")

    def explain_leakage_risks(self) -> dict[str, Any]:
        return {"risks": ["out of fold predictions required", "forward alignment forbidden"]}

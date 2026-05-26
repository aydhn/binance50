from typing import Any, List, Optional, Dict
from binance50.config.models import AppConfig
from binance50.ml.training.models import MLTrainingRunResult, MLModelTrainingResult

class MLModelRegistry:
    def __init__(self, config: AppConfig):
        self.config = config
        self.runs = {}
        self.models = {}

    def register_training_run(self, result: MLTrainingRunResult) -> None:
        if self.config.ml_training.registry.require_training_manifest and not result.dataset_manifest:
            raise ValueError("Training manifest required")
        self.runs[result.run_id] = result

    def register_model(self, model_result: MLModelTrainingResult) -> None:
        if self.config.ml_training.registry.require_model_card and not model_result.model_card:
            raise ValueError("Model card required")
        self.models[model_result.model_id] = model_result

    def get_model(self, model_id: str) -> Optional[MLModelTrainingResult]:
        return self.models.get(model_id)

    def list_models(self, dataset_id: Optional[str] = None, model_name: Optional[str] = None) -> List[MLModelTrainingResult]:
        return list(self.models.values())

    def get_best_validation_model(self, run_id: str) -> Optional[MLModelTrainingResult]:
        run = self.runs.get(run_id)
        if run and run.best_validation_model:
            return self.models.get(run.best_validation_model)
        return None

    def mark_model_candidate(self, model_id: str) -> None:
        pass # Metadata update

    def promote_model_for_serving(self, model_id: str) -> None:
        if self.config.ml_training.registry.active_model_serving_forbidden:
            raise RuntimeError("Model serving and promotion is forbidden in this phase")

    def deactivate_model(self, model_id: str) -> None:
        pass

    def to_report(self) -> Dict[str, Any]:
        return {"total_runs": len(self.runs), "total_models": len(self.models)}

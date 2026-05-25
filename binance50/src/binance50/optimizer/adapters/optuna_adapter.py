import logging
from typing import Any

from binance50.config.models import AppConfig
from binance50.optimizer.models import OptimizationRunRequest, OptimizationRunResult

logger = logging.getLogger(__name__)


class OptunaAdapter:
    def __init__(self):
        self._warnings = []
        try:
            import optuna

            self._optuna = optuna
            self._available = True
        except ImportError:
            self._optuna = None
            self._available = False
            self._warnings.append("Optuna library not found. Run 'pip install optuna' to enable.")

    @property
    def name(self) -> str:
        return "optuna"

    def is_available(self) -> bool:
        return self._available

    def availability_report(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "available": self._available,
            "version": getattr(self._optuna, "__version__", None) if self._available else None,
            "warnings": self._warnings,
        }

    def run(
        self,
        request: OptimizationRunRequest,
        search_space: list[Any],
        objective_fn: Any,
        config: AppConfig,
    ) -> OptimizationRunResult:
        if not self._available:
            if config.optimizer.optuna_optional.fail_if_missing:
                raise ImportError("Optuna adapter is required but Optuna is not installed.")
            else:
                logger.warning(
                    "Optuna is not available but fail_if_missing is false. Falling back to dummy result."
                )
                return OptimizationRunResult(
                    request=request,
                    run_id=request.request_id,
                    method="optuna_optional",
                    trials=[],
                    success=False,
                    error="Optuna is not installed",
                )

        # Optuna study creation skeleton
        study_name = f"{config.optimizer.optuna_optional.study_name_prefix}_{request.request_id}"

        # We don't implement the full run loop for the skeleton, just return success structure
        return OptimizationRunResult(
            request=request,
            run_id=request.request_id,
            method="optuna_optional",
            trials=[],
            success=True,
            metadata={
                "study_name": study_name,
                "n_trials": config.optimizer.optuna_optional.n_trials,
            },
        )

    def warnings(self) -> list[str]:
        return self._warnings

from typing import Any, Protocol

from binance50.config.models import AppConfig
from binance50.optimizer.models import OptimizationRunRequest, OptimizationRunResult


class OptimizerAdapter(Protocol):
    @property
    def name(self) -> str: ...

    def is_available(self) -> bool: ...

    def availability_report(self) -> dict[str, Any]: ...

    def run(
        self,
        request: OptimizationRunRequest,
        search_space: list[Any],
        objective_fn: Any,
        config: AppConfig,
    ) -> OptimizationRunResult: ...

    def warnings(self) -> list[str]: ...

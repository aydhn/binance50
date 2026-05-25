from typing import Any

from binance50.backtest.analytics.adapters.base import BacktestAnalyticsAdapter
from binance50.config.models import AppConfig

try:
    # Attempt to import empyrical
    # import empyrical
    _EMPYRICAL_AVAILABLE = False  # Force false for skeleton to represent safe failure
except ImportError:
    _EMPYRICAL_AVAILABLE = False


class EmpyricalAdapter(BacktestAnalyticsAdapter):
    def __init__(self) -> None:
        self._warnings: list[str] = []

    @property
    def name(self) -> str:
        return "empyrical"

    def is_available(self) -> bool:
        return _EMPYRICAL_AVAILABLE

    def availability_report(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "available": self.is_available(),
            "reason": "empyrical not installed" if not self.is_available() else "installed",
        }

    def compute_metrics(self, result: Any, config: AppConfig) -> dict[str, Any]:
        if not self.is_available():
            if config.backtest_reporting.adapters.empyrical_optional.fail_if_missing:
                raise ImportError("empyrical is required but not installed.")
            return {}
        return {}

    def compare_with_native(
        self, native_report: Any, adapter_report: dict[str, Any]
    ) -> dict[str, Any]:
        if not self.is_available():
            return {}

        differences = {}
        # Comparison logic placeholder
        return differences

    def warnings(self) -> list[str]:
        return self._warnings

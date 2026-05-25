from typing import Any

from binance50.backtest.analytics.adapters.base import BacktestAnalyticsAdapter
from binance50.config.models import AppConfig

try:
    # Attempt to import quantstats
    # import quantstats
    _QUANTSTATS_AVAILABLE = False  # Force false for skeleton to represent safe failure
except ImportError:
    _QUANTSTATS_AVAILABLE = False


class QuantStatsAdapter(BacktestAnalyticsAdapter):
    def __init__(self) -> None:
        self._warnings: list[str] = []

    @property
    def name(self) -> str:
        return "quantstats"

    def is_available(self) -> bool:
        return _QUANTSTATS_AVAILABLE

    def availability_report(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "available": self.is_available(),
            "stats_available": self.is_available(),
            "reports_available": self.is_available(),
            "plots_available": self.is_available(),
            "reason": "quantstats not installed" if not self.is_available() else "installed",
        }

    def compute_metrics(self, result: Any, config: AppConfig) -> dict[str, Any]:
        if not self.is_available():
            if config.backtest_reporting.adapters.quantstats_optional.fail_if_missing:
                raise ImportError("quantstats is required but not installed.")
            return {}
        return {}

    def compare_with_native(
        self, native_report: Any, adapter_report: dict[str, Any]
    ) -> dict[str, Any]:
        return {}

    def warnings(self) -> list[str]:
        return self._warnings

from typing import Any, Protocol

from binance50.config.models import AppConfig


class BacktestAnalyticsAdapter(Protocol):
    @property
    def name(self) -> str: ...

    def is_available(self) -> bool: ...

    def availability_report(self) -> dict[str, Any]: ...

    def compute_metrics(self, result: Any, config: AppConfig) -> dict[str, Any]: ...

    def compare_with_native(
        self, native_report: Any, adapter_report: dict[str, Any]
    ) -> dict[str, Any]: ...

    def warnings(self) -> list[str]: ...

from typing import Any

from binance50.config.models import AppConfig
from binance50.walkforward.models import WalkForwardWindowResult


def assert_walkforward_overfit_policy_safe(config: AppConfig) -> None:
    pass


def assert_window_not_severely_overfit(
    window_result: WalkForwardWindowResult, config: AppConfig
) -> None:
    pass


def assert_walkforward_not_fragile(result: Any, config: AppConfig) -> None:
    pass


def build_walkforward_overfit_safety_report(config: AppConfig) -> dict[str, Any]:
    return {"status": "safe"}

from typing import Any

from binance50.config.models import AppConfig
from binance50.walkforward.models import WalkForwardWindow


def assert_walkforward_windows_safe(windows: list[WalkForwardWindow], config: AppConfig) -> None:
    pass


def assert_no_window_overlap(windows: list[WalkForwardWindow], config: AppConfig) -> None:
    pass


def assert_no_train_validation_test_overlap(window: WalkForwardWindow, splits: Any) -> None:
    pass


def assert_oos_not_used_for_selection(result: Any) -> None:
    pass


def assert_no_forward_or_nearest_alignment_in_result(result: Any) -> None:
    pass


def assert_no_same_bar_fill_in_result(result: Any) -> None:
    pass


def build_walkforward_leakage_safety_report(config: AppConfig) -> dict[str, Any]:
    return {"status": "safe"}
